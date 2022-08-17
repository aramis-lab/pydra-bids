import os
import typing as ty

from pydra.engine.task import FunctionTask

import pydra


def make_bids_reader(
    output_query: ty.Optional[dict] = None,
) -> ty.Callable[..., FunctionTask]:
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


@pydra.mark.task
@pydra.mark.annotate({"return": {"subjects": ty.Iterable[str]}})
def query_subjects(
    base_dir: os.PathLike, allowed_subjects: ty.Optional[ty.Iterable[str]] = None
):
    from os import fspath

    from ancpbids import BIDSLayout

    layout = BIDSLayout(ds_dir=fspath(base_dir))

    subjects = layout.get_subjects()

    if allowed_subjects:
        subjects = list(set(subjects).intersection(allowed_subjects))

    return subjects


@pydra.mark.task
@pydra.mark.annotate(
    {"return": {"subjects": ty.Iterable[str], "sessions": ty.Iterable[str]}}
)
def query_subjects_and_sessions(
    base_dir: os.PathLike,
    allowed_subject_session_pairs: ty.Optional[ty.Iterable[ty.Tuple[str, str]]] = None,
):
    from os import fspath

    from ancpbids import BIDSLayout

    layout = BIDSLayout(ds_dir=fspath(base_dir))

    subject_session_pairs = set(
        [
            (subject, session)
            for subject in layout.get_subjects()
            for session in layout.get_sessions(subject=subject)
        ]
    )

    if allowed_subject_session_pairs:
        subject_session_pairs = subject_session_pairs.intersection(
            allowed_subject_session_pairs
        )

    return tuple(zip(*subject_session_pairs))
