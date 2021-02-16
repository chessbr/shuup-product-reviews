# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from shuup.core.models import Contact, Supplier, get_person_contact

from shuup_vendor_reviews.models import VendorReview


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name")


class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ("id", "name")


class VendorReviewSerializer(serializers.ModelSerializer):
    reviewer = ReviewerSerializer()

    class Meta:
        model = VendorReview
        exclude = ("shop", "status", "supplier", "modified_on")


class ReviewSerializer(serializers.ModelSerializer):
    supplier = VendorSerializer(read_only=True)
    reviewer = ReviewerSerializer(read_only=True)
    destination = serializers.PrimaryKeyRelatedField(
        write_only=True, source="supplier", queryset=Supplier.objects.enabled()
    )

    class Meta:
        model = VendorReview
        exclude = ("shop",)
        extra_kwargs = dict(
            status=dict(read_only=True),
        )

    def create(self, data):
        data["shop"] = self.context["request"].shop
        data["reviewer"] = get_person_contact(self.context["request"].user)

        existing_vendor_review = VendorReview.objects.filter(
            supplier=data["supplier"], reviewer=data["reviewer"], shop=data["shop"]
        )
        if existing_vendor_review.exists():
            raise serializers.ValidationError(_("A review for this vendor already exists."))

        return super().create(data)
