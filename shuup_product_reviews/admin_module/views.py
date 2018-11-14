# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import BaseDetailView

from shuup.admin.shop_provider import get_shop
from shuup.admin.toolbar import PostActionButton, Toolbar
from shuup.admin.utils.picotable import ChoicesFilter, Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.core.models import Contact, Order, Product
from shuup_product_reviews.models import ProductReview, ReviewStatus


class ProductReviewListView(PicotableListView):
    model = ProductReview
    url_identifier = "product_reviews"

    default_columns = [
        Column(
            "product",
            _("Product"),
            filter_config=TextFilter(
                filter_field="product__translations__name",
                placeholder=_("Filter by product...")
            )
        ),
        Column(
            "reviewer__name",
            _("Reviewer"),
            filter_config=TextFilter(filter_field="reviewer__name")
        ),
        Column("rating", _("Rating")),
        Column("comment", _("Comment")),
        Column(
            "status",
            _("Status"),
            filter_config=ChoicesFilter(
                choices=ReviewStatus.choices(),
                filter_field="reviewer__name"
            )
        )
    ]

    mass_actions = [
        "shuup_product_reviews.admin_module.mass_actions.ApproveProductReviewMassAction",
        "shuup_product_reviews.admin_module.mass_actions.RejectProductReviewMassAction"
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
            self.fields.pop("order")
        else:
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

    def get_queryset(self):
        return ProductReview.objects.filter(shop=get_shop(self.request))

    def get_toolbar(self):
        if self.object and self.object.pk:
            toolbar = Toolbar.for_view(self)

            if self.object.status != ReviewStatus.APPROVED:
                toolbar.append(
                    PostActionButton(
                        post_url=reverse("shuup_admin:product_reviews.set_status", kwargs={"pk": self.object.pk}),
                        name="status",
                        value=ReviewStatus.APPROVED.value,
                        icon="fa fa-check",
                        text=_("Approve"),
                        extra_css_class="btn-outline-success"
                    )
                )

            elif self.object.status != ReviewStatus.REJECTED:
                toolbar.append(
                    PostActionButton(
                        post_url=reverse("shuup_admin:product_reviews.set_status", kwargs={"pk": self.object.pk}),
                        name="status",
                        value=ReviewStatus.REJECTED.value,
                        icon="fa fa-close",
                        text=_("Reject"),
                        extra_css_class="btn-outline-danger"
                    )
                )
            return toolbar
        else:
            return super(ProductReviewEditView, self).get_toolbar()


class ProductReviewSetStatusView(BaseDetailView):
    model = ProductReview
    form_class = ProductReviewForm
    context_object_name = "product_review"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("shuup_admin:product_reviews.edit", kwargs={"pk": kwargs.get("pk")}))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            new_status = int(request.POST.get("status"))
        except ValueError:
            messages.error(request, _("Invalid status"))
            return self.get(request, *args, **kwargs)

        if new_status not in [choice[0] for choice in ReviewStatus.choices()]:
            messages.error(request, _("Invalid status"))
            return self.get(request, *args, **kwargs)

        self.object.status = new_status
        self.object.save()
        messages.success(request, _("Status changed succefully!"))
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        return ProductReview.objects.filter(shop=get_shop(self.request))
