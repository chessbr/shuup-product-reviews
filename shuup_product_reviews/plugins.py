# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import math

from django import forms
from django.utils.translation import ugettext_lazy as _

from shuup.core.models import ProductMode
from shuup.xtheme import TemplatedPlugin
from shuup.xtheme.plugins.forms import TranslatableField
from shuup_product_reviews.models import ProductReview
from shuup_product_reviews.utils import get_reviews_aggregation_for_product

ACCEPTED_PRODUCT_MODES = [
    ProductMode.NORMAL,
    ProductMode.SIMPLE_VARIATION_PARENT,
    ProductMode.VARIABLE_VARIATION_PARENT,
    ProductMode.VARIATION_CHILD
]


class ProductReviewStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.star_rating"
    name = _("Product Review Rating")
    template_name = "shuup_product_reviews/plugins/star_rating.jinja"

    fields = [
        ("customer_ratings_title", TranslatableField(
            label=_("Customer ratings title"),
            required=False,
            initial=_("Customer Ratings:")
        )),
        ("show_recommenders", forms.BooleanField(
            label=_("Show number of customers that recommend the product"),
            required=False,
            initial=False,
            help_text=_("Whether to show number of customer that recommends the product.")
        ))
    ]

    def is_context_valid(self, context):
        return bool(context.get("shop_product") or context.get("product"))

    def get_context_data(self, context):
        context = dict(context)
        product = None

        if context.get("shop_product"):
            product = context["shop_product"].product
        elif context.get("product"):
            product = context["product"]

        if product and product.mode in ACCEPTED_PRODUCT_MODES:
            product_rating = get_reviews_aggregation_for_product(product)

            if product_rating["reviews"]:
                rating = product_rating["rating"]
                reviews = product_rating["reviews"]
                full_stars = math.floor(rating)
                empty_stars = math.floor(5 - rating)
                half_star = (full_stars + empty_stars) < 5
                context.update({
                    "half_star": half_star,
                    "full_stars": int(full_stars),
                    "empty_stars": int(empty_stars),
                    "reviews": reviews,
                    "rating": rating,
                    "would_recommend": product_rating["would_recommend"],
                    "would_recommend_perc": product_rating["would_recommend"] / reviews,
                    "show_recommenders": self.config.get("show_recommenders", False),
                    "customer_ratings_title": self.get_translated_value("customer_ratings_title")
                })

        return context


class ProductReviewCommentsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.review_comments"
    name = _("Product Review Comments")
    template_name = "shuup_product_reviews/plugins/reviews_comments.jinja"

    def is_context_valid(self, context):
        return bool(context.get("shop_product") or context.get("product"))

    def get_context_data(self, context):
        context = dict(context)
        product = None

        if context.get("shop_product"):
            product = context["shop_product"].product
        elif context.get("product"):
            product = context["product"]

        if product and product.mode in ACCEPTED_PRODUCT_MODES:
            product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
            reviews = ProductReview.objects.approved().filter(
                shop=context["request"].shop,
                product_id__in=product_ids,
                comment__isnull=False
            )
            if reviews.exists():
                context["review_product"] = product

        return context
