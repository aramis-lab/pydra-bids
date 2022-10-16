import os

import pydra

__all__ = ["bids_info", "bids_data_reader", "bids_data_writer"]


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
    >>> task = bids_info(in_file="sub-P01_T1w.nii.gz")
    >>> result = task()
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    >>> task = bids_info(in_file="sub-P01_ses-M00_trc-18FFDG_pet.nii.gz")
    >>> result = task()
    >>> result.output.participant_id
    'sub-P01'
    >>> result.output.session_id
    'ses-M00'
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


def bids_data_reader():
    pass


def bids_data_writer():
    pass
