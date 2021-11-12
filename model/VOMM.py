from __future__ import annotations
from typing import Any, List, Set


class VOMMNode:
    """A node for a variable order markov model."""

    def __init__(self, value: Any, continuation_idx: int):
        self.value = value
        self.continuation_idxs = {continuation_idx}
        self.children = set()

    def __repr__(self):
        return 'VOMMNode({})'.format(self.value)

    def __str__(self):
        format_children = ', '.join(str(child) for child in self.children)
        if len(format_children) == 0:
            format_children = 'None'
        format_str = 'VOMMNode(value={}, continuation_idxs={}, children={})'
        return format_str.format(self.value, self.continuation_idxs, format_children)

    def __getitem__(self, key):
        for child in self.children:
            if child.value == key:
                return child
        return None

    def add_child(self, child: VOMMNode):
        self.children.add(child)

    def add_continuation_idx(self, continuation_idx: int):
        self.continuation_idxs.add(continuation_idx)


class VOMM:
    """A Variable Order Markov Model.
    Designed for fast retrieval by building a trie upside down
    with a root for each starting value.
    """

    def __init__(self):
        self.roots = set()

    def __repr__(self):
        return 'VOMM()'

    def __str__(self):
        format_roots = ', '.join(str(root) for root in self.roots)
        return 'VOMM({})'.format(format_roots)

    def insert(self, continuation_idx: int, context_values: List[Any]):
        """Inserts a new value idx in the trie."""

        if len(context_values) == 0:
            return
        context_values.reverse()
        last_context_value = context_values[0]
        if last_context_value not in (root.value for root in self.roots):
            current_node = VOMMNode(last_context_value, continuation_idx)
            self.roots.add(current_node)
        else:
            current_node = next((root for root in self.roots if root.value == last_context_value))
            current_node.add_continuation_idx(continuation_idx)
        for context_value in context_values[1:]:
            next_node = current_node[context_value]
            if next_node is None:
                next_node = VOMMNode(context_value, continuation_idx)
                current_node.add_child(next_node)
            else:
                next_node.add_continuation_idx(continuation_idx)
            current_node = next_node

    def get_continuation_idxs(self, context_values: List[Any]) -> Set[int] | None:
        if not context_values:
            return None
        last_context_value = context_values[-1]
        if last_context_value not in (root.value for root in self.roots):
            return None
        current_node = next((root for root in self.roots if root.value == last_context_value))
        context_sequence = context_values[-2::-1]
        for context_value in context_sequence:
            next_node = current_node[context_value]
            if next_node is None:
                return current_node.continuation_idxs
            current_node = next_node
        return current_node.continuation_idxs


if __name__ == '__main__':
    sequence1 = ['A', 'B', 'C', 'D']
    sequence2 = ['A', 'B', 'B', 'C']
    total_sequence = sequence1 + sequence2
    vomm = VOMM()
    for i in range(len(sequence1)):
        vomm.insert(i, sequence1[0:i])
    for i in range(len(sequence2)):
        vomm.insert(i + 4, sequence2[0:i])
    print(str(vomm))
    print(vomm.get_continuation_idxs(['A', 'B']))
