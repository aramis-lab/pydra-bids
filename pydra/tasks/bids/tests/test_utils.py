import pydra.tasks.bids.utils as utils


def test_bfi_defaults():
    task = utils.parse_bids_name()

    assert "file_path" in task.input_names
    assert {"entities", "suffix", "extension"} == set(task.output_names)


def test_bfi_with_output_entities():
    output_entities = {"sub": "sub", "run": "run"}
    task = utils.parse_bids_name(output_entities=output_entities)

    assert set(output_entities.keys()).issubset(task.output_names)


def test_bdr_defaults():
    task = utils.read_bids_dataset()

    assert "dataset_path" in task.input_names
    assert {"participant_id", "session_id"}.issubset(task.input_names)
    assert "dataset_description" in task.output_names


def test_bdr_with_output_queries():
    output_queries = {"T1w": {"suffix": "T1w"}, "bold": {"suffix": "bold"}}
    task = utils.read_bids_dataset(output_queries=output_queries)

    assert set(output_queries.keys()).issubset(task.output_names)
