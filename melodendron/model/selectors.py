from __future__ import annotations
from typing import Dict, Set, Any
import random


"""
Selectors.
Selectors functions used by the model to select a continuation index among possible continuation indexes.
"""


def random_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]]) -> int | None:
    """Returns a continuation index by randomly selecting in all continuation indexes."""
    all_continuation_idxs = list()
    for continuation_idxs in continuation_idxs_by_viewpoints.values():
        if continuation_idxs is not None:
            all_continuation_idxs.extend(list(continuation_idxs))
    if not all_continuation_idxs:
        return None
    state_selected = random.choice(all_continuation_idxs)
    str_format = '{} was selected among {}'.format(state_selected, all_continuation_idxs)
    print(str_format)
    return state_selected


def intersect_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]]) -> int | None:
    """Returns a continuation index by randomly selecting in continuation indexes present in all viewpoints."""
    all_continuation_idxs = (continuation_idxs for continuation_idxs in continuation_idxs_by_viewpoints.values()
                             if continuation_idxs is not None)
    continuation_idxs_intersection = set.intersection(*all_continuation_idxs)
    if not continuation_idxs_intersection:
        return None
    state_selected = random.choice(list(continuation_idxs_intersection))
    str_format = '{} was selected among {}'.format(state_selected, continuation_idxs_intersection)
    print(str_format)
    return state_selected


#TODO: Hierarchical select


__all__ = ['random_select', 'intersect_select']
