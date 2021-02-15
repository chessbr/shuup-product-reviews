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
from django.forms import BaseFormSet
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View

from shuup.core.models import Supplier
from shuup.front.views.dashboard import DashboardViewMixin
from shuup.utils.form_group import FormGroup
from shuup_product_reviews.base import BaseCommentsView
from shuup_product_reviews.enums import ReviewStatus
from shuup_vendor_reviews.models import VendorReview, VendorReviewOption
from shuup_vendor_reviews.utils import get_pending_vendors_reviews


class VendorReviewForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(), widget=forms.HiddenInput()
    )
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "rating-input"}),
        max_value=5,
        min_value=1,
        required=False,
    )
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(
        required=False, label=_("I would recommend this to a friend")
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(VendorReviewForm, self).__init__(*args, **kwargs)

    def save(self):
        data = self.cleaned_data
        if data.get("rating"):
            VendorReview.objects.update_or_create(
                supplier=data["supplier"],
                reviewer=self.request.person,
                shop=self.request.shop,
                defaults=dict(
                    rating=data["rating"],
                    comment=data["comment"],
                    would_recommend=data["would_recommend"],
                    status=ReviewStatus.PENDING,
                ),
            )


VendorReviewModelFormset = forms.formset_factory(VendorReviewForm, extra=0)


class VendorReviewsView(DashboardViewMixin, TemplateView):
    template_name = "shuup_vendor_reviews/vendor_reviews.jinja"

    def get_context_data(self, **kwargs):
        context = super(VendorReviewsView, self).get_context_data(**kwargs)
        pending_suppliers_reviews = get_pending_vendors_reviews(self.request)
        context["reviews"] = VendorReview.objects.for_reviewer(
            self.request.shop, self.request.person
        )

        if pending_suppliers_reviews.exists():
            initial_values = [
                dict(supplier=supplier) for supplier in pending_suppliers_reviews
            ]
            context["reviews_formset"] = VendorReviewModelFormset(
                form_kwargs=dict(request=self.request), initial=initial_values
            )

        return context

    def post(self, request):
        formset = VendorReviewModelFormset(
            request.POST, form_kwargs=dict(request=self.request)
        )
        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return HttpResponseRedirect(reverse("shuup:vendor_reviews"))


class VendorReviewCommentsView(BaseCommentsView):
    view_name = "vendor_review_comments"

    def get_reviews_page(self):
        supplier = Supplier.objects.filter(
            pk=self.kwargs["pk"], shops=self.request.shop
        ).first()
        queryset = (
            VendorReview.objects.approved()
            .filter(supplier=supplier, shop=self.request.shop, comment__isnull=False)
            .order_by("-created_on")
        )

        paginator = Paginator(queryset, settings.VENDOR_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get("page")

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)


class VendorReviewOptionForm(forms.Form):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(), widget=forms.HiddenInput()
    )
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "rating-input"}),
        max_value=5,
        min_value=1,
        required=False,
    )
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2)))
    would_recommend = forms.BooleanField(
        required=False, label=_("I would recommend this to a friend")
    )
    option = forms.ModelChoiceField(
        queryset=VendorReviewOption.objects.all(), widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.option = kwargs.pop("option")
        self.supplier = kwargs.pop("supplier")
        review = VendorReview.objects.filter(
            reviewer=self.request.person, supplier=self.supplier, option=self.option
        ).first()

        super(VendorReviewOptionForm, self).__init__(*args, **kwargs)

        if review:
            self.fields["rating"].initial = review.rating
            self.fields["comment"].initial = review.comment
            self.fields["would_recommend"].initial = review.would_recommend
            self.fields["supplier"].initial = review.supplier
            self.fields["option"].initial = review.option
        else:
            self.fields["supplier"].initial = self.supplier
            self.fields["option"].initial = self.option

    def save(self):
        data = self.cleaned_data

        if data.get("rating"):
            review, created = VendorReview.objects.update_or_create(
                supplier=data["supplier"],
                reviewer=self.request.person,
                shop=self.request.shop,
                option=data["option"],
                defaults=dict(
                    rating=data["rating"],
                    comment=data["comment"],
                    would_recommend=data["would_recommend"],
                    status=ReviewStatus.PENDING,
                ),
            )


class VendorReviewGroupForm(FormGroup):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.options = kwargs.pop("options", None)
        self.error_class = kwargs.pop("error_class", None)
        self.use_required_attribute = kwargs.pop("use_required_attribute", None)
        initial = kwargs.get("initial", None)
        if initial:
            self.supplier = initial.get("supplier", None)
        else:
            self.supplier = None

        super(VendorReviewGroupForm, self).__init__(*args, **kwargs)

        for option in self.options:
            self.add_form_def(
                name=option,
                form_class=VendorReviewOptionForm,
                kwargs={
                    "request": self.request,
                    "option": option,
                    "supplier": self.supplier,
                },
            )

    def save(self, **kwargs):
        for form in self.forms:
            self.forms[form].save()


class VendorReviewGroupFormset(BaseFormSet):
    def full_clean(self):
        for form in self.forms:
            form.full_clean()


VendorReviewGroupModelFormset = forms.formset_factory(
    VendorReviewGroupForm, extra=0, formset=VendorReviewGroupFormset
)


class VendorReviewOptionsView(DashboardViewMixin, TemplateView):
    template_name = "shuup_vendor_reviews/vendor_review_options.jinja"

    def get_context_data(self, **kwargs):
        context = super(VendorReviewOptionsView, self).get_context_data(**kwargs)
        pending_suppliers_reviews = get_pending_vendors_reviews(self.request)
        context["reviews"] = VendorReview.objects.for_reviewer(
            self.request.shop, self.request.person
        )
        context["review_dict"] = VendorReview.objects.for_reviewer_dict_options(
            self.request.shop, self.request.person
        )

        if pending_suppliers_reviews.exists():
            initial_values = [
                dict(supplier=supplier) for supplier in pending_suppliers_reviews
            ]
            options = [
                option
                for option in VendorReviewOption.objects.filter(
                    enabled=True, shop=self.request.shop
                )
            ]
            context["reviews_formset"] = VendorReviewGroupModelFormset(
                initial=initial_values,
                form_kwargs=dict(request=self.request, options=options),
            )

        return context

    def post(self, request):
        options = [
            option
            for option in VendorReviewOption.objects.filter(
                enabled=True, shop=request.shop
            )
        ]
        formset = VendorReviewGroupModelFormset(
            request.POST, form_kwargs=dict(request=self.request, options=options)
        )

        if formset.is_valid():
            with atomic():
                for form in formset.forms:
                    form.save()

        return HttpResponseRedirect(reverse("shuup:vendor_reviews_options"))


class VendorReviewOptionsCommentsView(BaseCommentsView):
    view_name = "vendor_review_options_comments"

    def get_reviews_page(self):
        supplier = Supplier.objects.filter(
            pk=self.kwargs["pk"], shops=self.request.shop
        ).first()
        queryset = (
            VendorReview.objects.approved()
            .filter(supplier=supplier, shop=self.request.shop, comment__isnull=False)
            .order_by("-created_on")
        )

        paginator = Paginator(queryset, settings.VENDOR_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get("page")

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)


class VendorReviewCommentsOptionsView(View):
    view_name = "vendor_review_comments_options"

    def get(self, request, *args, **kwargs):
        page = self.get_reviews_page()
        reviews = [
            {
                "id": review.pk,
                "date": review.created_on.isoformat(),
                "rating": review.rating,
                "comment": review.comment,
                "reviewer": review.reviewer.name,
                "option": review.option.pk,
            }
            for review in page.object_list
        ]

        next_page_url = None
        if page.has_next():
            next_page_url = "{}?page={}".format(
                reverse("shuup:%s" % self.view_name, kwargs=dict(pk=self.kwargs["pk"])),
                page.number + 1,
            )

        payload = {
            "reviews": reviews,
            "next_page_url": next_page_url,
        }
        return JsonResponse(payload)

    def get_reviews_page(self):
        supplier = Supplier.objects.filter(
            pk=self.kwargs["pk"], shops=self.request.shop
        ).first()
        queryset = (
            VendorReview.objects.approved()
            .filter(
                supplier=supplier,
                shop=self.request.shop,
                comment__isnull=False,
                option_id=self.kwargs["option"],
            )
            .order_by("-created_on")
        )

        paginator = Paginator(queryset, settings.VENDOR_REVIEWS_PAGE_SIZE)
        page = self.request.GET.get("page")

        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)
