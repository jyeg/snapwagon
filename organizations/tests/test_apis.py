# Standard library imports.
import datetime
import decimal
import re
from unittest import skip
from unittest.mock import (Mock, patch)

# Django imports.
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# Third-party imports.
from factory import (LazyAttribute, Sequence)
from factory.fuzzy import (FuzzyDateTime, FuzzyDecimal)
from factory.django import DjangoModelFactory
from nose.tools import (assert_dict_equal, assert_equal, assert_in, assert_list_equal, assert_regexp_matches,
                        assert_true)
from rest_framework.reverse import reverse
from rest_framework.test import (APIClient, APITestCase)
import sparkpost
import stripe

# Local imports.
from ..models import (Customer, Offer, Order, Organization, Voucher)
from ..serializers import (CustomerSerializer, OfferSerializer, OrderSerializer, SparkPostSerializer)
from ..apis import SubstitutionData

__author__ = 'Jason Parent'

COUPON_CODE_PATTERN = re.compile(r'^\w{4}-\w{4}-\w{4}-\w{4}$')


class OfferFactory(DjangoModelFactory):
    title = Sequence(lambda n: f'Offer {n}')
    value = FuzzyDecimal(low=20.00, high=40.00)
    discounted_value = FuzzyDecimal(low=10.00, high=15.00)
    expiration_ts = FuzzyDateTime(start_dt=timezone.now() + datetime.timedelta(days=7),
                                  end_dt=timezone.now() + datetime.timedelta(days=17))

    class Meta:
        model = Offer


class OfferTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_can_list_offers(self):
        offers = OfferFactory.create_batch(5)
        response = self.client.get(reverse('api:offer_list'))
        assert_equal(200, response.status_code)
        assert_equal(5, len(response.data))
        self.assertCountEqual(OfferSerializer(offers, many=True).data, response.data)

    def test_user_can_retrieve_offer(self):
        seven_days_from_now = timezone.now() + datetime.timedelta(days=7)
        offer = Offer.objects.create(
            title='Offer', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            expiration_ts=seven_days_from_now)
        response = self.client.get(offer.get_absolute_url())
        assert_dict_equal(OfferSerializer(offer).data, response.data)
        assert_equal(seven_days_from_now, parse_datetime(response.data.get('expiration_ts')))

    def test_user_can_retrieve_offers_that_have_not_expired(self):
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)
        seven_days_from_now = timezone.now() + datetime.timedelta(days=7)
        offer1 = Offer.objects.create(
            title='Offer 1', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            expiration_ts=seven_days_from_now)
        offer2 = Offer.objects.create(
            title='Offer 2', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            expiration_ts=seven_days_ago)
        offer3 = Offer.objects.create(
            title='Offer 3', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            expiration_ts=seven_days_from_now)
        response = self.client.get(reverse('api:offer_list'))
        assert_equal(200, response.status_code)
        self.assertCountEqual(OfferSerializer([offer1, offer3], many=True).data, response.data)

    def test_user_can_retrieve_offers_by_organization_id(self):
        organization1 = Organization.objects.create(name='Organization 1')
        organization2 = Organization.objects.create(name='Organization 2')
        offer1 = Offer.objects.create(
            title='Offer 1', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            organization=organization1)
        offer2 = Offer.objects.create(
            title='Offer 2', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            organization=organization1)
        offer3 = Offer.objects.create(
            title='Offer 3', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'),
            organization=organization2)
        response = self.client.get(reverse('api:offer_by_organization', kwargs={'organization_id': organization1.id}))
        assert_equal(200, response.status_code)
        self.assertCountEqual(OfferSerializer([offer1, offer2], many=True).data, response.data)

    def test_user_can_retrieve_offers_in_order_by_rank(self):
        offer1 = Offer.objects.create(
            title='Offer 1', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'), rank=2)
        offer2 = Offer.objects.create(
            title='Offer 2', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'))
        offer3 = Offer.objects.create(
            title='Offer 3', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'), rank=1)
        response = self.client.get(reverse('api:offer_list'))
        assert_equal(200, response.status_code)
        assert_list_equal(OfferSerializer([offer1, offer3, offer2], many=True).data, response.data)


class OrderTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.offer = Offer.objects.create(
            title='Offer', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'))

    def create_order(self, offer_id, token='tok_visa'):
        return {
            'customer': {
                'first_name': 'Jason',
                'last_name': 'Parent',
                'email': 'jason.a.parent@gmail.com',
                'phone_number': None
            },
            'offer': {
                'id': str(offer_id)
            },
            'quantity': 1,
            'charge': {
                'token': token
            }
        }

    @skip
    def test_user_can_retrieve_client_token(self):
        response = self.client.post(reverse('api:client_token'), data={
            'card': {
                'number': '4242424242424242',
                'exp_month': 12,
                'exp_year': 2018,
                'cvc': '123'
            }
        }, format='json')
        assert_in('token', response.data)

    def test_new_customer_can_place_order(self):
        # Mock call to Stripe.
        mock_charge = Mock(status='succeeded')
        patch('organizations.apis.stripe.Charge.create', return_value=mock_charge).start()

        # Mock call to SparkPost.
        patch('organizations.apis.sparkpost.SparkPost').start()

        assert_equal(0, Customer.objects.count())
        order = self.create_order(self.offer.id)
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(1, Customer.objects.count())
        assert_equal(1, Order.objects.count())
        order = Order.objects.last()
        assert_dict_equal(OrderSerializer(order).data, response.data)

    def test_existing_customer_can_place_order(self):
        # Mock call to Stripe.
        mock_charge = Mock(status='succeeded')
        patch('organizations.apis.stripe.Charge.create', return_value=mock_charge).start()

        # Mock call to SparkPost.
        patch('organizations.apis.sparkpost.SparkPost').start()

        Customer.objects.create(first_name='Jason', last_name='Parent', email='jason.a.parent@gmail.com')
        assert_equal(1, Customer.objects.count())
        order = self.create_order(self.offer.id)
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(1, Customer.objects.count())
        assert_equal(1, Order.objects.count())
        order = Order.objects.last()
        assert_dict_equal(OrderSerializer(order).data, response.data)

    def test_user_can_place_order_with_success(self):
        # Mock call to Stripe.
        mock_charge = Mock(status='succeeded')
        mock_create = patch('organizations.apis.stripe.Charge.create', return_value=mock_charge).start()

        # Mock call to SparkPost.
        patch('organizations.apis.sparkpost.SparkPost').start()

        order = self.create_order(self.offer.id, token='tok_visa')
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(200, response.status_code)
        mock_create.assert_called_once_with(
            amount=int(self.offer.discounted_value * 1 * 100),
            # 'customer': CustomerSerializer(Customer.objects.last()).data,
            currency='usd',
            source='tok_visa'
        )
        vouchers = Voucher.objects.filter(customer__email='jason.a.parent@gmail.com', offer_id=self.offer.id)
        assert_equal(1, vouchers.count())

    def test_user_can_place_order_with_failure(self):
        # Mock call to Stripe.
        mock_charge = Mock(status='failed', failure_message='Visa card declined.')
        mock_create = patch('organizations.apis.stripe.Charge.create', return_value=mock_charge).start()

        # Mock call to SparkPost.
        patch('organizations.apis.sparkpost.SparkPost').start()

        order = self.create_order(self.offer.id, token='tok_chargeDeclined')
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(400, response.status_code)
        mock_create.assert_called_once_with(
            amount=int(self.offer.discounted_value * 1 * 100),
            # 'customer': CustomerSerializer(Customer.objects.last()).data,
            currency='usd',
            source='tok_chargeDeclined'
        )
        vouchers = Voucher.objects.filter(customer__email='jason.a.parent@gmail.com', offer_id=self.offer.id)
        assert_equal(0, vouchers.count())

    def test_successful_order_generates_email(self):
        # Mock call to Stripe.
        mock_charge = Mock(status='succeeded')
        mock_charge.source.brand = 'Visa'
        mock_charge.source.customer = 'Jason Parent'
        mock_charge.source.last_4 = '1234'
        mock_create = patch('organizations.apis.stripe.Charge.create', return_value=mock_charge).start()

        # Mock call to SparkPost.
        mock_send = Mock()
        mock_sparkpost = patch('organizations.apis.sparkpost.SparkPost').start()
        mock_sparkpost.return_value.transmissions.send = mock_send

        order = self.create_order(self.offer.id, token='tok_visa')
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(200, response.status_code)
        assert_true(mock_send.called)
        call_args, call_kwargs = mock_send.call_args
        assert_list_equal([order['customer']['email']], call_kwargs.get('recipients'))
        assert_equal('order-confirmation', call_kwargs.get('template'))
        assert_true(call_kwargs.get('use_draft_template'))
        assert_dict_equal(SparkPostSerializer(SubstitutionData(
            charge=mock_charge,
            offer=Offer.objects.get(id=order['offer']['id']),
            organization=Organization.objects.last(),
            vouchers=Voucher.objects.all()
        )).data, call_kwargs.get('substitution_data'))

    @skip
    def test_user_receives_email_after_successful_order(self):
        organization = Organization.objects.create(name='ABC Inc.', desc='')
        offer = Offer.objects.create(title='Offer', value=decimal.Decimal('20.00'),
                                     discounted_value=decimal.Decimal('15.00'), organization=organization)
        order = self.create_order(offer.id, token='tok_visa')
        response = self.client.post(reverse('api:order_list'), data=order, format='json')
        assert_equal(200, response.status_code)

    def tearDown(self):
        patch.stopall()


class VoucherTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name='Jason', last_name='Parent', email='jason.a.parent@gmail.com')
        self.offer = Offer.objects.create(
            title='Offer', value=decimal.Decimal('20.00'), discounted_value=decimal.Decimal('15.00'))

    def test_coupon_code_is_generated_on_voucher_creation(self):
        voucher = Voucher.objects.create(customer=self.customer, offer=self.offer)
        assert_regexp_matches(voucher.coupon_code, COUPON_CODE_PATTERN)
