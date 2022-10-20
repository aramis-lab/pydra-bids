import dataclasses
import os
import typing as ty

import pydra

__all__ = ["bids_info", "make_bids_data_reader", "bids_data_writer"]


@pydra.mark.task
@pydra.mark.annotate(
    {
        "return": {
            "participant_id": str,
            "session_id": str,
            "entities": dict,
            "suffix": str,
            "extension": str,
        }
    }
)
def bids_info(in_file: os.PathLike):
    """Parse components of a BIDS file.

    Examples
    --------

    Parse the main components of a BIDS file:

    >>> task = bids_info(in_file="sub-P01_ses-M00_T1w.nii.gz")
    >>> result = task()
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    Other source entities are provided as a dictionary in a separate `entities` output:

    >>> task = bids_info(in_file="sub-P01_trc-18FFDG_pet.nii.gz")
    >>> result = task()
    >>> result.output.suffix
    'pet'
    >>> result.output.entities.get("trc")
    '18FFDG'
    """
    from ancpbids.utils import parse_bids_name

    parsed = parse_bids_name(os.fspath(in_file))

    entities = parsed["entities"]
    suffix = parsed["suffix"]
    extension = parsed["extension"]

    subject_label = entities.get("sub")
    session_label = entities.get("ses")

    return (
        f"sub-{subject_label}" if subject_label else None,
        f"ses-{session_label}" if session_label else None,
        entities,
        suffix,
        extension,
    )


def make_bids_data_reader(output_query: ty.Optional[dict] = None):
    from pydra.engine import specs

    # Query BOLD and T1w modalities by default.
    output_query = output_query or {
        "bold": {
            "suffix": "bold",
            "extension": [".nii", ".nii.gz"],
        },
        "T1w": {
            "suffix": "T1w",
            "extension": [".nii", ".nii.gz"],
        },
    }

    # Map output query keys to output spec for the task.
    returned = {key: ty.Iterable[specs.File] for key in list(output_query.keys())}

    # Define the inner files query implementation.
    @pydra.mark.task
    @pydra.mark.annotate({"return": returned})
    def query_files(
        dataset_path: os.PathLike,
        subject_id: ty.Union[str, ty.Iterable[str]] = "*",
        session_id: ty.Union[str, ty.Iterable[str]] = "*",
    ):
        """Query files from a BIDS dataset."""
        from os import fspath

        from ancpbids import BIDSLayout

        layout = BIDSLayout(ds_dir=fspath(dataset_path))

        results = [
            layout.get(
                return_type="files",
                subject=subject_id,
                session=session_id,
                **query,
            )
            for key, query in list(output_query.items())
        ]

        # Return tuple if more than 1 query (Pydra limitation).
        return tuple(results) if len(results) > 1 else results[0]

    return query_files


@dataclasses.dataclass
class BIDSFileInfo:
    """Parse components of a BIDS file.

    Examples
    --------

    Parse the main components of a BIDS file:

    >>> task = BIDSFileInfo().to_task(name="bids_file_info")
    >>> result = task(bids_file="sub-P01_ses-M00_T1w.nii.gz")
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    Additional source entities can be provided if specified as `output_entities`:

    >>> task = BIDSFileInfo(output_entities=["trc"]).to_task(name="bids_file_info")
    >>> result = task(bids_file="sub-P01_trc-18FFDG_pet.nii.gz")
    >>> result.output.trc
    '18FFDG'
    """

    output_entities: list = dataclasses.field(default_factory=list)

    def __call__(self, bids_file: os.PathLike):
        from ancpbids.utils import parse_bids_name

        parsed = parse_bids_name(os.fspath(bids_file))

        entities = parsed["entities"]
        suffix = parsed["suffix"]
        extension = parsed["extension"]

        # Extract participant ID
        subject_label = entities.get("sub")
        participant_id = f"sub-{subject_label}" if subject_label else None

        # Extract session ID
        session_label = entities.get("ses")
        session_id = f"ses-{session_label}" if session_label else None

        # Extract extra entities to provide as output.
        extra_entities = [entities.get(entity) for entity in self.output_entities]

        return tuple(
            [participant_id, session_id, entities, suffix, extension] + extra_entities
        )

    @property
    def input_spec(self) -> pydra.specs.SpecInfo:
        return pydra.specs.SpecInfo(
            name="BIDSFileInfoInput",
            fields=[("bids_file", os.PathLike)],
            bases=(pydra.specs.BaseSpec,),
        )

    @property
    def output_spec(self) -> pydra.specs.SpecInfo:
        # Default components parsed for all BIDS files.
        fields = [
            ("participant_id", str),
            ("session_id", str),
            ("entities", dict),
            ("suffix", str),
            ("extension", str),
        ] + [(entity, str) for entity in self.output_entities]

        return pydra.specs.SpecInfo(
            name="BIDSFileInfoOutput",
            fields=fields,
            bases=(pydra.specs.BaseSpec,),
        )

    def to_task(self, *args, **kwargs) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            *args,
            **kwargs,
        )


@dataclasses.dataclass
class BIDSDataReader:
    output_query: dict = dataclasses.field(
        default_factory=lambda: {
            "T1w": {"suffix": "T1w", "extension": ["nii", "nii.gz"]},
            "bold": {"suffix": "bold", "extension": ["nii", "nii.gz"]},
        },
    )

    def __call__(self, dataset_path: os.PathLike) -> dict:
        import ancpbids

        layout = ancpbids.BIDSLayout(ds_dir=os.fspath(dataset_path))

        return {
            key: layout.get(
                return_type="files",
                subject="*",
                session="*",
                **query,
            )
            for key, query in list(self.output_query.items())
        }

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

    def to_task(self, *args, **kwargs) -> pydra.engine.task.FunctionTask:
        return pydra.engine.task.FunctionTask(
            func=self,
            input_spec=self.input_spec,
            output_spec=self.output_spec,
            *args,
            **kwargs,
        )


def bids_data_writer():
    pass
