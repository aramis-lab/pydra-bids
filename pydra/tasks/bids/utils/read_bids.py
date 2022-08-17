from typing import Callable, Optional

from pydra.engine.task import FunctionTask


def make_bids_reader(
    output_query: Optional[dict] = None,
) -> Callable[..., FunctionTask]:
    """Generate a BIDS reading task.

    Parameters
    ----------
    output_query : dict
        Mapping between output and BIDS query

    Returns
    -------
    pydra.engine.task.FunctionTask
        BIDS reading task

    Examples
    --------
    >>> bids_reader = make_bids_reader()
    >>> task = bids_reader()
    >>> task.output_names
    ['bold', 'T1w']
    """
    import os
    import typing as ty

    import pydra

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

    returned = {key: pydra.engine.specs.File for key in list(output_query.keys())}

    @pydra.mark.task
    @pydra.mark.annotate({"return": returned})
    def read_bids(
        base_dir: os.PathLike,
        subject: ty.Optional[str] = None,
        session: ty.Optional[str] = None,
    ):
        from os import fspath

        from ancpbids import BIDSLayout

        layout = BIDSLayout(ds_dir=fspath(base_dir))

        results = [
            layout.get(
                return_type="files",
                subject=subject or "*",
                session=session or "*",
                **query,
            )
            for key, query in list(output_query.items())
        ]

        return tuple(results) if len(results) > 1 else results[0]

    return read_bids
