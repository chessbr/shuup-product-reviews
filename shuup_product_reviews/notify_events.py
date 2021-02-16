# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Language, Model, Phone


class ProductReviewCreated(Event):
    identifier = "product_review_created"
    name = _("Product Review Created")

    product_review = Variable(_("Product Review"), type=Model("shuup_product_reviews.ProductReview"))

    reviewer_email = Variable(_("Customer Email"), type=Email)
    reviewer_phone = Variable(_("Customer Phone"), type=Phone)

    shop_email = Variable(_("Shop Email"), type=Email)
    shop_phone = Variable(_("Shop Phone"), type=Phone)

    language = Variable(_("Language"), type=Language)


def send_product_review_created_notification(product_review):
    reviewer = product_review.reviewer
    shop = product_review.shop

    params = dict(
        product_review=product_review,
        reviewer_email=reviewer.email,
        reviewer_phone=reviewer.phone,
        shop_email=shop.contact_address.email if shop.contact_address else "",
        shop_phone=shop.contact_address.phone if shop.contact_address else "",
        language=product_review.order.language,
    )

    ProductReviewCreated(**params).run(shop=shop)
