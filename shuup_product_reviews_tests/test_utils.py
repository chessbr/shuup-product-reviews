# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest

from shuup.testing import factories
from shuup_product_reviews.utils import (
    get_reviews_aggregation_for_product, render_product_review_ratings
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

        assert '<span class="rating">%0.1f</span>' % totals["rating"] in rendered
        assert '%d reviews' % totals["reviews"] in rendered

        rendered = render_product_review_ratings(product_no_reviews)
        assert rendered == ""
