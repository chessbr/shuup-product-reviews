# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

import math

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from shuup.core.utils import context_cache
from shuup.xtheme import TemplatedPlugin
from shuup.xtheme.plugins.forms import GenericPluginForm, TranslatableField
from shuup.xtheme.plugins.widgets import XThemeSelect2ModelChoiceField, XThemeSelect2ModelMultipleChoiceField

from shuup_vendor_reviews.models import VendorReview, VendorReviewOption
from shuup_vendor_reviews.utils import (
    get_reviews_aggregation_for_supplier,
    get_reviews_aggregation_for_supplier_by_option,
    get_stars_from_rating,
)


class VendorReviewStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_vendor_reviews.star_rating"
    name = _("Vendor Review Rating")
    template_name = "shuup_vendor_reviews/plugins/vendor_star_rating.jinja"
    required_context_variables = ["supplier"]

    fields = [
        (
            "customer_ratings_title",
            TranslatableField(
                label=_("Customer ratings title"),
                required=False,
                initial=_("Customer Ratings:"),
            ),
        ),
        (
            "show_recommenders",
            forms.BooleanField(
                label=_("Show number of customers that recommend the vendor"),
                required=False,
                initial=False,
                help_text=_("Whether to show number of customers that recommend the vendor."),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]

        if supplier and supplier.enabled:
            supplier_rating = get_reviews_aggregation_for_supplier(supplier)
            if supplier_rating["reviews"]:
                rating = supplier_rating["rating"]
                reviews = supplier_rating["reviews"]
                (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
                context.update(
                    {
                        "half_star": half_star,
                        "full_stars": full_stars,
                        "empty_stars": empty_stars,
                        "reviews": reviews,
                        "rating": rating,
                        "would_recommend": supplier_rating["would_recommend"],
                        "would_recommend_perc": supplier_rating["would_recommend"] / reviews,
                        "show_recommenders": self.config.get("show_recommenders", False),
                        "customer_ratings_title": self.get_translated_value("customer_ratings_title"),
                    }
                )

        return context


class VendorReviewCommentsPlugin(TemplatedPlugin):
    identifier = "shuup_vendor_reviews.supplier_comments"
    name = _("Vendor Review Comments")
    template_name = "shuup_vendor_reviews/plugins/vendor_reviews_comments.jinja"
    required_context_variables = ["supplier"]

    fields = [
        (
            "title",
            TranslatableField(label=_("Title"), required=False, initial=_("Reviews")),
        ),
        (
            "no_reviews_text",
            TranslatableField(
                label=_("No reviews text"),
                required=False,
                initial=_("The vendor has no reviews."),
            ),
        ),
        (
            "load_more_text",
            TranslatableField(
                label=_("Load more reviews text"),
                required=False,
                initial=_("Load more comments"),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]

        if supplier and supplier.enabled:
            reviews = VendorReview.objects.approved().filter(
                shop=context["request"].shop, supplier=supplier, comment__isnull=False
            )
            if reviews.exists():
                context["review_supplier"] = supplier
                context["title"] = self.get_translated_value("title")
                context["no_reviews_text"] = self.get_translated_value("no_reviews_text")
                context["load_more_text"] = self.get_translated_value("load_more_text")

        return context


class VendorReviewOptionSelectionConfigForm(GenericPluginForm):
    """
    A configuration form for the VendorReviewOption plugins
    """

    def populate(self):
        """
        A custom populate method to display product choices
        """
        for field in self.plugin.fields:
            if isinstance(field, tuple):
                name, value = field
                value.initial = self.plugin.config.get(name, value.initial)
                self.fields[name] = value

        self.fields["vendor_review_option"] = XThemeSelect2ModelChoiceField(
            model="shuup_vendor_reviews.VendorReviewOption",
            label=_("Options"),
            help_text=_("Select the option you want to show"),
            required=True,
            initial=self.plugin.config.get("vendor_review_option"),
            extra_widget_attrs={"data-search-mode": "main"},
        )


class VendorReviewOptionStarRatingsPlugin(TemplatedPlugin):
    identifier = "shuup_vendor_reviews.option_star_rating"
    name = _("Vendor Review Option Rating")
    template_name = "shuup_vendor_reviews/plugins/vendor_star_option_rating.jinja"
    required_context_variables = ["supplier"]

    editor_form_class = VendorReviewOptionSelectionConfigForm

    fields = [
        (
            "customer_ratings_title",
            TranslatableField(
                label=_("Customer ratings title"),
                required=False,
                initial=_("Customer Ratings:"),
            ),
        ),
        (
            "show_recommenders",
            forms.BooleanField(
                label=_("Show number of customers that recommend the vendor"),
                required=False,
                initial=False,
                help_text=_("Whether to show number of customers that recommend the vendor."),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]
        ratings = dict()
        option_id = self.config.get("vendor_review_option")
        context["vendor_review_option"] = option_id

        if supplier and supplier.enabled and option_id:
            option = VendorReviewOption.objects.get(pk=option_id)
            supplier_rating = get_reviews_aggregation_for_supplier_by_option(supplier, option)
            if supplier_rating["reviews"]:
                rating = supplier_rating["rating"]
                reviews = supplier_rating["reviews"]
                (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
                ratings.update(
                    {
                        option: {
                            "half_star": half_star,
                            "full_stars": full_stars,
                            "empty_stars": empty_stars,
                            "reviews": reviews,
                            "rating": rating,
                            "would_recommend": supplier_rating["would_recommend"],
                            "would_recommend_perc": supplier_rating["would_recommend"] / reviews,
                            "show_recommenders": self.config.get("show_recommenders", False),
                            "customer_ratings_title": self.get_translated_value("customer_ratings_title"),
                        }
                    }
                )
            context.update({"ratings": ratings})
        return context


class VendorReviewOptionCommentsPlugin(TemplatedPlugin):
    identifier = "shuup_vendor_option_reviews.supplier_comments"
    name = _("Vendor Review Option Comments")
    template_name = "shuup_vendor_reviews/plugins/vendor_reviews_option_comments.jinja"
    required_context_variables = ["supplier"]
    editor_form_class = VendorReviewOptionSelectionConfigForm

    fields = [
        (
            "title",
            TranslatableField(label=_("Title"), required=False, initial=_("Reviews")),
        ),
        (
            "no_reviews_text",
            TranslatableField(
                label=_("No reviews text"),
                required=False,
                initial=_("The vendor has no reviews."),
            ),
        ),
        (
            "load_more_text",
            TranslatableField(
                label=_("Load more reviews text"),
                required=False,
                initial=_("Load more comments"),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]
        option_id = self.config.get("vendor_review_option")

        if supplier and supplier.enabled and option_id:
            reviews = VendorReview.objects.approved().filter(
                shop=context["request"].shop,
                supplier=supplier,
                comment__isnull=False,
                option_id=option_id,
            )

            if reviews.exists():
                context["review_supplier"] = supplier
                context["option"] = option_id
                context["title"] = self.get_translated_value("title")
                context["no_reviews_text"] = self.get_translated_value("no_reviews_text")
                context["load_more_text"] = self.get_translated_value("load_more_text")

        return context


class VendorReviewOptionTabsSelectionConfigForm(GenericPluginForm):
    def populate(self):
        for field in self.plugin.fields:
            if isinstance(field, tuple):
                name, value = field
                value.initial = self.plugin.config.get(name, value.initial)
                self.fields[name] = value

        self.fields["vendor_review_options"] = XThemeSelect2ModelMultipleChoiceField(
            model="shuup_vendor_reviews.VendorReviewOption",
            label=_("Options"),
            help_text=_("Select the options you want to show"),
            required=True,
            initial=self.plugin.config.get("vendor_review_options"),
            extra_widget_attrs={"data-search-mode": "main"},
        )


class VendorReviewOptionTabs(TemplatedPlugin):
    identifier = "shuup_vendor_reviews.option_reviews_tabs"
    name = _("Vendor Review Options Tabs")
    template_name = "shuup_vendor_reviews/plugins/vendor_reviews_option_tabs.jinja"
    required_context_variables = ["supplier"]

    editor_form_class = VendorReviewOptionTabsSelectionConfigForm

    fields = [
        (
            "main_title",
            TranslatableField(label=_("Main title"), required=False, initial=_("Reviews")),
        ),
        (
            "show_recommenders",
            forms.BooleanField(
                label=_("Show number of customers that recommend the vendor"),
                required=False,
                initial=False,
                help_text=_("Whether to show number of customers that recommend the vendor."),
            ),
        ),
        (
            "no_reviews_text",
            TranslatableField(
                label=_("No reviews text"),
                required=False,
                initial=_("The vendor has no reviews."),
            ),
        ),
        (
            "load_more_text",
            TranslatableField(
                label=_("Load more reviews text"),
                required=False,
                initial=_("Load more comments"),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]
        ratings = dict()
        options_id = self.config.get("vendor_review_options")

        context["vendor_review_options"] = options_id
        if supplier and supplier.enabled:

            if options_id:
                options = VendorReviewOption.objects.filter(pk__in=options_id)
            else:
                options = VendorReviewOption.objects.none()

            for option in options:
                supplier_rating = get_reviews_aggregation_for_supplier_by_option(supplier, option)

                if supplier_rating["reviews"]:
                    rating = supplier_rating["rating"]
                    rating_reviews = supplier_rating["reviews"]
                    (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)

                    ratings.update(
                        {
                            option: {
                                "half_star": half_star,
                                "full_stars": full_stars,
                                "empty_stars": empty_stars,
                                "reviews": rating_reviews,
                                "rating": rating,
                                "would_recommend": supplier_rating["would_recommend"],
                                "would_recommend_perc": supplier_rating["would_recommend"] / rating_reviews,
                                "show_recommenders": self.config.get("show_recommenders", False),
                                "option": option,
                                "load_more_text": self.get_translated_value("load_more_text"),
                            }
                        }
                    )

            context["no_reviews_text"] = self.get_translated_value("no_reviews_text")
            context["main_title"] = self.get_translated_value("main_title")
            context["options"] = options
            context.update({"ratings": ratings})
        return context


VENDOR_OPTIONS_RATINGS_CACHE_ITEM_FMT = "vendor_options_ratings-{shop_id}"


def get_vendor_options_ratings_cache_item(shop):
    shop_id = shop.id if hasattr(shop, "pk") else shop
    return VENDOR_OPTIONS_RATINGS_CACHE_ITEM_FMT.format(shop_id=shop_id)


class AverageOptionsRatingsPlugin(TemplatedPlugin):
    identifier = "averaged_options_ratings"
    name = _("Average Options Ratings")
    template_name = "shuup_vendor_reviews/plugins/vendor_average_options_ratings.jinja"
    required_context_variables = ["supplier"]

    fields = [
        (
            "customer_ratings_title",
            TranslatableField(
                label=_("Customer ratings title"),
                required=False,
                initial=_("Customer Ratings:"),
            ),
        ),
        (
            "show_recommenders",
            forms.BooleanField(
                label=_("Show number of customers that recommend the vendor"),
                required=False,
                initial=False,
                help_text=_("Whether to show number of customers that recommend the vendor."),
            ),
        ),
    ]

    def get_context_data(self, context):
        context = dict(context)
        supplier = context["supplier"]
        request = context["request"]
        if supplier and supplier.enabled:
            supplier_rating = get_reviews_aggregation_for_supplier(supplier)

            if supplier_rating["reviews"]:
                reviews = supplier_rating["reviews"]

                key, options_ratings = context_cache.get_cached_value(
                    identifier="vendor_options_ratings_%s" % (supplier.pk if supplier else ""),
                    item=get_vendor_options_ratings_cache_item(request.shop),
                    context=request,
                )

                if not options_ratings:
                    options_ratings = supplier.supplier_reviews.options_ratings()
                    context_cache.set_cached_value(
                        key,
                        options_ratings,
                        settings.SHUUP_TEMPLATE_HELPERS_CACHE_DURATION,
                    )

                for option_rating in options_ratings:
                    frac, whole = math.modf(option_rating["average"])
                    option_rating["full_stars"] = int(whole)
                    option_rating["half_stars"] = int(math.ceil(frac))
                    option_rating["empty_stars"] = 5 - option_rating["full_stars"] - option_rating["half_stars"]

                context.update(
                    {
                        "reviews": reviews,
                        "options_ratings": options_ratings,
                        "would_recommend": supplier_rating["would_recommend"],
                        "would_recommend_perc": supplier_rating["would_recommend"] / reviews,
                        "show_recommenders": self.config.get("show_recommenders", False),
                        "customer_ratings_title": self.get_translated_value("customer_ratings_title"),
                    }
                )

        return context
