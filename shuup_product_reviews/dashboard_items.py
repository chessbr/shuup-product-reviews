# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _

from shuup.core.models import Order
from shuup.front.utils.dashboard import DashboardItem


class ProductReviewDashboardItem(DashboardItem):
    template_name = "shuup_product_reviews/dashboard_item.jinja"
    title = _("Reviews")
    icon = "fa fa-star"
    view_text = _("Show all")
    _url = "shuup:product_reviews"

    def get_context(self):
        context = super(ProductReviewDashboardItem, self).get_context()
        context["orders"] = Order.objects.filter(customer=self.request.customer, shop=self.request.shop)
        return context
