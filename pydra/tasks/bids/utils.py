"""
Examples
--------

>>> task = parse_bids(in_file="sub-01/ses-M00/anat/sub-01_ses-M00_T1w.nii.gz")
>>> result = task()
>>> result.output.datatype
'anat'
>>> result.output.suffix
'T1w'
>>> result.output.extension
'.nii.gz'
>>> result.output.entities
['sub-01', 'ses-M00']
"""

from pydra.mark import annotate, task
from os import PathLike
from typing import Tuple


@task
@annotate({"return": {"datatype": str, "suffix": str, "extension": str, "entities": list}})
def parse_bids(in_file: PathLike) -> Tuple[str, str, str, list]:
    """Parse a BIDS filename and extract its BIDS components.

    :param in_file: Path to BIDS file
    :type in_file: os.PathLike
    :return: A tuple composed of the datatype, suffix, extension and entities
    :rtype: Tuple[str, str, str, list]
    """
    from pathlib import PurePath

    in_file = PurePath(in_file)
    datatype = in_file.parent.name
    filename = str(in_file.name)
    stem, _, extension = filename.partition(".")
    rest, _, suffix = stem.rpartition("_")
    entities = list(rest.split("_"))
    extension = f".{extension}"

    return datatype, suffix, extension, entities
