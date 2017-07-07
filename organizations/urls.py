# Django imports.
from django.conf.urls import url

# Local imports.
from .apis import (ClientToken, OfferView, OfferByOrganizationView, OrderView)

__author__ = 'Jason Parent'

urlpatterns = [
    url(r'^client_token/$', ClientToken.as_view(), name='client_token'),
    url(r'^organization/(?P<organization_id>\d+)/offer/', OfferByOrganizationView.as_view({'get': 'list'}), name='offer_by_organization'),
    url(r'^offer/(?P<offer_id>[^/]+)/$', OfferView.as_view({'get': 'retrieve'}), name='offer_detail'),
    url(r'^offer/$', OfferView.as_view({'get': 'list'}), name='offer_list'),
    # url(r'^order/(?P<order_id>[^/]+)/$', OrderView.as_view(), name='order_detail'),
    url(r'^order/$', OrderView.as_view(), name='order_list'),
]
