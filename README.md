# Melodendron

> This is a non-stable development prototype.

A musical composition generator capable of learning musical styles and generating compositions.
Under the hood, Melodendron uses multiple viewpoints variable order markov models.
Melodendron's design is inspired by Francois Pachet's Continuator.

## Features

- Implements a viewpoint agnostic multiple viewpoints variable order markov model tweaked for fast continuation
generation.
- Midi file parsing and utilities are provided.
- Reduction functions library to enrich state's viewpoints.
- Selector functions library to control selection of continuations.

## Roadmap

Parsing:

- Real-time parser.
- Legato tolerant parsing.
- Support for key and time signatures changes.

Model:

- Selector function that weights viewpoints using entropy.
- Better metrics.
- Real time learning.
- Real time generation.

## Examples

See the `examples` directory.