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

from shuup.xtheme import TemplatedPlugin
from shuup_product_reviews.models import ProductReviewAggregation


class ProductReviewStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.star_rating"
    name = _("Product Reviews Star Rating")
    template_name = "shuup_product_reviews/plugins/star_rating.jinja"
    required_context_variables = ["shop_product"]

    fields = [
        ("show_customer_rating_label", forms.BooleanField(
            label=_("Show customer rating label"),
            required=False, initial=True
        ))
    ]

    def get_context_data(self, context):
        context = super(ProductReviewStarRatingsPlugin, self).get_context_data(context)

        if context.get("shop_product"):
            product_rating = ProductReviewAggregation.objects.filter(
                product_id=context["shop_product"].product_id
            ).first()

            if product_rating:
                full_stars = math.floor(product_rating.rating)
                empty_stars = math.floor(5 - product_rating.rating)
                half_star = (full_stars + empty_stars) < 5
                context.update({
                    "half_star": half_star,
                    "full_stars": int(full_stars),
                    "empty_stars": int(empty_stars),
                    "product_rating": product_rating,
                    "show_customer_rating_label": self.config.get("show_customer_rating_label", False)
                })

        return context
