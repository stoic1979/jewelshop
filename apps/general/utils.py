import re
import os, binascii

from django.conf import settings
from datetime import datetime
from autoslug.settings import slugify as default_slugify
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template


import random
import string


def random_word(length):
   return '-'.join(random.choice(string.lowercase) for i in range(length))


def custom_slugify(value):
        time_now = str(datetime.now())
        random_string = random_word(11)
        p = re.compile(r'<.*?>')
        string_value = p.sub('', value)
        final_slug = string_value+random_string
        return default_slugify(final_slug).replace(' ', '_')


def get_hex_string(length):
        hex_string = binascii.b2a_hex(os.urandom(length))
        shuffled = ''.join(random.sample(hex_string+'-'+'-', 36))
        return default_slugify(shuffled)


def send_email(template_name=None, from_email=None, to_email=[], context=None, subject=''):
        """
        Sending admin emails.
        :param bind_form:
        :param recievers:
        :return:
        """
        if not from_email:
                from_email = settings.DEFAULT_FROM_EMAIL
        if not subject:
                subject = 'Quick quote notifications'
        template = get_template(template_name)
        context = Context(context)
        content = template.render(context)
        msg = EmailMessage(subject, content, from_email, to=to_email,)
        msg.content_subtype = "html"
        msg.send()