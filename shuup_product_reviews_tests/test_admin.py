# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json

import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client

from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware
from shuup_product_reviews.admin_module.mass_actions import (
    ApproveProductReviewMassAction, RejectProductReviewMassAction
)
from shuup_product_reviews.models import ProductReview, ReviewStatus

from .factories import create_random_review_for_product


@pytest.mark.django_db
def test_admin_list_view(admin_user):
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())

    # create 5 reviews for the product
    for _ in range(15):
        create_random_review_for_product(shop, product)

    client = Client()
    client.login(username=admin_user.username, password="password")

    reviews_list_url = reverse("shuup_admin:product_reviews.list")
    response = client.get(reviews_list_url, data={"jq": json.dumps({"perPage": 100, "page": 1})})
    assert response.status_code == 200
    data = json.loads(response.content)
    items = data["items"]
    assert len(items) == 15


@pytest.mark.django_db
def test_main_menu(admin_user):
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())

    # create 5 reviews for the product
    for _ in range(15):
        create_random_review_for_product(shop, product)

    client = Client()
    client.login(username=admin_user.username, password="password")

    response = client.get(reverse("shuup_admin:home"))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")
    assert "Product Reviews" in content
    assert reverse("shuup_admin:product_reviews.list") in content


@pytest.mark.django_db
def test_admin_mass_actions(rf, admin_user):
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())

    # create 5 reviews for the product
    for _ in range(15):
        create_random_review_for_product(shop, product)

    # we have 15 reviews
    assert ProductReview.objects.count() == 15
    assert ProductReview.objects.filter(status=ReviewStatus.APPROVED).count() == 15
    request = apply_request_middleware(rf.post("/"), user=admin_user)

    # reject all reviews
    RejectProductReviewMassAction().process(request, "all")
    assert ProductReview.objects.filter(status=ReviewStatus.REJECTED).count() == 15
    # approve all reviews
    ApproveProductReviewMassAction().process(request, "all")
    assert ProductReview.objects.filter(status=ReviewStatus.APPROVED).count() == 15

    # reject first 10 reviews
    RejectProductReviewMassAction().process(request, [r.pk for r in ProductReview.objects.all()[:10]])
    assert ProductReview.objects.filter(status=ReviewStatus.REJECTED).count() == 10
    assert ProductReview.objects.filter(status=ReviewStatus.APPROVED).count() == 5

    # approve first 3 reviews
    ApproveProductReviewMassAction().process(request, [r.pk for r in ProductReview.objects.all()[:3]])
    assert ProductReview.objects.filter(status=ReviewStatus.REJECTED).count() == 7
    assert ProductReview.objects.filter(status=ReviewStatus.APPROVED).count() == 8
