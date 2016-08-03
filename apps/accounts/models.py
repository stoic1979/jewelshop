from __future__ import unicode_literals

import re
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import (
     AbstractUser
)
from django.conf import settings
from datetime import datetime

from autoslug import AutoSlugField
from autoslug.settings import slugify as default_slugify

import random
import string


def random_word(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))


def custom_slugify(value):
        time_now = str(datetime.now())
        random_string = random_word(11)
        p = re.compile(r'<.*?>')
        string_value = p.sub('', value)
        final_slug = string_value+random_string+time_now
        return default_slugify(final_slug).replace(' ', '_')


class User(AbstractUser):
    """
    Custom user model
    """

    name_slug_field = AutoSlugField(populate_from='first_name', slugify=custom_slugify, null=True, blank=True)
    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    def get_absolute_url(self):
        return reverse('activate-user', kwargs={'slug': slugify(self.user_profile.activation_key)})

    def __unicode__(self):
        return self.get_full_name()



