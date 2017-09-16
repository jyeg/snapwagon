# Third-party imports.
from rest_framework import serializers

# Local imports.
from .models import (Customer, Offer, Order, Organization, Voucher)

__author__ = 'Jason Parent'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'phone_number',)


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title', 'desc', 'value', 'discounted_value', 'discount_percentage', 'image_url',
                  'organization', 'expiration_ts', 'rank',)
        read_only_fields = ('discount_percentage',)


class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    offer = OfferSerializer(read_only=True)

    # def create(self, validated_data):
    #     order = Order.objects.create(**validated_data)
    #     return order
    #
    # def update(self, instance, validated_data):
    #     raise NotImplementedError()

    class Meta:
        model = Order
        fields = ('customer', 'offer', 'quantity',)


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('name', 'desc',)


class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ('id', 'customer', 'offer', 'coupon_code', 'redeemed',)


class CouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = ('coupon_code',)


class SourceSerializer(serializers.Serializer):
    brand = serializers.CharField(read_only=True)
    last4 = serializers.CharField(read_only=True)

    def create(self, validated_data):
        raise NotImplementedError('Create not available.')

    def update(self, instance, validated_data):
        raise NotImplementedError('Update not available.')


class ChargeSerializer(serializers.Serializer):
    amount = serializers.IntegerField(read_only=True)
    source = SourceSerializer(read_only=True)

    def create(self, validated_data):
        raise NotImplementedError('Create not available.')

    def update(self, instance, validated_data):
        raise NotImplementedError('Update not available.')


class SparkPostSerializer(serializers.Serializer):
    charge = ChargeSerializer(read_only=True)
    customer_name = serializers.CharField(read_only=True)
    offer = OfferSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    vouchers = CouponCodeSerializer(read_only=True, many=True)

    def create(self, validated_data):
        raise NotImplementedError('Create not available.')

    def update(self, instance, validated_data):
        raise NotImplementedError('Update not available.')
