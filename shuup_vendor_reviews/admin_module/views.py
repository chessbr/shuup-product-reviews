# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.forms import ShuupAdminForm
from shuup.admin.shop_provider import get_shop
from shuup.admin.toolbar import get_default_edit_toolbar
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup_product_reviews.admin_module.base import BaseProductReviewListView
from shuup_vendor_reviews.models import VendorReview, VendorReviewOption


class VendorReviewListView(BaseProductReviewListView):
    model = VendorReview
    url_identifier = "vendor_reviews"

    default_columns = [
        Column(
            "supplier",
            _("Vendor"),
            filter_config=TextFilter(
                filter_field="supplier__name", placeholder=_("Filter by vendor...")
            ),
        ),
        Column(
            "option",
            _("Vendor Review Option"),
            filter_config=TextFilter(
                filter_field="option__name", placeholder=_("Filter by option...")
            ),
        ),
    ] + BaseProductReviewListView.default_columns

    mass_actions = [
        "shuup_vendor_reviews.admin_module.mass_actions.ApproveVendorReviewMassAction",
        "shuup_vendor_reviews.admin_module.mass_actions.RejectVendorReviewMassAction",
    ]

    def get_queryset(self):
        return VendorReview.objects.filter(shop=get_shop(self.request))


class VendorReviewOptionListView(PicotableListView):
    model = VendorReviewOption

    default_columns = [
        Column("name", _("Name"), linked=True, filter_config=TextFilter()),
    ]

    def get_queryset(self):
        return VendorReviewOption.objects.filter(shop=get_shop(self.request))


class VendorReviewOptionForm(ShuupAdminForm):
    class Meta:
        model = VendorReviewOption
        exclude = ("shop",)


class VendorReviewOptionEditView(CreateOrUpdateView):
    model = VendorReviewOption
    template_name = "shuup_vendor_reviews/vendor_review_option_edit.jinja"
    context_object_name = "vendor_review_option"
    form_class = VendorReviewOptionForm
    add_form_errors_as_messages = True

    def get_toolbar(self):
        save_form_id = self.get_save_form_id()
        delete_url = None
        option = self.get_object()
        if option and option.pk:
            delete_url = reverse(
                "shuup_admin:vendor_reviews_options.delete", kwargs={"pk": option.pk}
            )

        return get_default_edit_toolbar(self, save_form_id, delete_url=delete_url)

    def form_valid(self, form):
        form.instance.shop = self.request.shop
        return super(VendorReviewOptionEditView, self).form_valid(form)

    def get_success_url(self):
        return reverse("shuup_admin:vendor_reviews_options.list")


class VendorReviewOptionDeleteView(DetailView):
    model = VendorReviewOption
    context_object_name = "vendor_review_option"

    def get(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        option = self.get_object()
        name = force_text(option)
        option.delete()
        messages.success(request, _("%s has been deleted.") % name)
        return HttpResponseRedirect(reverse("shuup_admin:vendor_reviews_options.list"))
