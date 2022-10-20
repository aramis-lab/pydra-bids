import pydra.tasks.bids.utils as utils


def test_bdr_defaults():
    task = utils.BIDSDataReader().to_task(name="test")

    assert "dataset_path" in task.input_names
    assert {"T1w", "bold"} == set(task.output_names)
