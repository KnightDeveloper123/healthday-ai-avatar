from app.evaluation.language_eval import evaluate


def test_eval_set_is_large_enough_and_meets_threshold() -> None:
    report = evaluate()
    assert report["total"] >= 20
    assert report["all_fields_accuracy"] >= 0.9, report["failures"]