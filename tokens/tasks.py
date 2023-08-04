import time
import json
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
    logger.info("mint_token celery task: nft_id: %s" % nft_id)
    creator_address = token.user.wallet_address
    proxy_address = settings.PROXY_ADDRESS
    contract_address = token.contract.contract_address
    logger.info("mint_token celery task: contract_address: %s" % contract_address)
    abi_def = get_contract_abi()
    contract_instance = web3.eth.contract(address=contract_address, abi=abi_def)
    # get nonce from DB
    transaction = Transaction.objects.filter(from_address=settings.PROXY_ADDRESS).order_by('-id').first()

    if transaction is None:
        nonce = web3.eth.get_transaction_count(settings.PROXY_ADDRESS)
    else:
        nonce = transaction.nonce + 1
    logger.info("mint_token celery task: nonce: %s" % nonce)

    # # get gas price
    gas_price = web3.eth.gas_price
    logger.info("mint_token celery task: gas_price: %s" % gas_price)

    amount = token.stock
    txn = contract_instance.functions.mintMultiToken(
        creator_address,
        nft_id,
        amount
    ).buildTransaction({
        'gas': 500000,
        'gasPrice': gas_price,
        'from': proxy_address,
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=settings.PROXY_PRIVATE_KEY)

    # tx = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    # try:
    #     tx_receipt = web3.eth.waitForTransactionReceipt(tx, timeout=120)
    # except Exception as e:
    #     logger.info("mint_token celery task: waitForTransactionReceipt error: %s" % e)
    #     return
    #
    # tx_status = tx_receipt['status']
    # logger.info("mint_token celery task: tx_status: %s" % tx_status)
    # tx_hash = web3.toHex(tx)
    # logger.info("mint_token celery task: tx_hash: %s" % tx_hash)

    token.status = 'MINTED'
    token.save()

