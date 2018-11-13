# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import Avg, Count, QuerySet
from django.db.models.signals import post_delete, post_save
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _
from enumfields import Enum, EnumIntegerField

from shuup.core.fields import LanguageField


class ReviewStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3

    class Labels:
        PENDING = _("Pending")
        APPROVED = _("Approved")
        REJECTED = _("Rejected")


class ProductReviewQuerySet(QuerySet):
    def waiting_approval(self):
        return self.filter(status=ReviewStatus.PENDING)

    def approved(self):
        return self.filter(status=ReviewStatus.APPROVED)

    def rejected(self):
        return self.filter(status=ReviewStatus.REJECTED)


class ProductReview(models.Model):
    shop = models.ForeignKey("shuup.Shop", verbose_name=_("shop"), related_name="product_reviews")
    product = models.ForeignKey("shuup.Product", verbose_name=_("product"), related_name="product_reviews")
    reviewer = models.ForeignKey("shuup.Contact", verbose_name=_("reviewer"), related_name="product_reviews")
    order = models.ForeignKey("shuup.Order", verbose_name=_("order"), related_name="product_reviews")
    rating = models.PositiveIntegerField(verbose_name=_("rating"), db_index=True, validators=[MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True, verbose_name=_("comment"))
    would_recommend = models.BooleanField(
        default=False,
        verbose_name=_("Would recommend to a friend?"),
        help_text=_("Indicates whether you would recommend this product to a friend.")
    )
    language = LanguageField(verbose_name="language")
    status = EnumIntegerField(ReviewStatus, db_index=True, default=ReviewStatus.PENDING)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_on = models.DateTimeField(auto_now=True)

    objects = ProductReviewQuerySet.as_manager()

    class Meta:
        unique_together = ("reviewer", "product")

    def __str__(self):
        return "%s - %s" % (self.reviewer, self.rating)

    def approve(self):
        self.status = ReviewStatus.APPROVED
        self.save()

    def reject(self):
        self.status = ReviewStatus.REJECTED
        self.save()


class ProductReviewAggregation(models.Model):
    product = models.OneToOneField(
        "shuup.Product",
        verbose_name=_("product"),
        related_name="product_reviews_aggregation",
    )
    rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_("rating"), default=0)
    review_count = models.PositiveIntegerField(verbose_name=_("review count"), default=0)


def recalculate_aggregation(product):
    reviews = ProductReview.objects.filter(product=product, status=ReviewStatus.APPROVED)
    if not reviews.exists():
        return

    reviews_agg = ProductReview.objects.filter(product=product, status=ReviewStatus.APPROVED).aggregate(
        count=Count("pk"),
        rating=Avg("rating")
    )
    ProductReviewAggregation.objects.update_or_create(product=product, defaults=dict(
        review_count=reviews_agg["count"],
        rating=reviews_agg["rating"]
    ))


def handle_product_review_post_signal(sender, instance, **kwargs):
    recalculate_aggregation(instance.product)


post_delete.connect(handle_product_review_post_signal, sender=ProductReview)
post_save.connect(handle_product_review_post_signal, sender=ProductReview)
