# Django imports.
from django.conf.urls import url

# Third-party imports.
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

# Local imports.
from .apis import (ClientToken, OfferView, OfferByOrganizationView, OrderView, OrganizationView, OrganizationDetailView,
                   SignUpView)

__author__ = 'Jason Parent'

urlpatterns = [
    url(r'^sign_up/$', SignUpView.as_view(), name='sign_up'),
    url(r'^token/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^client_token/$', ClientToken.as_view(), name='client_token'),
    url(r'^organization/(?P<organization_id>\d+)/offer/$', OfferByOrganizationView.as_view({'get': 'list'}), name='offer_by_organization'),
    url(r'^organization/(?P<organization_id>\d+)/$', OrganizationDetailView.as_view(), name='organization_detail'),
    url(r'^organization/$', OrganizationView.as_view(), name='organization_list'),
    url(r'^offer/(?P<offer_id>[^/]+)/$', OfferView.as_view({'get': 'retrieve'}), name='offer_detail'),
    url(r'^offer/$', OfferView.as_view({'get': 'list'}), name='offer_list'),
    # url(r'^order/(?P<order_id>[^/]+)/$', OrderView.as_view(), name='order_detail'),
    url(r'^order/$', OrderView.as_view(), name='order_list'),
]
