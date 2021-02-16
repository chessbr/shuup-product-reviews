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
from shuup.front.admin_module.forms import BaseSettingsForm, BaseSettingsFormPart


def is_dashboard_enabled(shop):
    return configuration.get(shop, "show_vendor_reviews_on_dashboard", True)


def is_dashboard_menu_enabled(shop):
    return configuration.get(shop, "show_vendor_reviews_on_dashboard_menu", True)


def is_dashboard_with_options_enabled(shop):
    return configuration.get(shop, "show_vendor_reviews_with_options_on_dashboard", False)


def is_dashboard_menu_with_options_enabled(shop):
    return configuration.get(shop, "show_vendor_reviews_with_options_on_dashboard_menu", False)


class VendorReviewsSettingsForm(BaseSettingsForm):
    title = _("Vendor Reviews Settings")
    show_vendor_reviews_on_dashboard = forms.BooleanField(
        label=_("Show vendor reviews on dashboard"), required=False, initial=True
    )
    show_vendor_reviews_on_dashboard_menu = forms.BooleanField(
        label=_("Show vendor reviews on dashboard menu"), required=False, initial=True
    )


class VendorReviewsSettingsFormPart(BaseSettingsFormPart):
    form = VendorReviewsSettingsForm
    name = "vendor_reviews_settings"
    priority = 11


class VendorReviewsOptionSettingsForm(BaseSettingsForm):
    title = _("Vendor Reviews Option Settings")
    show_vendor_reviews_with_options_on_dashboard = forms.BooleanField(
        label=_("Show vendor reviews with options on dashboard"),
        required=False,
        initial=False,
    )
    show_vendor_reviews_with_options_on_dashboard_menu = forms.BooleanField(
        label=_("Show vendor reviews with option on dashboard menu"),
        required=False,
        initial=False,
    )


class VendorReviewsOptionSettingsFormPart(BaseSettingsFormPart):
    form = VendorReviewsOptionSettingsForm
    name = "vendor_reviews_options_settings"
    priority = 11
