import pydra.tasks.bids.utils as utils


def test_bfi_defaults():
    task = utils.BIDSFileInfo().to_task()

    assert "file_path" in task.input_names
    assert {"entities", "suffix", "extension"} == set(task.output_names)


def test_bfi_with_output_entities():
    output_entities = {"participant_id": "sub", "run_id": "run"}
    task = utils.BIDSFileInfo(output_entities=output_entities).to_task()

    assert set(output_entities.keys()).issubset(task.output_names)


def test_bdr_defaults():
    task = utils.BIDSDatasetReader().to_task()

    assert "dataset_path" in task.input_names
    assert {"participant_id", "session_id"}.issubset(task.input_names)
    assert "dataset_description" in task.output_names


def test_bdr_with_output_query():
    output_query = {"T1w": {"suffix": "T1w"}, "bold": {"suffix": "bold"}}
    task = utils.BIDSDatasetReader(output_query=output_query).to_task()

    assert set(output_query.keys()).issubset(task.output_names)
