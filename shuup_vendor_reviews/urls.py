# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shuup_vendor_reviews.views import (
    VendorReviewCommentsOptionsView,
    VendorReviewCommentsView,
    VendorReviewOptionsCommentsView,
    VendorReviewOptionsView,
    VendorReviewsView,
)

urlpatterns = [
    url(
        r"vendor_reviews_options/$",
        login_required(VendorReviewOptionsView.as_view()),
        name="vendor_reviews_options",
    ),
    url(
        r"vendor_reviews_options/(?P<pk>\d+)/comments/(?P<option_id>\d+)$",
        VendorReviewOptionsCommentsView.as_view(),
        name="vendor_review_options_comments",
    ),
    url(
        r"vendor_reviews/$",
        login_required(VendorReviewsView.as_view()),
        name="vendor_reviews",
    ),
    url(
        r"vendor_reviews/(?P<pk>\d+)/comments/$",
        VendorReviewCommentsView.as_view(),
        name="vendor_review_comments",
    ),
    url(
        r"vendor_reviews/(?P<pk>\d+)/comments/(?P<option>\d+)/$",
        VendorReviewCommentsOptionsView.as_view(),
        name="vendor_review_comments_options",
    ),
]
