# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from shuup.core.utils.static import get_shuup_static_url
from shuup.utils.djangoenv import has_installed
from shuup.xtheme.resources import add_resource


def add_resources(context, content):
    if has_installed("shuup_product_reviews"):
        return

    request = context.get("request")
    if request:
        match = request.resolver_match
        if match and match.app_name == "shuup_admin":
            return

    add_resource(
        context,
        "head_end",
        get_shuup_static_url("shuup_vendor_reviews/shuup_vendor_reviews.css", "shuup-vendor-reviews"),
    )
    add_resource(
        context,
        "body_end",
        get_shuup_static_url("shuup_vendor_reviews/shuup_vendor_reviews.js", "shuup-vendor-reviews"),
    )
