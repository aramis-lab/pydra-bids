import pydra.tasks.bids.utils as utils


def test_bfi_defaults():
    task = utils.BIDSFileInfo().to_task()

    assert "bids_file" in task.input_names
    assert {"entities", "suffix", "extension"} == set(task.output_names)


def test_bdr_defaults():
    task = utils.BIDSDataReader().to_task()

    assert "dataset_path" in task.input_names
    assert {"T1w", "bold"} == set(task.output_names)
