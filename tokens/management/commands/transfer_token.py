from django.core.management.base import BaseCommand, CommandError
from tokens.tasks import transfer_token

class Command(BaseCommand):
    """
    Manual transfer token
    """
    help = "Manual transfer token"

    def add_arguments(self, parser):
        parser.add_argument('--token_id_list', nargs='+', type=int)
        parser.add_argument('--to_address', type=str)
        parser.add_argument('--amount_list', nargs='+', type=int)

    def handle(self, *args, **options):
        token_id_list = options['token_id_list']
        to_address = options['to_address']
        amount_list = options['amount_list']

        # show all the arguments
        print(token_id_list)
        print(to_address)
        print(amount_list)

        transfer_token(token_id_list, to_address, amount_list)
        self.stdout.write(self.style.SUCCESS('Successfully transfer token'))