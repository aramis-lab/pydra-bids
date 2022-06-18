# pydra-bids

Pydra tasks for BIDS I/O.

[Pydra] is a dataflow engine which provides a set of lightweight abstractions
for DAG construction, manipulation, and distributed execution.

[BIDS] defines standards for organizing neuroimaging files and metadata.

This project provides tasks for reading from and writing to BIDS datasets.

## Development

Setup for development requires [Poetry].

Install the project and its dependencies with:

```console
make install
```

Run the tests with:

```console
make test
```

Build the project's documentation with:

```console
make docs
```

Format the code before review with:

```console
make format
```

## Licensing

This project is released under the terms of the Apache License 2.0.


[Pydra]: https://nipype.github.io/pydra
[BIDS]: https://bids-specification.readthedocs.io
[Poetry]: https://python-poetry.org
