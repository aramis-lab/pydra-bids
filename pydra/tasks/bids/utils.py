import os

import pydra

__all__ = ["bids_info", "bids_data_reader", "bids_data_writer"]


@pydra.mark.task
@pydra.mark.annotate(
    {
        "return": {
            "subject_label": str,
            "session_label": str,
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
    >>> result.output.subject_label
    'P01'
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'

    >>> task = bids_info(in_file="sub-P01_ses-M00_trc-18FFDG_pet.nii.gz")
    >>> result = task()
    >>> result.output.subject_label
    'P01'
    >>> result.output.session_label
    'M00'
    >>> result.output.suffix
    'pet'
    >>> result.output.entities.get("trc")
    '18FFDG'
    """
    from pathlib import PurePath
    from ancpbids.utils import parse_bids_name

    parsed = parse_bids_name(PurePath(in_file))

    entities = parsed["entities"]
    suffix = parsed["suffix"]
    extension = parsed["extension"]

    return (
        entities.get("sub"),    # subject_label
        entities.get("ses"),    # session_label
        entities,
        suffix,
        extension,
    )

def bids_data_reader():
    pass


def bids_data_writer():
    pass
