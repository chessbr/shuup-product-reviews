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

const Star = {
    view(vnode) {
        return m(".star", {
            onmouseover() {
                vnode.attrs.onMouseOver();
            },
            onmouseout() {
                vnode.attrs.onMouseOut();
            },
            onclick() {
                vnode.attrs.onClick();
            }
        }, vnode.attrs.highlight ? m("i.fa.fa-star.fa-2x") : m("i.fa.fa-star-o.fa-2x"))
    }
};


const RatingStarsInput = {
    oninit(vnode) {
        vnode.state.overState = prop(false);
        vnode.state.overStarIndex = prop(0);
        vnode.state.selectedStarIndex = prop(0);
        vnode.state.shouldHighlight = (index) => (
            (
                (vnode.state.overState() && vnode.state.overStarIndex() >= index) ||
                (!vnode.state.overState() && vnode.state.selectedStarIndex() >= index)
            )
        );
        vnode.state.onStarPress = (index) => {
            if (vnode.state.selectedStarIndex() === index) {
                vnode.state.selectedStarIndex(0);
                vnode.state.$input.attr("value", 0);
            } else {
                vnode.state.selectedStarIndex(index);
                vnode.state.$input.attr("value", index);
            }
        };
    },
    oncreate(vnode) {
        vnode.state.$input = $(vnode.dom).parent().siblings("input.rating-input");
        vnode.state.$input.hide();
    },
    view(vnode) {
        return m(".stars", {
            onmouseover() {
                vnode.state.overState(true);
            },
            onmouseout() {
                vnode.state.overState(false);
            }
        },
            [1, 2, 3, 4, 5].map(index => (
                m(Star, {
                    key: index,
                    highlight: vnode.state.shouldHighlight(index),
                    onMouseOver() {
                        vnode.state.overStarIndex(index);
                    },
                    onMouseOut() {
                        vnode.state.overStarIndex(0);
                    },
                    onClick() {
                        vnode.state.onStarPress(index);
                    }
                })
            ))
        );
    }
};

export default RatingStarsInput;
