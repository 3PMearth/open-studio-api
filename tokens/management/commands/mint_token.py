from django.core.management.base import BaseCommand, CommandError
from tokens.tasks import mint_token

class Command(BaseCommand):
    """
    Manual mint token
    """
    help = "Manual mint token"

    def add_arguments(self, parser):
        parser.add_argument('--token_id', type=int)

    def handle(self, *args, **options):
        token_id = options['token_id']
        mint_token(token_id)
        self.stdout.write(self.style.SUCCESS('Successfully mint token "%s"' % token_id))