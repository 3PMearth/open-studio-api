import datetime
import os
import logging
from web3 import Web3
from django.conf import settings
from uuid import uuid4

logger = logging.getLogger(__name__)


def upload_file_to_s3(instance, filename):
    """
    This function is used to upload files  to s3 bucket
    """
    year = datetime.date.today().year
    f_name, f_ext = os.path.splitext(filename)

    uuid = str(uuid4())[:4]
    return '{}/{}/{}_{}{}'.format(settings.AWS_STORAGE_BASE_FOLDER_NAME,
                                  year,
                                  f_name,
                                  uuid,
                                  f_ext
                                  )



def check_balance_of_token(contract_address, nft_id, user_wallet):
    """
    This function is used to check the balance of a token in a smart contract.

    :param contract_address: The address of the token smart contract.
    :param nft_id: The unique identifier of the NFT.
    :param user_wallet: The user's wallet address.

    :return: A tuple (success, balance) where success is a boolean indicating whether the operation was successful,
             and balance is the balance of the token for the specified user.
    """
    web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    if web3.is_connected() is False:
        return False, "web3 connection error"

    # abi for balanceOf
    abi = [
        {
            'inputs': [
                {'internalType': 'address', 'name': 'account', 'type': 'address'},
                {'internalType': 'uint256', 'name': 'id', 'type': 'uint256'}
            ],
            'name': 'balanceOf',
            'outputs': [
                {'internalType': 'uint256', 'name': '', 'type': 'uint256'}
            ],
            'stateMutability': 'view',
            'type': 'function',
            'constant': True
        }
    ]
    trg_contract_address = web3.to_checksum_address(contract_address)
    contract_instance = web3.eth.contract(address=trg_contract_address, abi=abi)
    user_wallet = web3.to_checksum_address(user_wallet)
    try:
        token_balance = contract_instance.functions.balanceOf(user_wallet, nft_id).call()
    except Exception as e:
        logger.error(e)
        return False, "balanceOf error"

    logging.info("token_balance: {}".format(token_balance))
    return True, token_balance


def validate_t2(nft_id, verifier_id, contract_address, user_wallet, verifier_code, T2):
    """
    This function is used to validate the T2 value.

    :param nft_id: The unique identifier of the NFT.
    :param verifier_id: The unique identifier of the verifier.
    :param contract_address: The address of the token smart contract.
    :param user_wallet: The user's wallet address.
    :param verifier_code: The unique code of the verifier.
    :param T2: The T2 value to validate.

    :return: A tuple (success, message) where success is a boolean indicating whether the operation was successful,
             and message is the message to return to the user.
    """
    secret_shared_token = settings.SECRET_SHARED_TOKEN
    data_to_sign = str(nft_id) + str(verifier_id) + \
                   contract_address.lower() + user_wallet.lower() + secret_shared_token + verifier_code
    hash_obj = Web3.keccak(text=data_to_sign)
    calculated_t2 = hash_obj.hex()
    logger.info("data_to_sign: {}".format(data_to_sign))
    logger.info("calculated_t2: {}".format(calculated_t2))
    if calculated_t2 != T2:
        return False, "invalid T2"
    return True, "success"