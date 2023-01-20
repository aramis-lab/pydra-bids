# pydra-bids

[![PyPI - Version](https://img.shields.io/pypi/v/pydra-bids.svg)](https://pypi.org/project/pydra-bids)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydra-bids.svg)](https://pypi.org/project/pydra-bids)

---

Pydra tasks for BIDS I/O.

[Pydra][pydra] is a dataflow engine
which provides a set of lightweight abstractions
for DAG construction, manipulation, and distributed execution.

[BIDS][bids] defines standards for organizing neuroimaging files and metadata.

This project provides tasks for reading from and writing to BIDS datasets.

**Table of contents**

- [Installation](#installation)
- [Development](#development)
- [Licensing](#licensing)

## Installation

```console
pip install pydra-bids
```

## Development

This project is managed with [Hatch][hatch]:

```console
pipx install hatch
```

To run the test suite:

```console
hatch run test:no-cov
```

To fix linting issues:

```console
hatch run lint:fix
```

To check the documentation:

```console
hatch run docs:serve --open-browser
```

## Licensing

This project is released under the terms of the [Apache License, Version 2.0][license].

[pydra]: https://nipype.github.io/pydra
[bids]: https://bids-specification.readthedocs.io
[hatch]: https://hatch.pypa.io
[license]: https://opensource.org/licenses/Apache-2.0
