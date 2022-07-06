"""
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

from os import PathLike
from typing import Tuple

from pydra.mark import annotate, task


@task
@annotate(
    {"return": {"entities": dict, "suffix": str, "extension": str}}
)
def parse_bids(in_file: PathLike) -> Tuple[dict, str, str]:
    """Parse a BIDS filename and extract its BIDS components.

    :param in_file: Path to BIDS file
    :type in_file: os.PathLike
    :return: A tuple composed of the datatype, suffix, extension and entities
    :rtype: Tuple[str, str, str, list]
    """
    from pathlib import PurePath

    from ancpbids.utils import parse_bids_name

    parsed = parse_bids_name(PurePath(in_file).name)

    return parsed["entities"], parsed["suffix"], parsed["extension"]
