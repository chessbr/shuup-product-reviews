/**
 * This file is part of Shuup Product Reviews Addon.
 *
 * Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
 *
 * This source code is licensed under the OSL-3.0 license found in the
 * LICENSE file in the root directory of this source tree.
 */
import m from "mithril";
import RatingStarsInput from "./starInput";
import ReviewComments from "./reviews";


(() => {
    // mount rating stars when needed
    Array.from(document.getElementsByClassName("rating-input")).forEach((element) => {
        const ratingStarsInput = document.createElement("div");
        element.parentElement.appendChild(ratingStarsInput);
        ratingStarsInput.className = "star-rating-input";
        m.mount(ratingStarsInput, RatingStarsInput);
    });

    // mount review comments component when needed
    Array.from(document.getElementsByClassName("product-review-comments")).forEach((element) => {
        const commentsUrl = element.getAttribute("data-url");
        m.mount(element, {
            view() {
                return m(ReviewComments, { commentsUrl });
            }
        });
    });
})();
