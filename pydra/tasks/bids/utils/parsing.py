"""Tasks for parsing BIDS components."""

import os
import typing as ty

import pydra


@pydra.mark.task
@pydra.mark.annotate({"return": {"entities": dict, "suffix": str, "extension": str}})
def parse_bids(in_file: os.PathLike) -> ty.Tuple[dict, str, str]:
    """Parse a BIDS filename and extract its BIDS components.

    Parameters
    ----------
    in_file : os.PathLike
        Path to the input BIDS file.

    Returns
    -------
    entities: dict
        The entities composing the BIDS file as a mapping from prefix to value.
    suffix: str
        The suffix of the BIDS file.
    extension: str
        The extension of the BIDS file.

    Examples
    --------

    >>> task = parse_bids(in_file="sub-01/ses-M00/anat/sub-01_ses-M00_T1w.nii.gz")
    >>> result = task()
    >>> result.output.suffix
    'T1w'
    >>> result.output.extension
    '.nii.gz'
    >>> result.output.entities
    {'sub': '01', 'ses': 'M00'}
    """
    from pathlib import PurePath

    from ancpbids.utils import parse_bids_name

    return tuple(parse_bids_name(PurePath(in_file)).values())
