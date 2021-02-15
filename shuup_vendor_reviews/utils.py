# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import math
from django.db.models import Avg, Sum

from shuup.core import cache
from shuup.core.models import get_person_contact, Order, Supplier
from shuup_vendor_reviews.models import VendorReviewAggregation


def get_orders_for_review(request):
    """
    Returns an order queryset that contains all products that could be reviewed.
    It is basically any paid order.
    """
    return Order.objects.paid().filter(
        shop=request.shop,
        customer__in=set([
            customer
            for customer in [get_person_contact(request.user), request.customer, request.person]
            if customer
        ])
    )


def get_pending_vendors_reviews(request):
    return Supplier.objects.enabled().filter(shops=request.shop).filter(
        order_lines__order__in=get_orders_for_review(request)
    ).distinct()


def get_reviews_aggregation_for_supplier(supplier):
    return VendorReviewAggregation.objects.filter(supplier=supplier).aggregate(
        rating=Avg("rating"),
        reviews=Sum("review_count"),
        would_recommend=Sum("would_recommend")
    )


def get_reviews_aggregation_for_supplier_by_option(supplier, option):
    return VendorReviewAggregation.objects.filter(supplier=supplier, option=option).aggregate(
        rating=Avg("rating"),
        reviews=Sum("review_count"),
        would_recommend=Sum("would_recommend"),
    )


def get_stars_from_rating(rating):
    """
    Returns the number of full stars, empty stars and whether it has a half star
    """
    full_stars = math.floor(rating)
    empty_stars = math.floor(5 - rating)
    half_star = (full_stars + empty_stars) < 5
    return (full_stars, empty_stars, half_star)


def render_vendor_review_ratings(
        vendor, option=None, customer_ratings_title=None, show_recommenders=False, minified=False):
    """
    Render the star rating template for a given vendor and options.
    Returns None if no reviews exists for product
    """

    cached_star_rating = get_cached_star_rating(vendor.pk, (option.pk if option else ""))
    if cached_star_rating is not None:
        return cached_star_rating

    vendor_rating = get_reviews_aggregation_for_supplier(vendor)
    rating = vendor_rating["rating"]
    star_rating = None
    if rating:
        (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
        context = {
            "half_star": half_star,
            "full_stars": full_stars,
            "empty_stars": empty_stars,
            "reviews": vendor_rating["reviews"],
            "rating": rating,
            "customer_ratings_title": customer_ratings_title,
            "show_recommenders": show_recommenders,
            "minified": minified
        }
        from django.template import loader
        star_rating = loader.render_to_string("shuup_vendor_reviews/plugins/vendor_star_rating.jinja", context=context)

    if star_rating is not None:
        cache_star_rating(vendor.id, star_rating, (option.pk if option else ""))

    return star_rating or ""


def get_cached_star_rating(vendor_id, option_id=None):
    return cache.get("vendor_reviews_star_rating_{}_{}".format(
        vendor_id,
        (option_id or "")
        )
    )


def cache_star_rating(vendor_id, star_rating, option_id=None):
    key = "vendor_reviews_star_rating_{}_{}".format(
        vendor_id,
        (option_id or "")
        )

    cache.set(key, star_rating)


def bump_star_rating_cache(vendor_id, option_id=None):
    cache.bump_version("vendor_reviews_star_rating_{}_{}".format(
        vendor_id,
        (option_id or "")
        )
    )
