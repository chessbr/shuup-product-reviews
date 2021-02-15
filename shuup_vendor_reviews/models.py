# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Case, Count, F, Sum, Value, When
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumIntegerField
from parler.models import TranslatableModel, TranslatedFields

from shuup.core.models import Supplier
from shuup_product_reviews.enums import ReviewStatus


class VendorReviewOption(TranslatableModel):
    shop = models.ForeignKey(
        "shuup.Shop",
        on_delete=models.CASCADE,
        verbose_name=_("shop"),
        related_name="supplier_reviews_option",
    )
    translations = TranslatedFields(
        name=models.CharField(
            max_length=255,
            blank=True,
            null=True,
        )
    )
    enabled = models.BooleanField(
        default=False,
        verbose_name=_("enabled"),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Vendor Review Option")
        verbose_name_plural = _("Vendor Review Options")


class VendorReviewQuerySet(models.QuerySet):
    def for_reviewer(self, shop, reviewer):
        return self.filter(shop=shop, reviewer=reviewer)

    def approved(self):
        return self.filter(status=ReviewStatus.APPROVED)

    def for_reviewer_dict_options(self, shop, reviewer):
        reviews = dict()
        suppliers = Supplier.objects.enabled().filter(
            supplier_reviews__reviewer=reviewer
        )

        for supplier in suppliers:
            reviews[supplier] = self.filter(
                shop=shop, reviewer=reviewer, supplier=supplier
            )

        return reviews

    def for_reviewer_by_option(self, shop, reviewer, option):
        return self.filter(shop=shop, reviewer=reviewer, option=option).order_by(
            "supplier"
        )

    def options_ratings(self):

        return (
            VendorReviewOption.objects.filter(vendor_review_options__in=self)
            .values("translations__name")
            .annotate(
                average=Avg("vendor_review_options__rating"),
                options_name=F("translations__name"),
            )
        )


class VendorReview(models.Model):
    shop = models.ForeignKey(
        "shuup.Shop",
        verbose_name=_("shop"),
        related_name="supplier_reviews",
        on_delete=models.CASCADE,
    )
    supplier = models.ForeignKey(
        "shuup.Supplier",
        verbose_name=_("supplier"),
        related_name="supplier_reviews",
        on_delete=models.CASCADE,
    )
    reviewer = models.ForeignKey(
        "shuup.Contact",
        verbose_name=_("reviewer"),
        related_name="supplier_reviews",
        on_delete=models.CASCADE,
    )
    rating = models.PositiveIntegerField(
        verbose_name=_("rating"),
        validators=[MaxValueValidator(5), MinValueValidator(1)],
    )
    comment = models.TextField(blank=True, null=True, verbose_name=_("comment"))
    would_recommend = models.BooleanField(
        default=False,
        verbose_name=_("Would recommend to a friend?"),
        help_text=_("Indicates whether you would recommend this product to a friend."),
    )
    status = EnumIntegerField(ReviewStatus, db_index=True, default=ReviewStatus.PENDING)
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_on = models.DateTimeField(auto_now=True)
    option = models.ForeignKey(
        VendorReviewOption,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vendor_review_options",
    )

    objects = VendorReviewQuerySet.as_manager()

    def __str__(self):
        return _("{option}Review for {supplier} by {reviewer_name}").format(
            option=(self.option.name + " " if self.option else ""),
            supplier=self.supplier,
            reviewer_name=self.reviewer.name,
        )

    def save(self, *args, **kwargs):
        super(VendorReview, self).save(*args, **kwargs)
        recalculate_aggregation(self.supplier, self.option)
        from shuup_vendor_reviews.utils import bump_star_rating_cache

        bump_star_rating_cache(
            self.supplier.pk, (self.option.pk if self.option else "")
        )

    def approve(self):
        self.status = ReviewStatus.APPROVED
        self.save()

    def reject(self):
        self.status = ReviewStatus.REJECTED
        self.save()


class VendorReviewAggregation(models.Model):
    supplier = models.ForeignKey(
        "shuup.Supplier",
        verbose_name=_("supplier"),
        related_name="supplier_reviews_aggregation",
        on_delete=models.CASCADE,
    )
    rating = models.DecimalField(
        max_digits=2, decimal_places=1, verbose_name=_("rating"), default=0
    )
    review_count = models.PositiveIntegerField(
        verbose_name=_("review count"), default=0
    )
    would_recommend = models.PositiveIntegerField(
        verbose_name=_("users would recommend"), default=0
    )
    option = models.ForeignKey(
        VendorReviewOption,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="vendor_review_agg_options",
    )

    def __str__(self):
        return "{option} VendorReviewAggregation for {supplier}".format(
            option=(self.option.name if self.option else ""),
            supplier=self.supplier.name,
        )

    class Meta:
        unique_together = ("supplier", "option")


def recalculate_aggregation_for_queryset(queryset):
    if not queryset.exists():
        # Make sure there is no aggregation since there is no approved reviews
        return

    return queryset.aggregate(
        count=Count("pk"),
        rating=Avg("rating"),
        would_recommend=Sum(
            Case(
                When(would_recommend=True, then=Value(1)),
                When(would_recommend=False, then=Value(0)),
                default=Value(0),
                output_field=models.PositiveIntegerField(),
            )
        ),
    )


def recalculate_aggregation(supplier, option):
    if not supplier:
        return

    reviews_agg = recalculate_aggregation_for_queryset(
        VendorReview.objects.filter(
            supplier=supplier, status=ReviewStatus.APPROVED, option=option
        )
    )
    if not reviews_agg:
        aggregation = VendorReviewAggregation.objects.filter(
            supplier=supplier, option=option
        ).first()
        if aggregation:
            aggregation.delete()
        return

    VendorReviewAggregation.objects.update_or_create(
        supplier=supplier,
        option=option,
        defaults=dict(
            review_count=reviews_agg["count"],
            rating=reviews_agg["rating"],
            would_recommend=reviews_agg["would_recommend"],
        ),
    )
