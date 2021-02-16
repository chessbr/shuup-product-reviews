# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from shuup import configuration
from shuup.core.models import OrderStatus, ProductType
from shuup.testing import factories

from shuup_product_reviews.utils import (
    get_pending_products_reviews,
    get_reviews_aggregation_for_product,
    render_product_review_ratings,
)

from .factories import create_random_review_for_product


@pytest.mark.django_db
def test_comments_view():
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())
    product_no_reviews = factories.create_product("product-no", shop=shop, supplier=factories.get_default_supplier())

    # create 15 reviews for the product, it should exist 3 pages of comments
    [create_random_review_for_product(shop, product) for _ in range(15)]

    for test in range(2):
        totals = get_reviews_aggregation_for_product(product)
        rendered = render_product_review_ratings(product)

        expected_rating = (
            """
            <span class="rating">
                %0.1f
                <span class="sr-only">Rating&nbsp;</span>
            </span>
        """
            % totals["rating"]
        )
        assert expected_rating in rendered
        assert "%d reviews" % totals["reviews"] in rendered

        rendered = render_product_review_ratings(product_no_reviews)
        assert rendered == ""


@pytest.mark.django_db
def test_ignored_products(rf):
    shop = factories.get_default_shop()
    supplier = factories.get_default_supplier()
    invalid_type = ProductType.objects.create(name="invalid")
    customer = factories.create_random_person()
    user = factories.create_random_user()
    customer.user = user
    customer.save()
    product1 = factories.create_product("product1", shop=shop, supplier=supplier)
    product2 = factories.create_product("product2", shop=shop, supplier=supplier, type=invalid_type)

    for product in [product1, product2]:
        order = factories.create_order_with_product(product, supplier, 1, 10, shop=shop)
        order.create_payment(order.taxful_total_price)
        order.customer = customer
        order.status = OrderStatus.objects.get_default_complete()
        order.save()

    request = rf.get("/")
    request.person = customer
    request.customer = customer
    request.shop = shop
    request.user = user
    pending_products = get_pending_products_reviews(request)

    assert len(pending_products) == 2

    configuration.set(shop, "product_review_ignore_product_types", [invalid_type.pk])

    pending_products = get_pending_products_reviews(request)
    assert len(pending_products) == 1
    assert product1 in pending_products

    configuration.set(shop, "product_review_ignore_product_types", None)
