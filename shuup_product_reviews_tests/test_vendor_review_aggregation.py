# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from shuup.core.models import Supplier
from shuup.testing import factories

from shuup_vendor_reviews.models import VendorReview
from shuup_vendor_reviews.utils import get_reviews_aggregation_for_supplier

from .factories import create_multi_supplier_order_to_review, create_vendor_review_for_order_line


@pytest.mark.django_db
def test_rejecting_all_reviews_multiple_suppliers():
    shop = factories.get_default_shop()
    customer = factories.create_random_person("en")
    user = factories.create_random_user("en")
    user.set_password("user")
    user.save()
    customer.user = user
    customer.save()

    suppliers = [
        ("1", "Supplier 1 name", 1, 5),
        ("2", "Supplier 2 name", 2, 2),
        ("3", "Supplier 3 name", 3, 5),
        ("4", "Supplier 4 name", 5, 5),
        ("5", "Supplier 5 name", 1, 4),
    ]
    product = factories.create_product("test1", shop=shop, default_price=10)
    shop_product = product.get_shop_instance(shop=shop)
    for identifier, name, rating1, rating2 in suppliers:
        supplier = Supplier.objects.create(identifier=identifier, name=name)
        shop_product.suppliers.add(supplier)

    assert shop_product.suppliers.count() == 5

    order1 = create_multi_supplier_order_to_review(shop_product, customer)
    assert order1.lines.count() == 5
    for identifier, name, rating1, rating2 in suppliers:
        create_vendor_review_for_order_line(order1.lines.filter(supplier__identifier=identifier).first(), rating1)

    order2 = create_multi_supplier_order_to_review(shop_product, customer)
    assert order1.lines.count() == 5
    for identifier, name, rating1, rating2 in suppliers:
        create_vendor_review_for_order_line(order2.lines.filter(supplier__identifier=identifier).first(), rating2)

    assert VendorReview.objects.count() == 10
    for identifier, name, rating1, rating2 in suppliers:
        totals = get_reviews_aggregation_for_supplier(Supplier.objects.get(identifier=identifier))
        assert totals["rating"] == (rating1 + rating2) / 2
        assert totals["reviews"] == 2
