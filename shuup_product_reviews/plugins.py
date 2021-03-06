# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup.xtheme import TemplatedPlugin
from shuup.xtheme.plugins.forms import TranslatableField

from shuup_product_reviews.models import ProductReview
from shuup_product_reviews.utils import (
    get_reviews_aggregation_for_product,
    get_stars_from_rating,
    is_product_valid_mode,
)


class ProductReviewStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.star_rating"
    name = _("Product Review Rating")
    template_name = "shuup_product_reviews/plugins/star_rating.jinja"
    required_context_variables = ["shop_product"]

    fields = [
        (
            "customer_ratings_title",
            TranslatableField(label=_("Customer ratings title"), required=False, initial=_("Customer Ratings:")),
        ),
        (
            "show_recommenders",
            forms.BooleanField(
                label=_("Show number of customers that recommend the product"),
                required=False,
                initial=False,
                help_text=_("Whether to show number of customers that recommend the product."),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        product = context["shop_product"].product

        if product and is_product_valid_mode(product):
            product_rating = get_reviews_aggregation_for_product(product)

            if product_rating["reviews"]:
                rating = product_rating["rating"]
                reviews = product_rating["reviews"]
                (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
                context.update(
                    {
                        "half_star": half_star,
                        "full_stars": full_stars,
                        "empty_stars": empty_stars,
                        "reviews": reviews,
                        "rating": rating,
                        "would_recommend": product_rating["would_recommend"],
                        "would_recommend_perc": product_rating["would_recommend"] / reviews,
                        "show_recommenders": self.config.get("show_recommenders", False),
                        "customer_ratings_title": self.get_translated_value("customer_ratings_title"),
                    }
                )

        return context


class ProductReviewCommentsPlugin(TemplatedPlugin):
    identifier = "shuup_product_reviews.review_comments"
    name = _("Product Review Comments")
    template_name = "shuup_product_reviews/plugins/reviews_comments.jinja"
    required_context_variables = ["shop_product"]

    fields = [
        ("title", TranslatableField(label=_("Title"), required=False, initial=_("Reviews"))),
        (
            "no_reviews_text",
            TranslatableField(label=_("No reviews text"), required=False, initial=_("The vendor has no reviews.")),
        ),
        (
            "load_more_text",
            TranslatableField(label=_("Load more reviews text"), required=False, initial=_("Load more comments")),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        product = context["shop_product"].product

        if product and is_product_valid_mode(product):
            product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
            reviews = ProductReview.objects.approved().filter(
                shop=context["request"].shop, product_id__in=product_ids, comment__isnull=False
            )
            if reviews.exists():
                context["review_product"] = product
                context["title"] = self.get_translated_value("title")
                context["no_reviews_text"] = self.get_translated_value("no_reviews_text")
                context["load_more_text"] = self.get_translated_value("load_more_text")

        return context
