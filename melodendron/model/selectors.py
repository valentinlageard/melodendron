from __future__ import annotations
from typing import Dict, Set, Any
import random
import math


"""
Selectors.
Selectors functions used by the model to select a continuation index among possible continuation indexes.
"""


def random_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]], verbose=False) -> int | None:
    """Returns a continuation index by randomly selecting in all continuation indexes."""
    all_continuation_idxs = list()
    for continuation_idxs in continuation_idxs_by_viewpoints.values():
        if continuation_idxs is not None:
            all_continuation_idxs.extend(list(continuation_idxs))
    if not all_continuation_idxs:
        return None
    state_selected = random.choice(all_continuation_idxs)
    if verbose:
        str_format = '{} was selected among {}'.format(state_selected, all_continuation_idxs)
        print(str_format)
    return state_selected


def intersect_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]], verbose=False) -> int | None:
    """Returns a continuation index by randomly selecting in continuation indexes present in all viewpoints."""
    all_continuation_idxs = (continuation_idxs for continuation_idxs in continuation_idxs_by_viewpoints.values()
                             if continuation_idxs is not None)
    continuation_idxs_intersection = set.intersection(*all_continuation_idxs)
    if not continuation_idxs_intersection:
        return None
    state_selected = random.choice(list(continuation_idxs_intersection))
    if verbose:
        str_format = '{} was selected among {}'.format(state_selected, continuation_idxs_intersection)
        print(str_format)
    return state_selected

def weighted_intersect_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]], verbose=False) -> int | None:
    """Returns a continuation index by assigning a weight to each continuation index and randomly selecting using the
    weights.
    weight = sum(1 / len(continuation_idxs)) for viewpoints if continuation_idx in viewpoint
    """
    all_weighted_continuation_idxs = dict()
    for continuation_idxs in continuation_idxs_by_viewpoints.values():
        if continuation_idxs is not None:
            for continuation_idx in continuation_idxs:
                if continuation_idx in all_weighted_continuation_idxs:
                    all_weighted_continuation_idxs[continuation_idx] += 1 / len(continuation_idxs)
                else:
                    all_weighted_continuation_idxs[continuation_idx] = 1 / len(continuation_idxs)
    if not all_weighted_continuation_idxs:
        return None
    state_selected = random.choices(list(all_weighted_continuation_idxs.keys()),
                                    list(all_weighted_continuation_idxs.values()))[0]
    if verbose:
        str_format = '{} was selected among {}'.format(state_selected, all_weighted_continuation_idxs)
        print(str_format)
    return state_selected

def exp_weighted_intersect_select(continuation_idxs_by_viewpoints: Dict[str: Set[Any]],
                                  factor=1, verbose=False) -> int | None:
    """Similar to weighted_intersect_select except that an exponential factor is given to increase relative
    weighting."""
    all_weighted_continuation_idxs = dict()
    for continuation_idxs in continuation_idxs_by_viewpoints.values():
        if continuation_idxs is not None:
            for continuation_idx in continuation_idxs:
                if continuation_idx in all_weighted_continuation_idxs:
                    all_weighted_continuation_idxs[continuation_idx] += 1 / len(continuation_idxs)
                else:
                    all_weighted_continuation_idxs[continuation_idx] = 1 / len(continuation_idxs)
    for continuation_idx, weight in all_weighted_continuation_idxs.items():
        all_weighted_continuation_idxs[continuation_idx] = math.exp(weight * factor) - 1
    if not all_weighted_continuation_idxs:
        return None
    state_selected = random.choices(list(all_weighted_continuation_idxs.keys()),
                                    list(all_weighted_continuation_idxs.values()))[0]
    if verbose:
        str_format = '{} was selected among {}'.format(state_selected, all_weighted_continuation_idxs)
        print(str_format)
    return state_selected


#TODO: Hierarchical select


__all__ = ['random_select', 'intersect_select', 'weighted_intersect_select', 'exp_weighted_intersect_select']
