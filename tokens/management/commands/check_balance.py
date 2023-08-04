from django.core.management.base import BaseCommand, CommandError
from tokens.tasks import mint_token
from web3 import Web3
from django.conf import settings
from utils.contract_abi import get_contract_abi
from tokens.models import Token

class Command(BaseCommand):
    """
    Manual mint token
    """
    help = "check balance"

    def add_arguments(self, parser):
        parser.add_argument('--wallet_address', type=str)
        parser.add_argument('--token_id', type=int)

    def handle(self, *args, **options):
        target_address = options['wallet_address']
        token_id = options['token_id']
        token = Token.objects.get(id=token_id)
        nft_id = token.nft_id
        contract_address = token.contract.contract_address
        web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        abi = get_contract_abi()
        target_address = web3.toChecksumAddress(target_address)
        contract_instance = web3.eth.contract(address=contract_address, abi=abi)
        balance = contract_instance.functions.balanceOf(target_address, nft_id).call()
        self.stdout.write(self.style.SUCCESS('balance {}, wallet : {}'.format(balance, target_address)))


