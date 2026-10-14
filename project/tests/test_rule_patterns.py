"""Smoke tests for the Section 7.3 Q3 rule-pattern harness."""

from pathlib import Path

from experiments.rule_patterns import CSV_FIELDS, measure_case, study_cases

from bpe_token_automata.dictionary import Dictionary, parse_dictionary_path

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_example2_zero_rules_has_no_steps() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    empty = Dictionary(())
    payload = measure_case("empty", empty, frozenset({b"a", b"b"}))
    assert payload["steps"] == []
    assert payload["summary"]["n_rules"] == 0


def test_example2_first_rule_is_self_merge() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    one = Dictionary(parsed.dictionary.rules[:1])
    payload = measure_case("example2_one", one, frozenset({b"a", b"b"}))
    assert len(payload["steps"]) == 1
    row = payload["steps"][0]
    for key in CSV_FIELDS:
        assert key in row
    assert row["self_merge"] is True
    assert int(row["baseline_n_fresh"]) >= 1
    assert int(row["compact_n_states"]) >= 1


def test_study_cases_smoke_excludes_realistic() -> None:
    cases = study_cases(include_realistic=False)
    names = {case["case"] for case in cases}
    assert "example2" in names
    assert "paper_example1_chain" in names
    assert "paper_example1_chain_o2_o3_off" in names
    assert "gpt2_prefix_250" not in names
    chain_on = next(case for case in cases if case["case"] == "paper_example1_chain")
    chain_off = next(
        case for case in cases if case["case"] == "paper_example1_chain_o2_o3_off"
    )
    on_states = chain_on["summary"]["compact_n_states_final"]
    off_states = chain_off["summary"]["compact_n_states_final"]
    assert on_states <= off_states
