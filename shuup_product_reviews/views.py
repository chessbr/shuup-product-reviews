# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.views.generic import TemplateView

from shuup.core.models import Order, Product
from shuup_product_reviews.models import ProductReview
from shuup.front.views.dashboard import DashboardViewMixin
from django import forms


class ProductReviewForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.HiddenInput())
    rating = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "rating-input"}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(required=False)


class ProductReviewsView(DashboardViewMixin, TemplateView):
    template_name = "shuup_product_reviews/product_reviews.jinja"

    def get_context_data(self, **kwargs):
        context = super(ProductReviewsView, self).get_context_data(**kwargs)
        orders = Order.objects.complete().filter(
            shop=self.request.shop,
            customer__in=[self.request.customer, self.request.person]
        )
        products = Product.objects.filter(order_lines__order__in=orders).distinct()

        products_to_review = products.filter(product_reviews__isnull=True)
        context["reviews"] = ProductReview.objects.filter(
            reviewer=self.request.person,
            shop=self.request.shop
        )
        if products_to_review.exists():
            ProductReviewModelFormset = forms.formset_factory(ProductReviewForm, extra=0)
            context["reviews_formset"] = ProductReviewModelFormset(
                initial=[dict(product=product) for product in products_to_review]
            )

        return context

    def post(self, request):
        return self.get(request)
