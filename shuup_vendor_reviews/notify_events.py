# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _

from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Model, Phone


class VendorReviewCreated(Event):
    identifier = "vendor_review_created"
    name = _("Vendor Review Created")

    vendor_review = Variable(
        _("Vendor Review"), type=Model("shuup_vendor_reviews.VendorReview")
    )

    reviewer_email = Variable(_("Customer Email"), type=Email)
    reviewer_phone = Variable(_("Customer Phone"), type=Phone)

    shop_email = Variable(_("Shop Email"), type=Email)
    shop_phone = Variable(_("Shop Phone"), type=Phone)


def send_vendor_review_created_notification(vendor_review):
    reviewer = vendor_review.reviewer
    shop = vendor_review.shop

    params = dict(
        vendor_review=vendor_review,
        reviewer_email=reviewer.email,
        reviewer_phone=reviewer.phone,
        shop_email=shop.contact_address.email if shop.contact_address else "",
        shop_phone=shop.contact_address.phone if shop.contact_address else "",
    )

    VendorReviewCreated(**params).run(shop=shop)
