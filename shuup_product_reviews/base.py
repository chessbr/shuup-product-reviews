# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.http.response import JsonResponse
from django.urls import reverse
from django.views.generic import View


class BaseCommentsView(View):
    view_name = ""

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
                reverse("shuup:%s" % self.view_name, kwargs=dict(pk=self.kwargs["pk"])), page.number + 1
            )

        payload = {
            "reviews": reviews,
            "next_page_url": next_page_url,
        }
        return JsonResponse(payload)
