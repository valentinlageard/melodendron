from __future__ import annotations

from typing import List, Any, Dict, Callable, Set
from model.VOMM import VOMM
import random


class MVVOMM:
    """A Multiple Viewpoints Variable Order Markov Model.

    Given a viewpoints hierarchy and a sequence of events with
    multiple properties, it builds VOMM for each viewpoints and
    is able to generate new events by hierarchically selecting
    the next event given a context sequence.

    Based on "The Continuator: Musical Interaction With Style"
    by F. Pachet (2010) and "Multiple Viewpoints Systems for
    Music Prediction" by I. Witten and D. Conklin (1993).
    """

    def __init__(self, viewpoints: List[str], verbose=False):
        self.viewpoints = viewpoints                                  # A list of viewpoints
        self.state_sequence = list()                                  # An ordered sequence of all states
        self.vomms = {viewpoint: VOMM() for viewpoint in viewpoints}  # A dict of VOMM with their viewpoint as key
        self.verbose = verbose

    def __repr__(self):
        return 'VOMM(viewpoints={})'.format(self.viewpoints)

    def insert(self, state: Dict[str, Any], context_states: List[Dict[str, Any]]):
        """Inserts a new state into the sequence and updates the VOMMs."""
        self.state_sequence.append(state)
        continuation_idx = len(self.state_sequence) - 1
        for viewpoint in self.viewpoints:
            vomm = self.vomms[viewpoint]
            context_values = [state[viewpoint] for state in context_states]
            vomm.insert(continuation_idx, context_values)

    def next(self, context_states: List[Dict[str, Any]],
             selector: Callable[[Dict[str: Set[Any]]], int | None]) -> Dict[str, Any]:
        """Returns a state given a context sequence and a selector."""
        # Find all potential continuations for each viewpoint
        continuation_idxs_by_viewpoints = dict()
        for viewpoint in self.viewpoints:
            vomm = self.vomms[viewpoint]
            context_values = [state[viewpoint] for state in context_states]
            continuation_idxs_by_viewpoints[viewpoint] = vomm.get_continuation_idxs(context_values)
        # Select a continuation index using the selector
        selected_continuation_idx = selector(continuation_idxs_by_viewpoints)
        # If nothing was selected, return a random state
        if selected_continuation_idx is None:
            return random.choice(self.state_sequence)
        # Else return the state corresponding to the selected continuation index
        return self.state_sequence[selected_continuation_idx]
        # Should the algorithm use the depth traversed in order to bias for longer depth ?

    def random_states(self, n=5):
        """Returns a random sample of n states taken from the internal sequence."""
        return random.sample(self.state_sequence, n)

