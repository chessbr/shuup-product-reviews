# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import math

from django.db.models import Avg, Sum
from shuup import configuration
from shuup.core import cache
from shuup.core.models import Order, Product, ProductMode, get_person_contact

from shuup_product_reviews.models import ProductReviewAggregation

ACCEPTED_PRODUCT_MODES = [
    ProductMode.NORMAL,
    ProductMode.SIMPLE_VARIATION_PARENT,
    ProductMode.VARIABLE_VARIATION_PARENT,
    ProductMode.VARIATION_CHILD,
]


def get_ignored_product_types_ids(shop):
    return configuration.get(shop, "product_review_ignore_product_types") or []


def get_orders_for_review(request):
    """
    Returns an order queryset that contains all products that could be reviewed.
    It is basically any paid order.
    """
    return Order.objects.paid().filter(
        shop=request.shop,
        customer__in=set(
            [customer for customer in [get_person_contact(request.user), request.customer, request.person] if customer]
        ),
    )


def get_pending_products_reviews(request):
    """
    Returns a Product queryset that contains all products
    that can be reviewed by the current request shop and contact
    """
    ignored_product_types = get_ignored_product_types_ids(request.shop)

    products = (
        Product.objects.all_except_deleted(shop=request.shop)
        .filter(
            order_lines__order__in=get_orders_for_review(request),
            mode__in=[ProductMode.NORMAL, ProductMode.VARIATION_CHILD],
        )
        .distinct()
    )

    if ignored_product_types:
        products = products.exclude(type__in=ignored_product_types)

    return products.exclude(product_reviews__reviewer=request.person)


def is_product_valid_mode(product):
    """
    Check whether product mode is valid for having reviews attached
    """
    return product.mode in ACCEPTED_PRODUCT_MODES


def get_reviews_aggregation_for_product(product):
    """
    Calculate the reviews totals for a giving product
    """
    product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
    return ProductReviewAggregation.objects.filter(product_id__in=product_ids).aggregate(
        rating=Avg("rating"), reviews=Sum("review_count"), would_recommend=Sum("would_recommend")
    )


def get_stars_from_rating(rating):
    """
    Returns the number of full stars, empty stars and whether it has a half star
    """
    full_stars = math.floor(rating)
    empty_stars = math.floor(5 - rating)
    half_star = (full_stars + empty_stars) < 5
    return (full_stars, empty_stars, half_star)


def render_product_review_ratings(product, customer_ratings_title=None, show_recommenders=False, minified=False):
    """
    Render the star rating template for a given product and options.
    Returns None if no reviews exists for product
    """
    if is_product_valid_mode(product):
        cached_star_rating = get_cached_star_rating(product.pk)
        if cached_star_rating is not None:
            if cached_star_rating == -1:
                return ""
            return cached_star_rating

        product_rating = get_reviews_aggregation_for_product(product)
        rating = product_rating["rating"]
        star_rating = None
        if rating:
            (full_stars, empty_stars, half_star) = get_stars_from_rating(rating)
            context = {
                "half_star": half_star,
                "full_stars": full_stars,
                "empty_stars": empty_stars,
                "reviews": product_rating["reviews"],
                "rating": rating,
                "customer_ratings_title": customer_ratings_title,
                "show_recommenders": show_recommenders,
                "minified": minified,
            }
            from django.template import loader

            star_rating = loader.render_to_string("shuup_product_reviews/plugins/star_rating.jinja", context=context)

        # -1 is a flag that indicates that there is no content to render
        cache_star_rating(product.id, star_rating or -1)
        return star_rating or ""


def get_cached_star_rating(product_id):
    return cache.get("product_reviews_star_rating_{}".format(product_id))


def cache_star_rating(product_id, star_rating):
    cache.set("product_reviews_star_rating_{}".format(product_id), star_rating)


def bump_star_rating_cache(product_id):
    cache.bump_version("product_reviews_star_rating_{}".format(product_id))
