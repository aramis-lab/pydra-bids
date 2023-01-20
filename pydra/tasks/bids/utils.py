import os
import pathlib
import typing as ty

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
    ...         "participant_id": "sub",
    ...         "session_id": "ses",
    ...         "tracer_id": "trc",
    ...     },
    ... ).to_task()
    >>> result = task(file_path="sub-P01_ses-M00_trc-18FFDG_pet.nii.gz")
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
    >>> result.output.tracer_id
    'trc-18FFDG'

    If some output entities are not present, their corresponding value is set to None:

    >>> task = BIDSFileInfo(output_entities={"session_id": "ses"}).to_task()
    >>> result = task(file_path="sub-P01_T1w.nii.gz")
    >>> result.output.session_id is None
    True
    """

    def __init__(self, output_entities: dict = None):
        self.output_entities = output_entities or {}

    def __call__(self, file_path: os.PathLike):
        from ancpbids.utils import parse_bids_name

        parsed = parse_bids_name(pathlib.PurePath(file_path).name)

        entities = parsed["entities"]
        suffix = parsed["suffix"]
        extension = parsed["extension"]

        # Extract extra entities to provide as output.
        extra_entities = [
            f"{prefix}-{value}" if value else None
            for prefix, value in [
                (entity, entities.get(entity))
                for entity in self.output_entities.values()
            ]
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
        ] + [(entity, ty.Optional[str]) for entity in self.output_entities.keys()]

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
        self.output_query = output_query

    def __call__(
        self,
        dataset_path: os.PathLike,
        participant_id: ty.Optional[str] = None,
        session_id: ty.Optional[str] = None,
    ):
        import ancpbids

        layout = ancpbids.BIDSLayout(ds_dir=os.fspath(dataset_path))

        dataset_description = layout.get_dataset_description(all_=False)

        subjects = participant_id.replace("sub-", "") if participant_id else "*"
        sessions = session_id.replace("ses-", "") if session_id else "*"

        files = (
            tuple(
                layout.get(
                    return_type="files",
                    subjects=subjects,
                    sessions=sessions,
                    **query,
                )
                for key, query in list(self.output_query.items())
            )
            if self.output_query
            else None
        )

        return (dataset_description,) + files if files else dataset_description

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSDatasetReaderInput",
            fields=[
                ("dataset_path", os.PathLike),
                ("participant_id", ty.Optional[str]),
                ("session_id", ty.Optional[str]),
            ],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        fields = [("dataset_description", dict)]
        if self.output_query:
            fields += [(key, str) for key in list(self.output_query.keys())]

        return pydra.specs.SpecInfo(
            name="BIDSDatasetReaderOutput", fields=fields, bases=(pydra.specs.BaseSpec,)
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
