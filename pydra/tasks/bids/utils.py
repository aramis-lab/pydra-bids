import functools
import os
import pathlib
import typing as ty
import warnings

with warnings.catch_warnings():
    # UserWarning: Development of the BIDSLayout interface will continue in the pybids project.
    warnings.simplefilter("ignore")
    import ancpbids

import pydra

__all__ = ["parse_bids_name", "read_bids_dataset"]


def _parse_bids_name(file_path: os.PathLike, output_entities: list):
    """Parse BIDS components of a BIDS file.

    Parameters
    ----------
    file_path: path-like
        Path to the BIDS file.
    output_entities: list of str
        Extra entities to parse.

    Returns
    -------
    tuple:
        Composed of:
        - The dataset description as a dictionary
        - The parsed BIDS entities as a dictionary
        - The suffix as a string
        - The extension as a string
        - Each extra entity as a string
    """
    file_name = pathlib.PurePath(file_path).name
    parsed = ancpbids.utils.parse_bids_name(file_name)

    entities = parsed["entities"]
    suffix = parsed["suffix"]
    extension = parsed["extension"]

    # Extract extra entities to provide as output.
    extra_entities = [
        f"{prefix}-{value}" if value else None
        for prefix, value in [
            (entity, entities.get(entity))
            for entity in output_entities
        ]
    ]

    return tuple([entities, suffix, extension] + extra_entities)


def parse_bids_name(output_entities: ty.Optional[dict] = None, **kwargs) -> pydra.engine.task.FunctionTask:
    """Parse components of a BIDS file.

    Attributes
    ----------
    output_entities : dict, optional
        Mapping of BIDS entities to output names.

    Examples
    --------
    Parse the main components of a BIDS file:

    >>> task = parse_bids_name()
    >>> result = task(file_path="sub-P01_T1w.nii.gz")
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    Extra entities can be provided if specified as `output_entities`:

    >>> task = parse_bids_name(
    ...     output_entities={
    ...         "participant_id": "sub",
    ...         "session_id": "ses",
    ...         "tracer_id": "trc",
    ...     }
    ... )
    >>> result = task(file_path="sub-P01_ses-M00_trc-18FFDG_pet.nii.gz")
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
    >>> result.output.tracer_id
    'trc-18FFDG'

    If some output entities are not present, their corresponding value is set to None:

    >>> task = parse_bids_name(output_entities={"session_id": "ses"})
    >>> result = task(file_path="sub-P01_T1w.nii.gz")
    >>> result.output.session_id is None
    True
    """

    output_entities = output_entities or {}

    input_spec = pydra.specs.SpecInfo(
        name="Input",
        fields=[("file_path", os.PathLike)],
        bases=(pydra.specs.BaseSpec,),
    )

    output_spec = pydra.specs.SpecInfo(
        name="Output",
        fields=[
            ("entities", dict),
            ("suffix", str),
            ("extension", str),
        ] + [
            (entity, ty.Optional[str])
            for entity in output_entities.keys()
        ],
        bases=(pydra.specs.BaseSpec,),
    )

    name = kwargs.pop("name", "parse_bids_name")

    return pydra.engine.task.FunctionTask(
        func=functools.partial(
            _parse_bids_name,
            output_entities=list(output_entities.values()),
        ),
        input_spec=input_spec,
        output_spec=output_spec,
        name=name,
        **kwargs,
    )


def _read_bids_dataset(
    dataset_path: os.PathLike,
    output_queries: ty.Optional[list] = None,
    participant_id: ty.Optional[str] = None,
    session_id: ty.Optional[str] = None,
):
    """Read files from a BIDS dataset.

    Parameters
    ----------
    dataset_path: path-like
        Path to the BIDS dataset.
    output_queries: list of dict, optional
        Queries for files in the BIDS dataset.
        For instance: [
            {"suffix": "T1w", "extension": "nii.gz"},
            {"suffix": "bold", "extension": "nii.gz"},
        ]
    participant_id: str, optional
        Restrict queries to a specific participant ID.
    session_id: str, optional
        Restrict queries to a specific session ID.
    Returns
    -------
    tuple:
        Composed of:
        - The dataset description as a dictionary
        - A list of files for each query
    """
    dataset = ancpbids.load_dataset(os.fspath(dataset_path))
    dataset_description = dict(dataset.dataset_description)

    if output_queries:
        subjects = participant_id.replace("sub-", "") if participant_id else "*"
        sessions = session_id.replace("ses-", "") if session_id else "*"

        files = tuple(
            dataset.query(
                return_type="files",
                subjects=subjects,
                sessions=sessions,
                **query,
            )
            for query in output_queries
        )
    else:
        files = None

    return (dataset_description,) + files if files else dataset_description


def read_bids_dataset(output_queries: ty.Optional[dict] = None, **kwargs) -> pydra.engine.task.FunctionTask:
    """Read files from a BIDS dataset.

    Attributes
    ----------
    output_queries : dict, optional
        Mapping of BIDS file queries to output names.

    Examples
    --------
    Fetch all T1w scans and make them available under the "out" named output:

    >>> task = read_bids_dataset(
    ...     output_query={
    ...         "out": {
    ...             "suffix": "T1w",
    ...             "extension": ["nii", "nii.gz"],
    ...         },
    ...     }
    ... )
    """

    output_queries = output_queries or {}

    input_spec = pydra.specs.SpecInfo(
        name="Input",
        fields=[
            ("dataset_path", os.PathLike),
            ("participant_id", ty.Optional[str]),
            ("session_id", ty.Optional[str]),
        ],
        bases=(pydra.specs.BaseSpec,),
    )

    output_spec = pydra.specs.SpecInfo(
        name="Output",
        fields=[("dataset_description", dict)] + [
            (key, str) for key in output_queries.keys()
        ],
        bases=(pydra.specs.BaseSpec,),
    )

    name = kwargs.pop("name", "read_bids_dataset")

    return pydra.engine.task.FunctionTask(
        func=functools.partial(
            _read_bids_dataset,
            output_queries=list(output_queries.values()),
        ),
        input_spec=input_spec,
        output_spec=output_spec,
        name=name,
        **kwargs,
    )
