# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup_vendor_reviews"
    label = "shuup_vendor_reviews"
    verbose_name = "Shuup Vendor Reviews"
    provides = {
        "admin_module": [
            "shuup_vendor_reviews.admin_module.SupplierReviewsModule",
            "shuup_vendor_reviews.admin_module.SupplierReviewOptionsModule"
        ],
        "admin_shop_form_part": [
            "shuup_vendor_reviews.admin_module.dashboard.VendorReviewsSettingsFormPart",
            "shuup_vendor_reviews.admin_module.dashboard.VendorReviewsOptionSettingsFormPart",
        ],
        "xtheme_plugin": [
            "shuup_vendor_reviews.plugins.VendorReviewStarRatingsPlugin",
            "shuup_vendor_reviews.plugins.VendorReviewCommentsPlugin",
            "shuup_vendor_reviews.plugins.VendorReviewOptionStarRatingsPlugin",
            "shuup_vendor_reviews.plugins.VendorReviewOptionCommentsPlugin",
            "shuup_vendor_reviews.plugins.VendorReviewOptionTabs",
            "shuup_vendor_reviews.plugins.AverageOptionsRatingsPlugin",
            ],
        "customer_dashboard_items": [
            "shuup_vendor_reviews.dashboard_items:VendorReviewDashboardItem",
            "shuup_vendor_reviews.dashboard_items:VendorReviewWithOptionsDashboardItem"
        ],
        "front_urls": [
            "shuup_vendor_reviews.urls:urlpatterns"
        ],
        "xtheme_resource_injection": [
            "shuup_vendor_reviews.resources:add_resources"
        ],
        "notify_event": [
            "shuup_vendor_reviews.notify_events.VendorReviewCreated"
        ],
        "api_populator": [
            "shuup_vendor_reviews.api.populate_api"
        ]
    }

    def ready(self):
        # connect signals
        import shuup_vendor_reviews.signal_handlers  # noqa (C901)
