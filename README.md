# pydra-bids

Pydra tasks for BIDS I/O.

[Pydra] is a dataflow engine which provides a set of lightweight abstractions
for DAG construction, manipulation, and distributed execution.

[BIDS] defines standards for organizing neuroimaging files and metadata.

This project provides tasks for reading from and writing to BIDS datasets.

## Development

This project is managed using [Poetry].

To install, check and test the code:

```console
make
```

To run the test suite when hacking:

```console
make test
```

To format the code before review:

```console
make format
```

To build the project's documentation:

```console
make docs
```

## Licensing

This project is released under the terms of the Apache License 2.0.

[Pydra]: https://nipype.github.io/pydra
[BIDS]: https://bids-specification.readthedocs.io
[Poetry]: https://python-poetry.org
