# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.db.transaction import atomic
from django.http.response import JsonResponse
from django.views.generic import TemplateView, View

from shuup.core.models import Product
from shuup.front.views.dashboard import DashboardViewMixin
from shuup_product_reviews.models import ProductReview
from shuup_product_reviews.utils import (
    get_orders_for_review, get_pending_products_reviews
)


class ProductReviewForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    rating = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "rating-input"}), required=False)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(required=False)

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
                    would_recommend=data["would_recommend"]
                )
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
                initial=[dict(product=product) for product in pending_products_reviews]
            )
        return context

    def post(self, request):
        formset = ProductReviewModelFormset(request.POST, form_kwargs=dict(request=self.request))
        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return self.get(request)


class ProductReviewCommentsView(View):
    def get(self, request, *args, **kwargs):
        page = self.get_reviews_page()
        reviews = [
            {
                "id": review.pk,
                "date": review.created_on.isoformat(),
                "rating": review.rating,
                "comment": review.comment,
                "reviewer": review.reviewer.name,
            }
            for review in page.object_list
        ]

        next_page_url = None
        if page.has_next():
            next_page_url = "{}?page={}".format(
                reverse('shuup:product_review_comments', kwargs=dict(pk=self.kwargs["pk"])),
                page.number + 1
            )

        payload = {
            "reviews": reviews,
            "next_page_url": next_page_url,
        }
        return JsonResponse(payload)

    def get_reviews_page(self):
        product = Product.objects.filter(pk=self.kwargs["pk"], shop_products__shop=self.request.shop).first()
        queryset = ProductReview.objects.approved().filter(
            product=product,
            shop=self.request.shop,
        ).order_by("-created_on")

        paginator = Paginator(queryset, settings.PRODUCT_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get('page')

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
