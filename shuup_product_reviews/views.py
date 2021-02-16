# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.transaction import atomic
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from shuup.core.models import Product
from shuup.front.views.dashboard import DashboardViewMixin

from shuup_product_reviews.models import ProductReview
from shuup_product_reviews.utils import get_orders_for_review, get_pending_products_reviews

from .base import BaseCommentsView


class ProductReviewForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "rating-input"}), max_value=5, min_value=1, required=False
    )
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(required=False, label=_("I would recommend this to a friend"))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ProductReviewForm, self).__init__(*args, **kwargs)

    def save(self):
        data = self.cleaned_data
        if data.get("rating"):
            # fetch the last order that this product was bought
            order = get_orders_for_review(self.request).filter(lines__product=data["product"]).last()
            ProductReview.objects.get_or_create(
                product=data["product"],
                reviewer=self.request.person,
                defaults=dict(
                    shop=self.request.shop,
                    order=order,
                    rating=data["rating"],
                    comment=data["comment"],
                    would_recommend=data["would_recommend"],
                ),
            )


ProductReviewModelFormset = forms.formset_factory(ProductReviewForm, extra=0)


class ProductReviewsView(DashboardViewMixin, TemplateView):
    template_name = "shuup_product_reviews/product_reviews.jinja"

    def get_context_data(self, **kwargs):
        context = super(ProductReviewsView, self).get_context_data(**kwargs)
        pending_products_reviews = get_pending_products_reviews(self.request)
        context["reviews"] = ProductReview.objects.for_reviewer(self.request.shop, self.request.person)

        if pending_products_reviews.exists():
            context["reviews_formset"] = ProductReviewModelFormset(
                form_kwargs=dict(request=self.request),
                initial=[dict(product=product) for product in pending_products_reviews],
            )
        return context

    def post(self, request):
        formset = ProductReviewModelFormset(request.POST, form_kwargs=dict(request=self.request))
        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return HttpResponseRedirect(reverse("shuup:product_reviews"))


class ProductReviewCommentsView(BaseCommentsView):
    view_name = "product_review_comments"

    def get_reviews_page(self):
        product = Product.objects.filter(pk=self.kwargs["pk"], shop_products__shop=self.request.shop).first()
        product_ids = [product.pk] + list(product.variation_children.values_list("pk", flat=True))
        queryset = (
            ProductReview.objects.approved()
            .filter(product__id__in=product_ids, shop=self.request.shop, comment__isnull=False)
            .order_by("-created_on")
        )

        paginator = Paginator(queryset, settings.PRODUCT_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get("page")

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
