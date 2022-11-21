import pydra.tasks.bids.utils as utils


def test_bfi_defaults():
    task = utils.BIDSFileInfo().to_task()

    assert "file_path" in task.input_names
    assert {"entities", "suffix", "extension"} == set(task.output_names)


def test_bdr_defaults():
    task = utils.BIDSDatasetReader().to_task()

    assert "dataset_path" in task.input_names
    assert "dataset_description" in task.output_names


def test_bdr_with_output_query():
    task = utils.BIDSDatasetReader(
        output_query={"T1w": {"suffix": "T1w"}, "bold": {"suffix": "bold"}}
    ).to_task()
    assert {"T1w", "bold"}.issubset(task.output_names)
