# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from shuup import configuration
from shuup.core.models import ProductType
from shuup.front.admin_module.forms import BaseSettingsForm, BaseSettingsFormPart


def is_dashboard_enabled(shop):
    return configuration.get(shop, "show_product_reviews_on_dashboard", True)


def is_dashboard_menu_enabled(shop):
    return configuration.get(shop, "show_product_reviews_on_dashboard_menu", True)


class ProductReviewsSettingsForm(BaseSettingsForm):
    title = _("Product Reviews Settings")

    show_product_reviews_on_dashboard = forms.BooleanField(
        label=_("Show product reviews on dashboard"), required=False, initial=True
    )
    show_product_reviews_on_dashboard_menu = forms.BooleanField(
        label=_("Show product reviews on dashboard menu"), required=False, initial=True
    )
    product_review_ignore_product_types = forms.MultipleChoiceField(
        choices=[(product_type.pk, product_type.name) for product_type in ProductType.objects.all()],
        label=_("Product types to ignore"),
        help_text=_("Select all product types that should be ignored from reviews"),
        required=False,
    )


class ProductReviewsSettingsFormPart(BaseSettingsFormPart):
    form = ProductReviewsSettingsForm
    name = "product_reviews_settings"
    priority = 12
