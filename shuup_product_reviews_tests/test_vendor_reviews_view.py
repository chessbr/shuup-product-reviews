# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from bs4 import BeautifulSoup
from django.test.client import Client
from django.urls import reverse
from shuup.core.models import Supplier
from shuup.testing import factories

from .factories import create_multi_supplier_order_to_review


class SmartClient(Client):
    def soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        assert 200 <= response.status_code <= 299, "Valid status"
        return BeautifulSoup(response.content)

    def response_and_soup(self, path, data=None, method="get"):
        response = getattr(self, method)(path=path, data=data)
        return (response, BeautifulSoup(response.content))


@pytest.mark.django_db
def test_reviews_view_multiple_supplires(rf):
    shop = factories.get_default_shop()
    customer = factories.create_random_person("en")
    user = factories.create_random_user("en")
    user.set_password("user")
    user.save()
    customer.user = user
    customer.save()

    supplier1_name = "Supplier 1 name"
    supplier1 = Supplier.objects.create(identifier="1", name=supplier1_name)
    supplier1.shops.set([shop])
    supplier2_name = "Supplier 2 name"
    supplier2 = Supplier.objects.create(identifier="2", name=supplier2_name)
    supplier2.shops.set([shop])
    product = factories.create_product("test1", shop=shop, supplier=supplier1, default_price=10)
    shop_product = product.get_shop_instance(shop=shop)
    assert shop_product.suppliers.filter(id=supplier1.id).exists()
    shop_product.suppliers.add(supplier2)
    assert shop_product.suppliers.filter(id=supplier2.id).exists()

    create_multi_supplier_order_to_review(shop_product, customer)

    client = SmartClient()
    client.login(username=user.username, password="user")

    response, soup = client.response_and_soup(reverse("shuup:vendor_reviews"))
    assert "Vendors to Review" in soup.text
    assert (
        len(
            soup.findAll("div", attrs={"class": "vendors-to-review"})[0].findChildren(
                "div", attrs={"class": "list-group-item"}
            )
        )
        == 2
    )
    assert "%s" % supplier2_name in soup.text
    assert "%s" % supplier1_name in soup.text
