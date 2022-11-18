import os
from typing import Iterable, Union

import pydra

__all__ = ["BIDSFileInfo", "BIDSDatasetReader"]


class BIDSFileInfo:
    """Parse components of a BIDS file.

    Attributes
    ----------
    output_entities : dict, optional
        Mapping of BIDS entities to output names.

    Examples
    --------

    Parse the main components of a BIDS file:

    >>> task = BIDSFileInfo().to_task()
    >>> result = task(file_path="sub-P01_T1w.nii.gz")
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    Extra entities can be provided if specified as `output_entities`:

    >>> task = BIDSFileInfo(
    ...     output_entities={
    ...         "subject": "sub",
    ...         "session": "ses",
    ...         "tracer": "trc",
    ...     },
    ... ).to_task()
    >>> result = task(file_path="sub-P01_ses-M00_trc-18FFDG_pet.nii.gz")
    >>> result.output.subject
    'P01'
    >>> result.output.session
    'M00'
    >>> result.output.tracer
    '18FFDG'
    """

    def __init__(self, output_entities: dict = None):
        self.output_entities = output_entities or {}

    def __call__(self, file_path: os.PathLike):
        from ancpbids.utils import parse_bids_name

        parsed = parse_bids_name(os.fspath(file_path))

        entities = parsed["entities"]
        suffix = parsed["suffix"]
        extension = parsed["extension"]

        # Extract extra entities to provide as output.
        extra_entities = [
            entities.get(entity) for entity in self.output_entities.values()
        ]

        return tuple([entities, suffix, extension] + extra_entities)

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSFileInfoInput",
            fields=[("file_path", os.PathLike)],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        # Default components parsed for all BIDS files.
        fields = [
            ("entities", dict),
            ("suffix", str),
            ("extension", str),
        ] + [(entity, str) for entity in self.output_entities.keys()]

        return pydra.specs.SpecInfo(
            name="BIDSFileInfoOutput",
            fields=fields,
            bases=(pydra.specs.BaseSpec,),
        )

    def to_task(
        self, name: str = "bids_file_info", **kwargs
    ) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            name=name,
            **kwargs,
        )


class BIDSDatasetReader:
    """Read files from a BIDS dataset.

    Attributes
    ----------
    output_query : dict, optional
        Mapping of BIDS file queries to output names. By default, fetch T1w and BOLD imaging files.

    Examples
    --------

    Fetch all T1w scans and make them available under the "out" named output:

    >>> task = BIDSDatasetReader(
    ...     output_query={
    ...         "out": {
    ...             "suffix": "T1w",
    ...             "extension": ["nii", "nii.gz"],
    ...         },
    ...     },
    ... ).to_task()
    """

    def __init__(self, output_query: dict = None):
        self.output_query = output_query or {
            "T1w": {"suffix": "T1w", "extension": ["nii", "nii.gz"]},
            "bold": {"suffix": "bold", "extension": ["nii", "nii.gz"]},
        }

    def __call__(
        self,
        dataset_path: os.PathLike,
        subjects: Union[str, Iterable[str]] = None,
        sessions: Union[str, Iterable[str]] = None,
    ):
        import ancpbids

        layout = ancpbids.BIDSLayout(ds_dir=os.fspath(dataset_path))

        files = tuple(
            layout.get(
                return_type="files",
                subjects=subjects or "*",
                sessions=sessions or "*",
                **query,
            )
            for key, query in list(self.output_query.items())
        )

        # Flatten results if single query.
        return files if len(self.output_query) > 1 else files[0]

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSDataReaderInput",
            fields=[("dataset_path", os.PathLike)],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSDataReaderOutput",
            fields=[(key, str) for key in list(self.output_query.keys())],
            bases=(pydra.specs.BaseSpec,),
        )

    def to_task(
        self, name: str = "bids_data_reader", **kwargs
    ) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            name=name,
            **kwargs,
        )
