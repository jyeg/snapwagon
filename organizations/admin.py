# Django imports.
from django.contrib import admin
from django.utils.timezone import now

# Local imports.
from .models import (Customer, Offer, Order, Organization, Voucher)

__author__ = 'Jason Parent'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'email', 'phone_number',)
    list_display = ('first_name', 'last_name', 'email', 'phone_number',)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    fields = ('id', 'title', 'desc', 'value', 'discounted_value', 'image_url', 'organization', 'expiration_ts', 'rank',)
    readonly_fields = ('id', 'discount_percentage',)
    list_display = ('id', 'title', 'desc', 'value', 'discounted_value', 'discount_percentage', 'image_url',
                    'organization', 'expiration_ts', 'rank',)
    raw_id_fields = ('organization',)
    list_select_related = ('organization',)
    autocomplete_lookup_fields = {
        'fk': ('organization',),
    }

    class Media:
        js = ('/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('customer', 'offer', 'quantity',)
    list_display = ('customer', 'offer', 'quantity',)
    raw_id_fields = ('customer', 'offer',)
    list_select_related = ('customer', 'offer',)
    autocomplete_lookup_fields = {
        'fk': ('customer', 'offer',),
    }


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'desc', 'stripe_organization_id',)
    readonly_fields = ('id',)
    list_display = ('id', 'name', 'desc', 'stripe_organization_id',)

    class Media:
        js = ('/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
              '/static/grappelli/tinymce_setup/tinymce_setup.js',)


def redeem_voucher(modeladmin, request, queryset):
    queryset.update(redeemed=True, updated=now())

redeem_voucher.short_description = 'Redeem voucher'


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    fields = ('customer', 'offer', 'coupon_code', 'redeemed', 'created', 'updated',)
    readonly_fields = ('coupon_code','created', 'updated',)
    list_display = ('customer', 'offer', 'coupon_code', 'redeemed', 'created', 'updated',)
    raw_id_fields = ('customer', 'offer',)
    list_select_related = ('customer', 'offer',)
    autocomplete_lookup_fields = {
        'fk': ('customer', 'offer',),
    }
    actions = [redeem_voucher]
