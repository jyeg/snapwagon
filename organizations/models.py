# Standard library imports.
import decimal
import uuid

# Django imports.
from django.db import models
from django.db.models import Q
from django.utils import timezone

# Third-party imports.
from coupon_codes import cc_generate
from localflavor.us.models import PhoneNumberField
from rest_framework.reverse import reverse

__author__ = 'Jason Parent'


class Organization(models.Model):
    """

    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=250)
    desc = models.TextField(null=True, blank=True)
    stripe_organization_id = models.CharField(max_length=250, null=True, blank=True, help_text='The stripe connect Id used to group payments')

    @staticmethod
    def autocomplete_search_fields():
        return 'name__icontains',

    def __str__(self):
        return self.name


class OfferManager(models.Manager):
    def current_offers(self):
        return self.get_queryset().exclude(expiration_ts__lte=timezone.now())


class Offer(models.Model):
    """A special deal offered to customers that allows them to purchase a good/service at a discounted price."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=250)
    desc = models.TextField(null=True, blank=True)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    discounted_value = models.DecimalField(decimal_places=2, max_digits=10)
    image_url = models.ImageField(upload_to='images', null=True, blank=True)
    organization = models.ForeignKey('organizations.Organization', null=True, blank=True)
    expiration_ts = models.DateTimeField(null=True, blank=True)
    rank = models.IntegerField(default=0)

    objects = OfferManager()

    @property
    def discount_percentage(self):
        context = decimal.getcontext()
        context.prec = 2
        return int(100 * (self.discounted_value / self.value))

    @staticmethod
    def autocomplete_search_fields():
        return 'id__icontains', 'title__icontains',

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('api:offer_detail', kwargs={'offer_id': str(self.id)})


class Customer(models.Model):
    """A person who has purchased a good/service from an organization."""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    offers = models.ManyToManyField('organizations.Offer', through='organizations.Order',
                                    through_fields=('customer', 'offer'))

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @staticmethod
    def autocomplete_search_fields():
        return 'first_name__icontains', 'last_name__icontains', 'email__icontains',

    def __str__(self):
        return self.email


class Order(models.Model):
    """The actual purchase of a good/service."""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey('organizations.Customer', related_name='orders')
    offer = models.ForeignKey('organizations.Offer', related_name='orders')
    quantity = models.IntegerField()

    def __str__(self):
        return '{customer}:{offer}:{quantity}'.format(
            customer=self.customer, offer=self.offer, quantity=self.quantity)


def generate_coupon_code():
    return cc_generate(n_parts=4)


class Voucher(models.Model):
    """

    """

    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey('organizations.Customer', related_name='vouchers')
    offer = models.ForeignKey('organizations.Offer', related_name='vouchers')
    coupon_code = models.CharField(max_length=19, editable=False, default=generate_coupon_code)
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        return self.coupon_code
