# Standard library imports.
import collections
import datetime
import json
import logging

# Django imports.
# from django.conf import settings
from django.utils import timezone

# Third-party imports.
from rest_framework import (generics, status, views, viewsets)
from rest_framework.response import Response
import sparkpost
from sparkpost.exceptions import SparkPostAPIException
import stripe
from stripe.error import CardError

# Local imports.
from .models import (Customer, Offer, Order, Organization, Voucher)
from .serializers import (CustomerSerializer, OfferSerializer, OrderSerializer, OrganizationSerializer, SparkPostSerializer)

__author__ = 'Jason Parent'

logger = logging.getLogger(__name__)

SubstitutionData = collections.namedtuple('SubstitutionData', ['charge', 'customer_name', 'offer', 'organization', 'vouchers'])


class ClientToken(views.APIView):
    def post(self, request, *args, **kwargs):
        card = request.data.get('card')
        token = stripe.Token.create(card=card)
        return Response(data={'token': token.id})


class OfferView(viewsets.ReadOnlyModelViewSet):
    queryset = Offer.objects.current_offers().order_by('-rank')
    serializer_class = OfferSerializer
    lookup_url_kwarg = 'offer_id'


class OfferByOrganizationView(viewsets.ReadOnlyModelViewSet):
    serializer_class = OfferSerializer
    lookup_url_kwarg = 'organization_id'

    def get_queryset(self):
        return Offer.objects.current_offers().filter(
            organization_id=self.kwargs[self.lookup_url_kwarg]
        ).order_by('-rank')


class OrderView(views.APIView):
    def post(self, request, *args, **kwargs):
        charge_data = request.data.pop('charge')
        customer_data = request.data.pop('customer')
        customer_email = customer_data.get('email')
        try:
            customer = Customer.objects.get(email=customer_email)
        except Customer.DoesNotExist:
            customer_serializer = CustomerSerializer(data=customer_data)
            if customer_serializer.is_valid(raise_exception=True):
                customer = customer_serializer.create(customer_serializer.validated_data)
        offer_data = request.data.pop('offer')
        offer = Offer.objects.get(id=offer_data.get('id'))
        request_data = request.data
        request_data['customer_id'] = customer.id
        request_data['offer_id'] = offer.id
        order = Order.objects.create(**request_data)

        # Process charge.
        try:
            charge = stripe.Charge.create(
                amount=int(offer.discounted_value * int(order.quantity) * 100),
                currency='usd',
                source=charge_data.get('token')
            )
        except CardError as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': error.code})
        else:
            if charge.status == 'succeeded':
                # Create vouchers.
                vouchers = [
                    Voucher.objects.create(customer=customer, offer=offer)
                    for _ in range(order.quantity)
                ]

                # Send email.
                try:
                    substitution_data = SubstitutionData(
                        charge=charge,
                        customer_name=customer.get_full_name(),
                        offer=offer,
                        organization=offer.organization,
                        vouchers=vouchers
                    )

                    sp = sparkpost.SparkPost()
                    sp.transmissions.send(
                        recipients=[customer_email],
                        template='order-confirmation',
                        use_draft_template=True,
                        substitution_data=SparkPostSerializer(substitution_data).data
                    )
                except SparkPostAPIException as exception:
                    logger.error(exception.errors)

            return Response(data=OrderSerializer(order).data)
        
        
class OrganizationView(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
