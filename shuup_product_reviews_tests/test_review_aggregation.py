# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from shuup.testing import factories

from shuup_product_reviews.models import ProductReview
from shuup_product_reviews.utils import get_reviews_aggregation_for_product

from .factories import create_random_review_for_product


@pytest.mark.django_db
def test_rejecting_all_reviews():
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())
    create_random_review_for_product(shop, product, rating=5)

    totals = get_reviews_aggregation_for_product(product)
    assert totals["rating"] == 5
    assert totals["reviews"] == 1

    # Now let's reject all reviews for product and let's see that all cool
    for review in ProductReview.objects.filter(product=product):
        review.reject()

    totals = get_reviews_aggregation_for_product(product)
    assert totals["rating"] is None
    assert totals["reviews"] is None
