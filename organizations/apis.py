# Standard library imports.
# import logging
import datetime

# Django imports.
# from django.conf import settings
from django.utils import timezone

# Third-party imports.
import braintree
from rest_framework import (status, views, viewsets)
from rest_framework.response import Response

# Local imports.
from .models import (Customer, Offer, Order, Voucher)
from .serializers import (CustomerSerializer, OfferSerializer, OrderSerializer)

__author__ = 'Jason Parent'

# logger = logging.getLogger(__name__)


class ClientToken(views.APIView):
    def get(self, request, *args, **kwargs):
        return Response(data={'token': braintree.ClientToken.generate()})


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
        sale_data = request.data.pop('sale')
        customer_data = request.data.pop('customer')
        customer_email = customer_data.pop('email')
        customer, _ = Customer.objects.get_or_create(email=customer_email, defaults=customer_data)
        offer_data = request.data.pop('offer')
        offer = Offer.objects.get(id=offer_data.get('id'))
        request_data = request.data
        request_data['customer_id'] = customer.id
        request_data['offer_id'] = offer.id
        order = Order.objects.create(**request_data)

        # Process sale.
        result = braintree.Transaction.sale({
            'amount': offer.discounted_value * int(order.quantity),
            # 'customer': CustomerSerializer(order.customer).data,
            'options': {
                'submit_for_settlement': True
            },
            'payment_method_nonce': sale_data.get('payment_method_nonce')
        })

        # Create vouchers.
        if result.is_success:
            Voucher.objects.bulk_create([Voucher(customer=customer, offer=offer) for _ in range(order.quantity)])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': result.message})

        # TODO: Send email to customer with vouchers' coupon codes.

        return Response(data=OrderSerializer(order).data)
