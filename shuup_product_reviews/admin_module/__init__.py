# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import PRODUCTS_MENU_CATEGORY
from shuup.admin.utils.permissions import get_default_model_permissions
from shuup.admin.utils.urls import derive_model_url, get_edit_and_list_urls, admin_url
from shuup_product_reviews.models import ProductReview


class ProductReviewsModule(AdminModule):
    name = _("Product Reviews")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:product_reviews.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^product_reviews",
            view_template="shuup_product_reviews.admin_module.views.ProductReview%sView",
            name_template="product_reviews.%s"
        ) + [
            admin_url(
                "^product_reviews/(?P<pk>\d+)/set-status/$",
                "shuup_product_reviews.admin_module.views.ProductReviewSetStatusView",
                name="product_reviews.set_status",
                permissions=get_default_model_permissions(ProductReview)
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-star",
                url="shuup_admin:product_reviews.list",
                category=PRODUCTS_MENU_CATEGORY,
                ordering=5
            )
        ]

    def get_required_permissions(self):
        return get_default_model_permissions(ProductReview)

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(ProductReview, "shuup_admin:product_reviews", object, kind)
