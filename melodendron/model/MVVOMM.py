from __future__ import annotations

from typing import List, Any, Dict, Callable, Set
from melodendron.model.VOMM import VOMM
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
        self.alphabets = {}
        self.state_sequence = list()                                  # An ordered sequence of all states
        self.vomms = {viewpoint: VOMM() for viewpoint in viewpoints}  # A dict of VOMM with their viewpoint as key
        self.verbose = verbose

    def __repr__(self):
        return 'VOMM(viewpoints={})'.format(self.viewpoints)

    def _state_to_mapped_state(self, state):
        mapped_state = {'id': state['id']}
        for viewpoint in (viewpoint for viewpoint in state if viewpoint != 'id'):
            if viewpoint not in self.alphabets:
                self.alphabets[viewpoint] = {0: state[viewpoint]}
            else:
                alphabet = self.alphabets[viewpoint]
                key, value = next(((key, value) for key, value in alphabet.items()
                                   if state[viewpoint] == value), (None, None))
                if key is None:
                    key = len(alphabet)
                    value = state[viewpoint]
                    alphabet[key] = value
                mapped_state[viewpoint] = key
        return mapped_state

    def _mapped_state_to_state(self, mapped_state):
        state = {'id': mapped_state['id']}
        for viewpoint in (viewpoint for viewpoint in mapped_state if viewpoint != 'id'):
            state[viewpoint] = self.alphabets[viewpoint][mapped_state[viewpoint]]
        return state

    def insert(self, state: Dict[str, Any], context_states: List[Dict[str, Any]]):
        """Inserts a new state into the sequence and updates the VOMMs."""
        # Add an id to the state (useful to compute plagiarism related metrics)
        state['id'] = len(self.state_sequence)
        mapped_state = self._state_to_mapped_state(state)
        self.state_sequence.append(mapped_state)
        # Insert the continuation index with context in each viewpoints VOMM
        continuation_idx = len(self.state_sequence) - 1
        for viewpoint in self.viewpoints:
            vomm = self.vomms[viewpoint]
            mapped_context_states = [self._state_to_mapped_state(state) for state in context_states]
            mapped_context_values = [mapped_state[viewpoint] for mapped_state in mapped_context_states]
            vomm.insert(continuation_idx, mapped_context_values)

    def insert_sequence(self, state_sequence, max_order=8):
        for i, state in enumerate(state_sequence):
            self.insert(state, state_sequence[i - max_order:i])

    def next(self, context_states: List[Dict[str, Any]],
             selector: Callable[[Dict[str: Set[Any]]], int | None]) -> Dict[str, Any]:
        """Returns a state given a context sequence and a selector."""
        # Find all potential continuations for each viewpoint
        continuation_idxs_by_viewpoints = dict()
        for viewpoint in self.viewpoints:
            vomm = self.vomms[viewpoint]
            mapped_context_states = [self._state_to_mapped_state(state) for state in context_states]
            mapped_context_values = [mapped_state[viewpoint] for mapped_state in mapped_context_states]
            continuation_idxs_by_viewpoints[viewpoint] = vomm.get_continuation_idxs(mapped_context_values)
        # Select a continuation index using the selector
        selected_continuation_idx = selector(continuation_idxs_by_viewpoints)
        # If nothing was selected, return a random state
        if selected_continuation_idx is None:
            selected_mapped_state = random.choice(self.state_sequence)
            return self._mapped_state_to_state(selected_mapped_state)
        # Else return the state corresponding to the selected continuation index
        selected_mapped_state = self.state_sequence[selected_continuation_idx]
        return self._mapped_state_to_state(selected_mapped_state)
        # Should the algorithm use the depth traversed in order to bias for longer depth ?

    def random_states(self, n=8):
        """Returns a random sample of n states taken from the internal sequence."""
        return [self._mapped_state_to_state(mapped_state) for mapped_state in random.sample(self.state_sequence, n)]

    def generate_n(self, n, selector, order=8):
        new_sequence = self.random_states(order)
        for i in range(order, n):
            new_state = self.next(new_sequence[i - order:i], selector)
            new_sequence.append(new_state)
        return new_sequence

