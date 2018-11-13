# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client

from shuup.testing import factories
from shuup.themes.classic_gray.theme import ClassicGrayTheme
from shuup.xtheme._theme import get_current_theme, set_current_theme
from shuup.xtheme.layout import Layout
from shuup.xtheme.models import SavedViewConfig, SavedViewConfigStatus
from shuup_product_reviews.plugins import (
    ProductReviewCommentsPlugin, ProductReviewStarRatingsPlugin
)

from .factories import create_random_review_for_product


@pytest.mark.django_db
@pytest.mark.parametrize("show_recommenders,title", [
    (True, "My Title Here"),
    (False, "A new life")
])
def test_ratings_plugin(show_recommenders, title):
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())

    # create 15 reviews for the product
    [create_random_review_for_product(shop, product) for _ in range(15)]

    set_current_theme(ClassicGrayTheme.identifier, shop)
    svc = SavedViewConfig(
        theme_identifier=ClassicGrayTheme.identifier,
        shop=shop,
        view_name="ProductDetailView",
        status=SavedViewConfigStatus.CURRENT_DRAFT
    )
    layout = Layout(get_current_theme(shop), "product_extra_2")
    layout.add_plugin(ProductReviewStarRatingsPlugin.identifier, {
        "customer_ratings_title": {
            "en": title
        },
        "show_recommenders": show_recommenders
    })
    svc.set_layout_data(layout.placeholder_name, layout)
    svc.save()
    svc.publish()

    client = Client()
    response = client.get(reverse("shuup:product", kwargs=dict(pk=product.pk, slug=product.slug)))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")

    assert "product-reviews-rating-star" in content
    assert 'class="rating"' in content
    assert ('class="recommend"' in content) == show_recommenders
    assert title in content


@pytest.mark.django_db
@pytest.mark.parametrize("title", ["My Title Here", "A new life"])
def test_comments_plugin(title):
    shop = factories.get_default_shop()
    product = factories.create_product("product", shop=shop, supplier=factories.get_default_supplier())

    # create 15 reviews for the product
    [create_random_review_for_product(shop, product) for _ in range(15)]

    set_current_theme(ClassicGrayTheme.identifier, shop)
    svc = SavedViewConfig(
        theme_identifier=ClassicGrayTheme.identifier,
        shop=shop,
        view_name="ProductDetailView",
        status=SavedViewConfigStatus.CURRENT_DRAFT
    )
    layout = Layout(get_current_theme(shop), "product_bottom")
    layout.add_plugin(ProductReviewCommentsPlugin.identifier, {
        "title": {
            "en": title
        }
    })
    svc.set_layout_data(layout.placeholder_name, layout)
    svc.save()
    svc.publish()

    client = Client()
    response = client.get(reverse("shuup:product", kwargs=dict(pk=product.pk, slug=product.slug)))
    assert response.status_code == 200
    response.render()
    content = response.content.decode("utf-8")

    assert "product-review-comments" in content
    assert 'data-url="%s"' % reverse('shuup:product_review_comments', kwargs=dict(pk=product.pk)) in content
    assert 'data-title="%s"' % title in content
