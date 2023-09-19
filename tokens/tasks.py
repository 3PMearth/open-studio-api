from celery import shared_task
from django.conf import settings
from web3 import Web3
from .models import Token
from utils.contract_abi import get_contract_abi
from contracts.models import Transaction
import logging

logger = logging.getLogger(__name__)

@shared_task
def transfer_token(token_id_list, to_address, amount_list):
    """
    transfer token to another address
    params:
        token_id_list: list of token id
        to_address: only one buyer address
        amount_list: list of amount to transfer
    """
    # check the length of token_id_list and amount_list
    if len(token_id_list) != len(amount_list):
        logger.info("transfer_token celery task: token_id_list and amount_list length is not same")
        return
    else:
        tuple_list = zip(token_id_list, amount_list)

    num_reqeust = len(token_id_list)
    logger.info("transfer_token celery task: num_reqeust: %s" % num_reqeust)
    web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    proxy_address = settings.PROXY_ADDRESS
    gas_price = web3.eth.gas_price
    gas_price = int(gas_price * 1.2)

    cnt = 0
    for tokenid_and_amount in tuple_list:
        cnt += 1
        logging.info(" {} / {} transfering token".format(cnt, num_reqeust))
        logging.info("transfer_token celery task: tokenid_and_amount: {}".format(tokenid_and_amount))
        token = Token.objects.get(id=tokenid_and_amount[0])
        if token.status != 'MINTED':
            logger.info("transfer_token celery task: token status is not MINTED")
            return
        # transfer token here
        transaction = Transaction.objects.order_by('-id').first()
        if transaction is None:
            nonce_onchain = web3.eth.get_transaction_count(settings.PROXY_ADDRESS)
            nonce = nonce_onchain
        else:
            nonce_onchain = web3.eth.get_transaction_count(settings.PROXY_ADDRESS)
            nonce_db = transaction.nonce + 1
            logger.info("transfer_token celery task: nonce_onchain: {} nonce_db: {}".format(nonce_onchain, nonce_db))
            # check nonce value in case of missing db transaction data
            nonce = nonce_onchain if nonce_onchain > nonce_db else nonce_db

        logger.info("transfer_token celery task: nonce: {} gas:price : {}".format(nonce, gas_price))
        contract_address = token.contract.contract_address
        abi_def = get_contract_abi()
        contract_instance = web3.eth.contract(address=contract_address, abi=abi_def)
        from_address = token.user.wallet_address
        logging.info("transfer_token celery task: from_address: {} "
                      "to_address : {} "
                      "amount : {}, token_id {}".format(from_address,
                                                        to_address,
                                                        tokenid_and_amount[1],
                                                        tokenid_and_amount[0]
                                                        ))
        data_byte = web3.to_bytes(tokenid_and_amount[1])
        txn = contract_instance.functions.safeTransferFrom(
            from_address,
            to_address,
            tokenid_and_amount[0],
            tokenid_and_amount[1],
            data_byte
        ).build_transaction({
            'gas': 500000,
            'gasPrice': gas_price,
            'from': proxy_address,
            'nonce': nonce
        })
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=settings.PROXY_PRIVATE_KEY)
        tx = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_hash = tx.hex()
        logger.info("mint_token celery task: tx_hash: %s" % tx_hash)
        tx_received = False
        tx_receipt = None

        # save transaction
        transaction = Transaction(contract=token.contract,
                                  tx_hash=tx_hash,
                                  to_address=to_address,
                                  amount=tokenid_and_amount[1],
                                  token=token,
                                  gas_price=float(gas_price/1000000000),
                                  func="safeTransferFrom",
                                  nonce=nonce)
        logger.info("transaction dict : {}".format(transaction.__dict__))
        logger.info("save transaction: %s" % transaction)
        transaction.save()

        try:
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx, timeout=300)
            tx_received = True
        except Exception as e:
            logger.info("mint_token celery task: waitForTransactionReceipt error: %s" % e)
            token.status = 'ERROR'
            token.save()

        if tx_received is False:
            tx_status = 0
            gas_used = 0
        else:
            tx_status = tx_receipt['status']
            gas_used = tx_receipt['gasUsed']

        # update transaction table
        transaction.tx_status = tx_status
        transaction.gas_used = gas_used
        transaction.save()

        if tx_status == 1:
            logger.info("transfer_token celery task: tx_status: %s" % tx_status)
            # reduce stock
            token.stock -= tokenid_and_amount[1]
            token.save()



@shared_task
def mint_token(token_id):
    web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    logger.info("mint_token celery task started: token_id: %s" % token_id)
    token = Token.objects.get(id=token_id)
    if token.status != 'PREPARE':
        logger.info("mint_token celery task: token status is not PREPARE")
        return

    nft_id = token.nft_id
    creator_address = token.user.wallet_address
    logger.info("mint_token celery task: nft_id: {}, creator_address: {}".format(nft_id, creator_address))
    contract_address = token.contract.contract_address
    proxy_address = settings.PROXY_ADDRESS
    logger.info("mint_token celery task: contract_address: %s" % contract_address)
    abi_def = get_contract_abi()
    contract_instance = web3.eth.contract(address=contract_address, abi=abi_def)
    # get nonce from DB
    try:
        transaction = Transaction.objects.order_by('-id').first()
    except Exception as e:
        logger.info("mint_token celery task: Transaction.objects.filter error: %s" % e)
        transaction = None

    transaction = Transaction.objects.order_by('-id').first()
    if transaction is None:
        nonce_onchain = web3.eth.get_transaction_count(settings.PROXY_ADDRESS)
        nonce = nonce_onchain
    else:
        nonce_onchain = web3.eth.get_transaction_count(settings.PROXY_ADDRESS)
        nonce_db = transaction.nonce + 1
        logger.info("transfer_token celery task: nonce_onchain: {} nonce_db: {}".format(nonce_onchain, nonce_db))
        # check nonce value in case of missing db transaction data
        nonce = nonce_onchain if nonce_onchain > nonce_db else nonce_db

    logger.info("mint_token celery task: nonce: %s" % nonce)

    # # get gas price and make it little bit higher
    gas_price = web3.eth.gas_price
    gas_price = int(gas_price * 1.2)
    logger.info("mint_token celery task: gas_price: %s" % gas_price)

    amount = token.stock
    txn = contract_instance.functions.mintMultiToken(
        creator_address,
        nft_id,
        amount
    ).build_transaction({
        'gas': 500000,
        'gasPrice': gas_price,
        'from': proxy_address,
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=settings.PROXY_PRIVATE_KEY)

    tx = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_hash = tx.hex()
    logger.info("mint_token celery task: tx_hash: %s" % tx_hash)
    tx_received = False
    tx_receipt = None
    # save to transaction table
    # save transaction
    transaction = Transaction(contract=token.contract,
                              tx_hash=tx_hash,
                              to_address=creator_address,
                              amount=amount,
                              token=token,
                              gas_price=float(gas_price/1000000000),
                              func="mintMultiToken",
                              nonce=nonce)
    logger.info("transaction dict : {}".format(transaction.__dict__))
    logger.info("save transaction: %s" % transaction)
    transaction.save()

    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx, timeout=300)
        tx_received = True
    except Exception as e:
        logger.info("mint_token celery task: waitForTransactionReceipt error: %s" % e)
        token.status = 'ERROR'
        token.save()

    if tx_received is False:
        tx_status = 0
        gas_used = 0
    else:
        tx_status = tx_receipt['status']
        gas_used = tx_receipt['gasUsed']

    # update transaction table
    transaction.tx_status = tx_status
    transaction.gas_used = gas_used
    transaction.save()

    # check is status is 1, otherwise it is error
    if tx_status != 1:
        token.status = 'ERROR'
        token.save()
        return
    else:
        logger.info("mint_token celery task: tx_status: %s" % tx_status)
        token.status = 'MINTED'
        token.save()
