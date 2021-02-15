# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.


def populate_api(router):
    """
    :param router: Router
    :type router: rest_framework.routers.DefaultRouter
    """
    from shuup_vendor_reviews.api.views import (
        ReviewViewSet, VendorReviewsViewSet
    )

    router.register("vendor-review/review", ReviewViewSet)
    router.register("vendor-review/reviews", VendorReviewsViewSet)
