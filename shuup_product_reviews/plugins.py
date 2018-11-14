# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import math

from django.db.models import Avg, Count, Sum
from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup.core.models import ProductMode

from shuup.xtheme import TemplatedPlugin
from shuup_product_reviews.models import ProductReviewAggregation


class ProductReviewStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.star_rating"
    name = _("Product Reviews Star Rating")
    template_name = "shuup_product_reviews/plugins/star_rating.jinja"

    fields = [
        ("show_customer_rating_label", forms.BooleanField(
            label=_("Show customer rating label"),
            required=False, initial=True
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

        modes = [
            ProductMode.NORMAL,
            ProductMode.SIMPLE_VARIATION_PARENT,
            ProductMode.VARIABLE_VARIATION_PARENT,
            ProductMode.VARIATION_CHILD
        ]
        if product and product.mode in modes:
            product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
            product_rating = ProductReviewAggregation.objects.filter(product_id__in=product_ids).aggregate(
                rating=Avg("rating"),
                reviews=Sum("review_count"),
                would_recommend=Sum("would_recommend")
            )

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
                    "would_recommend": product_rating["would_recommend"] / reviews,
                    "show_customer_rating_label": self.config.get("show_customer_rating_label", False)
                })

        return context
