# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import Column
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup_product_reviews.models import ProductReview
from shuup.core.models import Contact, Product, Order
from shuup.admin.utils.picotable import TextFilter


class ProductReviewListView(PicotableListView):
    model = ProductReview
    url_identifier = "product_reviews"

    default_columns = [
        Column("product", _("Product"), ),
        Column("reviewer__name", _("Reviewer"), filter_config=TextFilter(filter_field="reviewer__name")),
        Column("rating", _("Rating")),
        Column("comment", _("Comment")),
        Column("status", _("Status")),
    ]

    def get_queryset(self):
        return ProductReview.objects.filter(shop=get_shop(self.request))


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        exclude = ("shop",)

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request")
        super(ProductReviewForm, self).__init__(**kwargs)
        shop = get_shop(self.request)

        if self.instance.pk:
            self.fields.pop("reviewer")
            self.fields.pop("product")
            self.fields.pop("rating")
            self.fields.pop("comment")
            self.fields.pop("language")
            self.fields.pop("order")
        else:
            self.fields["language"].choices = settings.LANGUAGES
            self.fields["reviewer"].queryset = Contact.objects.filter(shops=shop)
            self.fields["product"].queryset = Product.objects.filter(shop_products__shop=shop)
            self.fields["order"].queryset = Order.objects.filter(shop=shop)

    def save(self, *args, **kwargs):
        self.instance.shop = get_shop(self.request)
        return super().save(*args, **kwargs)


class ProductReviewEditView(CreateOrUpdateView):
    model = ProductReview
    form_class = ProductReviewForm
    template_name = "shuup_product_reviews/admin/edit_product_reviews.jinja"
    context_object_name = "product_review"

    def get_form_kwargs(self):
        kwargs = super(ProductReviewEditView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs
