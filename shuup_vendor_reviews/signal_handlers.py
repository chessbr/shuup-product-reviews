# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.db.models.signals import post_save
from django.dispatch import receiver

from shuup.core.utils import context_cache
from shuup_vendor_reviews.models import VendorReview
from shuup_vendor_reviews.notify_events import (
    send_vendor_review_created_notification
)


@receiver(post_save, sender=VendorReview)
def on_vendor_review_created(sender, instance, created, **kwargs):
    if not created:
        return

    send_vendor_review_created_notification(instance)


@receiver(post_save, sender=VendorReview)
def bump_vendor_review_cache(sender, instance, created, **kwargs):
    from shuup_vendor_reviews.plugins import (
        get_vendor_options_ratings_cache_item
    )

    shop = instance.shop
    cache_item = get_vendor_options_ratings_cache_item(shop)
    context_cache.bump_cache_for_item(cache_item)
