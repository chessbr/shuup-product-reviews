# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _

from shuup.front.utils.dashboard import DashboardItem
from shuup_vendor_reviews.models import VendorReview

from .admin_module.dashboard import (
    is_dashboard_enabled, is_dashboard_menu_enabled,
    is_dashboard_menu_with_options_enabled, is_dashboard_with_options_enabled
)


class VendorReviewDashboardItem(DashboardItem):
    template_name = "shuup_vendor_reviews/dashboard_item.jinja"
    title = _("Vendor Reviews")
    icon = "fa fa-star"
    view_text = _("Show all")
    _url = "shuup:vendor_reviews"

    def show_on_menu(self):
        return is_dashboard_menu_enabled(self.request.shop)

    def show_on_dashboard(self):
        return is_dashboard_enabled(self.request.shop)

    def get_context(self):
        context = super(VendorReviewDashboardItem, self).get_context()
        context["reviews"] = VendorReview.objects.for_reviewer(
            self.request.shop, self.request.person
        ).order_by("-created_on")[:5]
        return context


class VendorReviewWithOptionsDashboardItem(DashboardItem):
    template_name = "shuup_vendor_reviews/dashboard_item_with_options.jinja"
    title = _("Vendor Reviews")
    icon = "fa fa-star"
    view_text = _("Show all")
    _url = "shuup:vendor_reviews_options"

    def show_on_menu(self):
        return is_dashboard_menu_with_options_enabled(self.request.shop)

    def show_on_dashboard(self):
        return is_dashboard_with_options_enabled(self.request.shop)

    def get_context(self):
        context = super(VendorReviewWithOptionsDashboardItem, self).get_context()
        context["reviews"] = VendorReview.objects.for_reviewer(
            self.request.shop, self.request.person
        ).order_by("-created_on")[:5]
        return context
