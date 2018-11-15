# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.db.models import Avg, Sum

from shuup.core.models import Order, Product, ProductMode
from shuup_product_reviews.models import ProductReviewAggregation


def get_orders_for_review(request):
    """
    Returns an order queryset that contains all products that could be reviewed.
    It is basically any completed orders.
    """
    return Order.objects.complete().filter(
        shop=request.shop,
        customer__in=[request.customer, request.person]
    )


def get_pending_products_reviews(request):
    """
    Returns a Product queryset that contains all products
    that can be reviewed by the current request shop and contact
    """
    orders = Order.objects.complete().filter(
        shop=request.shop,
        customer__in=[request.customer, request.person]
    ).distinct()
    products = Product.objects.all_except_deleted(shop=request.shop).filter(
        order_lines__order__in=orders,
        mode__in=[ProductMode.NORMAL, ProductMode.VARIATION_CHILD]
    ).distinct()

    return products.exclude(product_reviews__reviewer=request.person)


def get_reviews_aggregation_for_product(product):
    product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
    return ProductReviewAggregation.objects.filter(product_id__in=product_ids).aggregate(
        rating=Avg("rating"),
        reviews=Sum("review_count"),
        would_recommend=Sum("would_recommend")
    )
