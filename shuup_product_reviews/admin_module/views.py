# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import Column, TextFilter

from shuup_product_reviews.models import ProductReview

from .base import BaseProductReviewListView


class ProductReviewListView(BaseProductReviewListView):
    model = ProductReview
    url_identifier = "product_reviews"

    default_columns = [
        Column(
            "product",
            _("Product"),
            filter_config=TextFilter(filter_field="product__translations__name", placeholder=_("Filter by product...")),
        )
    ] + BaseProductReviewListView.default_columns

    mass_actions = [
        "shuup_product_reviews.admin_module.mass_actions.ApproveProductReviewMassAction",
        "shuup_product_reviews.admin_module.mass_actions.RejectProductReviewMassAction",
    ]

    def get_queryset(self):
        return ProductReview.objects.filter(shop=get_shop(self.request))
