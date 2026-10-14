.PHONY: install test test-dict test-reference test-dfa test-transducer test-compact test-extensions test-section6 demo lint format format-check typecheck check \
	5.1 reference_tokenizer 5.2 token_dfa 5.3 examples 5.4 transducer 5.5 compact \
	5.6 timeout_study 6 tests 7 experiments 8.2 dictionary_equivalence \
	8.6 partial_order 8.11 pattern_match

SECTION_NAMES := 5.1 reference_tokenizer 5.2 token_dfa 5.3 examples 5.4 transducer \
	5.5 compact 5.6 timeout_study 6 tests 7 experiments 8.2 dictionary_equivalence \
	8.6 partial_order 8.11 pattern_match
SELECTED := $(filter $(SECTION_NAMES),$(MAKECMDGOALS))
ifneq ($(SELECTED),)
  SECTION_FILES := $(filter-out $(SECTION_NAMES),$(MAKECMDGOALS))
  ifneq ($(strip $(SECTION_FILES)),)
    $(foreach file,$(SECTION_FILES),$(eval $(file):;@:))
    .PHONY: $(SECTION_FILES)
  endif
endif
section_args = $(foreach file,$(if $(strip $(SECTION_FILES)),$(SECTION_FILES),$(INPUT)),"$(file)") $(if $(TEXT),--text "$(TEXT)",) $(if $(PATTERN),--pattern "$(PATTERN)",)

define run_section
@uv run python scripts/section.py $@ $(section_args)
endef

# Install the package and locked development dependencies via uv.
install:
	uv sync

# Run the pytest suite (includes coverage via pyproject.toml addopts).
test:
	uv run pytest

test-dict:
	uv run pytest --no-cov -q tests/test_dictionary_parser.py tests/test_dictionary_validator.py tests/test_tokens.py

test-reference:
	uv run pytest --no-cov -q tests/test_reference_tokenizer.py

test-dfa:
	uv run pytest --no-cov -q tests/test_token_dfa_construction.py tests/test_token_dfa_examples.py tests/test_token_dfa_unicode.py

test-transducer:
	uv run pytest --no-cov -q tests/test_transducer_tokenize.py tests/test_transducer_observation.py tests/test_transducer_determinize.py

test-compact:
	uv run pytest --no-cov -q tests/test_compact_construction.py tests/test_compact_equivalence.py

test-extensions:
	uv run pytest --no-cov -q tests/test_extensions.py tests/test_partial_order.py

test-section6:
	uv run pytest --no-cov -q

demo:
	uv run python scripts/demo.py walkthrough

5.1 reference_tokenizer:
	$(run_section)

5.2 token_dfa:
	$(run_section)

5.3 examples:
	$(run_section)

5.4 transducer:
	$(run_section)

5.5 compact:
	$(run_section)

5.6 timeout_study:
	$(run_section)

6 tests:
	$(run_section)

7 experiments:
	$(run_section)

8.2 dictionary_equivalence:
	$(run_section)

8.6 partial_order:
	$(run_section)

8.11 pattern_match:
	$(run_section)

# Lint the project with Ruff (no file modifications).
lint:
	uv run ruff check .

# Apply Ruff formatting to source and tests.
format:
	uv run ruff format .

# Verify Ruff formatting without writing changes.
format-check:
	uv run ruff format --check .

# Run mypy static type checks over src and tests.
typecheck:
	uv run mypy src tests

# Run all non-mutating quality checks (format, lint, types, tests).
check: format-check lint typecheck test
