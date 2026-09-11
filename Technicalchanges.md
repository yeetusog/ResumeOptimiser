# Technical Changes and Agent Tasks

## Overview
This document tracks the implementation of the immutable LaTeX resume tailoring pipeline. It is intentionally operational and engineering-focused so sub-agents can continue the work without re-reading the whole project history.

## Core architecture

### Required end-to-end flow
1. Static resume LaTeX source remains the canonical template.
2. Parse editable content into discrete text nodes with source spans.
3. Analyze job description for prioritized requirements.
4. Match candidate evidence to JD requirements with strict grounding rules.
5. Ask the user for proficiency only when required.
6. LLM generates replacement objects only, never full LaTeX.
7. Deterministic patcher applies replacements to the original source.
8. Structural diff ensures only editable text changed.
9. Compile the validated document to PDF.
10. Compute estimated ATS match score.

## Design guardrails
- `resume.tex` / the template is immutable except for editable content. Never regenerate protected LaTeX structure.
- LLMs may optimize wording only; patching is the document builder.
- Candidate evidence is the source of truth and blocks unsupported claims.
- Web research only improves terminology; it is never evidence of prior experience.
- Structural diff must fail on protected-region changes before compile.

## Relevant project files
- [backend/app/main.py](backend/app/main.py) — API orchestration and LLM integration
- [backend/app/ats.py](backend/app/ats.py) — ATS, keyword extraction, JD analysis hook
- [backend/app/parser.py](backend/app/parser.py) — document extraction and editable content parsing
- [backend/app/compiler.py](backend/app/compiler.py) — LaTeX rendering and PDF compilation
- [backend/app/sanitizer.py](backend/app/sanitizer.py) — LaTeX escaping safety
- [backend/app/templates/resume.tex.j2](backend/app/templates/resume.tex.j2) — canonical static template
- [frontend/src/App.jsx](frontend/src/App.jsx) — current client flow
- [tests/test_e2e_pipeline.py](tests/test_e2e_pipeline.py) — regression tests

## Phase plan

### Phase 0: Repository audit
- Completed: repository audit recorded and architecture map documented.
- Remaining: ensure all later work follows the documented immutable-template rule.

### Phase 1: Parse editable content
- Goal: convert a LaTeX source into editable text nodes with source spans while preserving the original source exactly.
- Required outputs:
  - `parse_editable_content(source: str) -> list[dict]`
  - `reconstruct_latex(source: str, nodes: list[dict]) -> str`
- Acceptance:
  - reconstruction equals original for valid template input
  - protected regions remain untouched
  - editable spans are explicit and machine-readable
- Tests to add:
  - extraction
  - source positions
  - protected-region handling
  - reconstruction fidelity
  - template compatibility with current resume structure

### Phase 2: JD analysis
- Goal: extract prioritized JD requirements.
- Required schema:
  - `title`
  - `required_skills`
  - `preferred_skills`
  - `tools`
  - `languages`
  - `frameworks`
  - `responsibilities`
  - `qualifications`
  - `keywords`
  - `synonyms`
- Rank: P1, P2, P3.
- Keep compact intermediate output.

### Phase 3: Candidate content matching
- Goal: match resume evidence to JD requirements without hallucination.
- Classify each requirement as EXACT_MATCH, PARTIAL_MATCH, IMPLIED_MATCH, VALIDATION_REQUIRED, or UNSUPPORTED.
- Grounding is mandatory before generation.

### Phase 4: Web research
- Goal: improve terminology and standard expectations only.
- Use official docs and credible sources.
- Never use research as proof of candidate experience.

### Phase 5: User validation
- Goal: ask only when proficiency is missing.
- Exactly five levels:
  1. Familiarity
  2. Working knowledge
  3. Proficient
  4. Advanced
  5. Expert
- Do not ask broad questions or request bullet rewrites.

### Phase 6: LLM content optimization
- Goal: LLM emits replacement objects only.
- Inputs: JD context, matched evidence, existing text, validated proficiency.
- Output schema: replacement objects with `id`, `original`, `replacement`, `keywords`, `reason`.
- Must never output full LaTeX, full resume text, or unsupported facts.

### Phase 7: Deterministic patcher
- Goal: apply replacements to original LaTeX only in editable spans.
- Rules:
  - exact ID match required
  - edits confined to editable regions
  - reject ambiguity and missing IDs
  - preserve layout, spacing, structure, and protected text

### Phase 8: Structural diff
- Goal: validate the tailored document differs only in editable content.
- Output object example:
  ```json
  {
    "valid": true,
    "changed_editable_nodes": 6,
    "protected_changes": 0
  }
  ```
- Compile is forbidden until diff passes.

### Phase 9: Compile and PDF generation
- Goal: compile the validated LaTeX and verify output PDF exists.
- Must identify and repair content problems without modifying template structure.

### Phase 10: ATS scoring
- Goal: calculate estimated ATS match score from P1/P2 coverage and contextual alignment.
- Label clearly as `Estimated ATS Match Score`.

### Phase 11: End-to-end testing
- Goal: confirm no regression across the full app.
- Add tests for:
  - parser fidelity
  - JD requirements extraction
  - matching logic
  - validation behavior
  - patch determinism
  - structural diff enforcement
  - compile success
  - API compatibility

## Handoff notes for sub-agents
- Do not rebuild or replace existing working functionality.
- Implement one phase at a time and validate before moving on.
- Prefer small, focused edits with regression tests.
- Keep the static template source canonical and immutable.
- Use deterministic patching and diff guards as the final protection layer.

## Execution guidance
- Current focus: Phase 1 parser implementation and test coverage.
- Next agent action: implement editable-content parsing and source-span reconstruction, then run the specific Phase 1 test file.
- Follow the project’s TDD approach: failing test first, then implementation, then validation.
