# Melodendron

## The Model

A MVVOMM (Multiple Viewpoints Variable Order Markov Model) is used to model n-order graphs of state transitions.
- Keeps a sequence of states composed of multiple properties (pitches, durations, ...).
- For each relevant property (or viewpoint), a VOMM (Variable Order Markov Model) is created and insertion of a new 
state inserts the state property for each viewpoint VOMM.
- Can be queried with a context sequence to select a new state (a continuation). To select the new state, the MVVOMM
queries its viewpoint's VOMMs to get all potential continuation indexes and then applies a selection function to select
the continuation.

States are dictionaries : {'property': value, ...}. Values should be equal comparable.

Problems : 
- Each viewpoint VOMM may not return continuation indexes with the same depth ? Is it really a problem ?

Several selector functions are implemented.
- Random selection : a state is randomly selected from concatenated continuations indexes of all viewpoints.
- Intersection selection : a state is randomly selected from the intersection of all viewpoint's continuations indexes.
- Hierarchical selection : TODO !

## Parsing

Midi is parsed using mido and converted to states of the form :

```python
state = dict('pitches': set(int, ...),
             'note_events': list(note_event, ...),
             'on_duration': int,
             'off_duration': int,
             'total_duration': int)

note_event = dict('pitch': int,
                  'velocity': int,
                  'start_delta': int,
                  'end_delta': int)
```

Design choices :
- Simultaneous midi notes are clustered together to manage polyphony. Therefore states may have multiple pitches. States
store a `note_event` list to recreate the play order of the state when converting back to midi.
- Silence after a note cluster is a property of the note cluster and not an state in itself.

TODO: Additional functions are implemented to enrich states with derived properties :
- Ticks to beats : all durations are converted to beats.
- Ticks to ms : all durations are converted to ms.
- Absolute pitch to non-octave pitch.
- Absolute pitch to relative to fundamental.
- Absolute pitch to pitch region.

### Polyphonic clustering problems

**Legato problem:** How to manage slightly ovelapping notes (legato) as pertaining to different states ?
- Consider slightly overlapping notes as different when the overlapping is small enough. Introduces a legato_delay parameter to tune.

**Polyphonic notes data structure:** Which data structure for polyphony ?
- Solution 1 : Stacked segmentation at every note boundary (àla Assayag & al.) ?
- Solution 2 : Ordered list of note events (pitch, velocity, on_duration, start_delta). Seems simpler in principle.

**Drone note problem:** What should happen when a single note is still pressed while others are played as melody ?

**Polyphonic comparison:** How to compare polyphonic states based on their pitches ?
- For trivial monophonic case, you easily compare equal or different.
- For polyphonic cases, we can compare strictly equal (all notes are presents) or per degree (how many notes are present).

**Changing key_signature and time_signature:** How to manage changes in key_signature and time_signature during the piece ?
- Clean tracks containing such changes, merge them and prioritize the meta messages.

TODO: There is an error in current clustering algorithm.