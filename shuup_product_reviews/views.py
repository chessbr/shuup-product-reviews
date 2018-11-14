# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.db.transaction import atomic
from django.views.generic import TemplateView

from shuup.core.models import Order, Product, ProductMode
from shuup.front.views.dashboard import DashboardViewMixin
from shuup_product_reviews.models import ProductReview


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
            order = Order.objects.complete().filter(
                shop=self.request.shop,
                customer__in=[self.request.customer, self.request.person],
                lines__product=data["product"]
            ).last()

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
        orders = Order.objects.complete().filter(
            shop=self.request.shop,
            customer__in=[self.request.customer, self.request.person]
        ).distinct()
        products = Product.objects.all_except_deleted(shop=self.request.shop).filter(
            order_lines__order__in=orders,
            mode__in=[ProductMode.NORMAL, ProductMode.VARIATION_CHILD]
        ).distinct()

        products_to_review = products.exclude(product_reviews__reviewer=self.request.person)
        context["reviews"] = ProductReview.objects.filter(
            reviewer=self.request.person,
            shop=self.request.shop
        )
        if products_to_review.exists():
            context["reviews_formset"] = ProductReviewModelFormset(
                form_kwargs=dict(request=self.request),
                initial=[dict(product=product) for product in products_to_review]
            )
        return context

    def post(self, request):
        formset = ProductReviewModelFormset(request.POST, form_kwargs=dict(request=self.request))
        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return self.get(request)
