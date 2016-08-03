from django.core.management.base import BaseCommand, CommandError
from random import randint
import random
import uuid

from apps.general.utils import custom_slugify, random_word, get_hex_string
from apps.leadquote.models import CustomerDetails


class Command(BaseCommand):
    def handle(self, *args, **options):
        customers = CustomerDetails.objects.all()
        for customer in customers:
            if customer.transaction_id:
                new_word = random_word(25)
                custom_id = custom_slugify(new_word)
                hex_word = get_hex_string(18)
                shuffled = ''.join(random.sample(hex_word+'-'+'-', 36))
                if custom_id:
                    customer.transaction_id = str(uuid.uuid4())
                    customer.save()
        self.stdout.write('Successfully closed')
