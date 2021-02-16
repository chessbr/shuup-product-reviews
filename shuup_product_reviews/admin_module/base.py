# -*- coding: utf-8 -*-
# This file is part of Shuup Product Reviews Addon.
#
# Copyright (c) 2012-2019, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from shuup.admin.utils.picotable import ChoicesFilter, Column, RangeFilter, TextFilter
from shuup.admin.utils.views import PicotableListView

from shuup_product_reviews.enums import ReviewStatus


class BaseProductReviewListView(PicotableListView):
    model = None

    default_columns = [
        Column("reviewer__name", _("Reviewer"), filter_config=TextFilter(filter_field="reviewer__name")),
        Column("rating", _("Rating"), filter_config=RangeFilter(min=1, max=5, step=1, filter_field="rating")),
        Column("comment", _("Comment")),
        Column(
            "status", _("Status"), filter_config=ChoicesFilter(choices=ReviewStatus.choices(), filter_field="status")
        ),
    ]

    def __init__(self):
        super(BaseProductReviewListView, self).__init__()
        self.columns = self.default_columns
