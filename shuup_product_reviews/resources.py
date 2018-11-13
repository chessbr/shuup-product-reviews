# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.templatetags.static import static

from shuup.xtheme.resources import add_resource


def add_resources(context, content):
    request = context.get("request")
    if request:
        match = request.resolver_match
        if match and match.app_name == "shuup_admin":
            return

    add_resource(context, "head_end", static("shuup_product_reviews/shuup_product_reviews.css"))
    add_resource(context, "body_end", static("shuup_product_reviews/shuup_product_reviews.js"))
