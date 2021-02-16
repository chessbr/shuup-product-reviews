# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from rest_framework import filters, mixins, response, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from shuup.core.models import Supplier, get_person_contact

from shuup_vendor_reviews.api.serializers import ReviewSerializer, VendorReviewSerializer, VendorSerializer
from shuup_vendor_reviews.models import ReviewStatus, VendorReview
from shuup_vendor_reviews.utils import get_pending_vendors_reviews


class VendorReviewsViewSet(viewsets.GenericViewSet):
    """
    List all reviews from a given vendor
    """

    queryset = VendorReview.objects.none()
    serializer_class = VendorReviewSerializer

    def get_queryset(self):
        return VendorReview.objects.filter(
            shop=self.request.shop,
            supplier=self.get_object(),
            status=ReviewStatus.APPROVED,
        ).order_by("-created_on")

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        return get_object_or_404(Supplier.objects.all(), **filter_kwargs)

    def get_view_name(self):
        return "Vendor Reviews - Reviews"


class ReviewFilters(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        # Filter the views by a given vendor
        vendor = request.query_params.get("vendor")
        if vendor:
            queryset = queryset.filter(supplier=vendor)
        return queryset


class ReviewViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Create, update and list reviews posted by the current authenticated user
    """

    queryset = VendorReview.objects.none()
    serializer_class = ReviewSerializer
    filter_backends = (ReviewFilters,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return self.queryset

        vendor_reviews = VendorReview.objects.filter(
            shop=self.request.shop, reviewer=get_person_contact(self.request.user)
        )

        if self.action == "pending":
            return get_pending_vendors_reviews(self.request).exclude(
                pk__in=vendor_reviews.values_list("supplier", flat=True)
            )

        return vendor_reviews.order_by("-created_on")

    def get_serializer_class(self):
        if self.action == "pending":
            return VendorSerializer

        return super().get_serializer_class()

    @action(detail=False, methods=["get"])
    def pending(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_view_name(self):
        return "Vendor Reviews - Review"
