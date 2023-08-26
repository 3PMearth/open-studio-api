from celery import shared_task
from django.conf import settings
from web3 import Web3
from .models import Token
from utils.contract_abi import get_contract_abi
from contracts.models import Transaction
import logging

logger = logging.getLogger(__name__)

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
    proxy_address = settings.PROXY_ADDRESS
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

    if transaction is None:
        nonce = web3.eth.get_transaction_count(proxy_address)
    else:
        nonce = transaction.nonce + 1
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
    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx, timeout=120)
    except Exception as e:
        logger.info("mint_token celery task: waitForTransactionReceipt error: %s" % e)
        token.status = 'ERROR'
        token.save()
        return

    tx_status = tx_receipt['status']

    # save transaction
    transaction = Transaction(contract=token.contract,
                              tx_hash=tx_hash,
                              to_address=creator_address,
                              amount=amount,
                              token=token,
                              gas_used=tx_receipt['gasUsed'],
                              gas_price=gas_price,
                              func="mintMultiToken",
                              nonce=nonce)
    logger.info("save transaction: %s" % transaction)
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
