# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import PicotableMassAction
from six import string_types

from shuup_vendor_reviews.models import VendorReview


class ApproveVendorReviewMassAction(PicotableMassAction):
    label = _("Approve reviews")
    identifier = "mass_action_approve_vendor_reviews"

    def process(self, request, ids):
        query = Q(shop=get_shop(request))

        if not (isinstance(ids, string_types) and ids == "all"):
            query &= Q(id__in=ids)

        for vendor_review in VendorReview.objects.only("pk").filter(query):
            vendor_review.approve()


class RejectVendorReviewMassAction(PicotableMassAction):
    label = _("Reject reviews")
    identifier = "mass_action_reject_vendor_reviews"

    def process(self, request, ids):
        query = Q(shop=get_shop(request))

        if not (isinstance(ids, string_types) and ids == "all"):
            query &= Q(id__in=ids)

        for vendor_review in VendorReview.objects.only("pk").filter(query):
            vendor_review.reject()
