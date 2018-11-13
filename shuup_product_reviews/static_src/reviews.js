/**
 * This file is part of Shuup Product Reviews Addon.
 *
 * Copyright (c) 2012-2018, Shuup Inc. All rights reserved.
 *
 * This source code is licensed under the OSL-3.0 license found in the
 * LICENSE file in the root directory of this source tree.
 */
import m from "mithril";
import prop from "mithril/stream";


const ReviewComment = {
    view(vnode) {
        const review = vnode.attrs.review;
        return m(".review-comment", { "data-index": vnode.attrs.index },
            m(".date", new Date(review.date).toLocaleDateString()),
            m(".rating",
                new Array(parseInt(review.rating, 10)).fill(0).map((star, index) => (
                    m("i.fa.fa-star.rating-star", { key: index })
                ))
            ),
            m(".reviewer", review.reviewer),
            m(".comment", review.comment)
        );
    }
};

const ReviewComments = {
    oninit(vnode) {
        vnode.state.reviews = prop([]);
        vnode.state.loading = prop(true);
        vnode.state.nextPageUrl = prop(vnode.attrs.commentsUrl);

        vnode.state.loadNextPage = () => {
            if (!vnode.state.nextPageUrl()) return;
            vnode.state.loading(true);

            m.request(vnode.state.nextPageUrl()).then((data) => {
                vnode.state.loading(false);
                vnode.state.nextPageUrl(data.next_page_url);
                vnode.state.reviews([
                    ...vnode.state.reviews(),
                    ...data.reviews
                ]);
            }, (err) => {
                console.err(err);
                vnode.state.loading(false);
            });
        };
        vnode.state.loadNextPage();
    },
    view(vnode) {
        return [
            vnode.attrs.title ? m("h3", vnode.attrs.title) : null,
            m(".reviews",
                vnode.state.reviews().map((review, index) => m(ReviewComment, { review, index })),
            ),
            (vnode.state.nextPageUrl() && !vnode.state.loading()) ? (
                m(".text-center.load-more",
                    m("button.btn.btn-primary.btn-load-more-reviews", {
                        type: "button",
                        onclick() {
                            vnode.state.loadNextPage();
                        }
                    }, gettext("Load more comments"))
                )
            ) : null,
            vnode.state.loading() ? m("p.text-center", m("i.fa.fa-spin.fa-spinner.fa-2x")) : null
        ];
    }
};

export default ReviewComments;
