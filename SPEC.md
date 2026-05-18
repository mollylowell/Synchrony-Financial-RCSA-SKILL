# Feature Specification: Synchrony Documentation Automation Skillset


**Owners**:  Molly Lowell , Whitney Robinson , Sheila Green  
**Input**: User description: "Agent skillset that turns technical repository artifacts into audit-ready compliance documentation using Claude Agent Skills architecture (SKILL.md + scripts + assets)"


---

## Overview

Synchrony Documentation Automation Skillset is an agent skillset that turns technical repository artifacts — schemas, code files, test catalogs, and control libraries — into audit-ready compliance documentation, delivered as structured markdown reports with citations, confidence scores, and validation checks.

It is designed primarily for Synchrony's documentation teams who need to generate data dictionaries from database schemas, and secondarily for risk/compliance teams who need to produce evidence-backed control narratives from repository artifacts. The skillset is built on the Claude Agent Skills architecture (SKILL.md + scripts + assets) and is optimized for audit readiness and risk detection rather than speed alone.

---

## Repository Structure

This is the canonical layout of the repository when all features across both skills (F1–F3 for Data Dictionary, F4–F6 for RCSA) are fully built. Each feature plan shows only its own files — refer to this section for the complete picture.

```
synchrony-doc-automation/                        # Repository root
│
├── .gitignore                                   # Excludes output/, __pycache__/, *.pyc, .env
│
├── skills/
│   ├── data-dictionary/                         # Skill 1 — Data Dictionary Generation
│   │   ├── SKILL.md                             # F1 — LLM instruction file
│   │   ├── scripts/                             # F2 — 6 Python pipeline scripts
│   │   │   ├── validate_input.py
│   │   │   ├── extract_fields.py
│   │   │   ├── attach_citations.py
│   │   │   ├── add_timestamps.py
│   │   │   ├── assemble_output.py
│   │   │   └── generate_qa_report.py
│   │   └── output/                              # F2 — created at runtime, NOT checked into repo
│   │       ├── data_dictionary.md               # Final deliverable
│   │       ├── qa_report.md                     # Final deliverable
│   │       └── intermediate/
│   │           ├── user_input.json
│   │           ├── validated_schema.json
│   │           ├── extracted_fields.json
│   │           ├── extraction_warnings.json     # Conditional — only if warnings exist
│   │           ├── llm_output.json
│   │           ├── merged_fields.json
│   │           └── timestamped_fields.json
│   │
│   └── rcsa/                                    # Skill 2 — RCSA Control Narrative Generation
│       ├── SKILL.md                             # F5 — LLM instruction file (agent skill)
│       ├── scripts/                             # F6 — 6 Python pipeline scripts
│       │   ├── validate_input.py                # Validates JSON inputs against F4 schemas
│       │   ├── build_registry.py                # Builds in-memory artifact registry
│       │   ├── map_evidence.py                  # Maps artifacts/tests to controls
│       │   ├── orchestrate_llm.py               # Formats evidence for LLM, handles degradation
│       │   ├── validate_citations.py            # Validates citations against registry
│       │   └── write_output.py                  # Populates templates, writes output files
│       ├── scripts/tests/                       # Development only — NOT delivered to Synchrony
│       │   ├── test_validate_input.py
│       │   ├── test_build_registry.py
│       │   ├── test_map_evidence.py
│       │   ├── test_orchestrate_llm.py
│       │   ├── test_validate_citations.py
│       │   ├── test_write_output.py
│       │   └── mocks/
│       │       ├── mock_llm_response_success.md
│       │       ├── mock_llm_response_malformed.md
│       │       └── mock_llm_response_empty.md
│       ├── assets/                              # F4 — Static asset package
│       │   ├── templates/
│       │   │   ├── rcsa_control_narratives_template.md
│       │   │   └── validation_report_template.md
│       │   ├── sample-data/
│       │   │   ├── sample_artifact_index.json
│       │   │   ├── sample_test_catalog.json
│       │   │   └── sample_control_library.json
│       │   └── citation_format.md
│       └── output/                              # F6 — created at runtime, NOT checked into repo
│           ├── rcsa_control_narratives.md       # Final deliverable
│           └── validation_report.md             # Final deliverable
│
├── assets/                                      # F3 — Data Dictionary static files
│   ├── data_dictionary_template.md
│   ├── qa_report_template.md
│   ├── sample_schema.json
│   ├── example_data_dictionary.md
│   ├── example_qa_report.md
│   └── glossary_template.json                   # P3 placeholder — not required for demo day
│
└── specs/                                       # Planning docs — NOT runtime files
    ├── f1-skill.md-data-dictionary/
    │   ├── plan.md
    │   ├── research.md
    │   ├── data-model.md
    │   ├── quickstart.md
    │   ├── contracts/
    │   │   ├── input-contract.md
    │   │   └── output-contract.md
    │   └── tasks.md
    ├── f2-scripts-data-dictionary/
    │   ├── plan.md
    │   ├── research.md
    │   ├── data-model.md
    │   ├── quickstart.md
    │   ├── contracts.md
    │   └── tasks.md
    ├── f3-assets-data-dictionary/
    │   ├── plan.md
    │   ├── research.md
    │   ├── data-model.md
    │   ├── quickstart.md
    │   ├── contracts.md
    │   └── tasks.md
    ├── f4-rcsa-assets/
    │   ├── plan.md
    │   ├── research.md
    │   ├── data-model.md
    │   ├── quickstart.md
    │   ├── contracts/
    │   └── tasks.md
    ├── 005-skill-rcsa/
    │   ├── plan.md
    │   ├── research.md
    │   ├── data-model.md
    │   ├── quickstart.md
    │   ├── contracts.md
    │   └── tasks.md
    └── f6-rcsa-scripts/
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── contracts/
        └── tasks.md
```

**Notes:**

- `output/` directories under both `skills/data-dictionary/` and `skills/rcsa/` are created at runtime by their respective scripts. They are not checked into the repository.
- Data Dictionary assets (`assets/`) are at the repository root. RCSA assets are co-located inside `skills/rcsa/assets/` because F4, F5, and F6 form a single agent skill.
- `specs/` contains planning documentation only. Nothing in `specs/` is read at runtime.
- For demo day, the LLM step is performed manually via Claude Desktop. No programmatic API calls are made.
- RCSA scripts use Python 3.11 standard library only — zero third-party dependencies.
- All `output/` directories must be in `.gitignore`.

---

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories are PRIORITIZED as user journeys ordered by importance.
  Each user story/journey is INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  P1 stories are required for the May 7th demo.
  P2 stories are documented for future implementation.
  P3/P4 stories are nice-to-haves.
-->

### User Story 1 — Generate a Data Dictionary (Priority: P1)

A documentation team member provides a schema file in JSON format. The skillset processes the schema and returns a complete data dictionary containing field-level metadata — name, type, constraints, plain-language description, citation, confidence score, and last_verified timestamp — along with a QA report flagging any items needing clarification.

> **Note:** YAML and DDL input formats are documented as future extensions but are not supported for the May 7th demo.

**Why this priority**: This is one of two core end-to-end workflows required for the May 7th demo. A working P1 is a shippable MVP that demonstrates the full artifact-to-documentation pipeline.

**Independent Test**: Can be fully tested by providing a sample schema file and verifying the returned data dictionary contains all required fields for every column in the schema, plus a QA report with coverage stats.

**Acceptance Scenarios**:

1. **Given** a valid JSON schema file, **When** the user invokes the skill, **Then** the system returns a `data_dictionary.md` with all required fields: field_name, type, nullable, constraints/enums, description, source_path(s), evidence_refs, confidence, and last_verified.
2. **Given** a valid schema file, **When** the data dictionary is generated, **Then** every field description includes a citation to the source schema artifact.
3. **Given** valid inputs, **When** the skill completes, **Then** the system also produces a `qa_report.md` showing coverage stats and any [NEEDS CLARIFICATION] items.

---

### User Story 2 — Generate RCSA Control Narratives (Priority: P1)

A risk/compliance team member provides repository artifacts (artifact index, test catalog, and control library — all JSON). The skillset maps evidence to four generic compliance controls (Access Control, Change Management, Data Quality, Incident Handling), generates citation-backed narratives for each control — explicitly flagging gaps where no evidence exists — and produces a validation report showing citation resolution stats.

**Why this priority**: This is the second core end-to-end workflow required for the May 7th demo. It demonstrates the skillset's ability to assess audit readiness and flag risk, which is the primary value proposition for Synchrony.

**Independent Test**: Can be fully tested by providing sample artifact index + test catalog + control library and verifying the returned control narratives address all four controls with citations, gap flags where appropriate, and a validation report with resolution stats.

**Acceptance Scenarios**:

1. **Given** valid inputs (artifact index, test catalog, control library), **When** the user invokes the skill, **Then** the system returns `rcsa_control_narratives.md` with a summary table and per-control narratives (3–5 sentences each) with inline citations using `[file_path — description]` format.
2. **Given** valid inputs where one control has no supporting evidence, **When** the skill completes, **Then** the system explicitly flags that control as a "Gap" — the system MUST NOT imply compliance without proof.
3. **Given** valid inputs, **When** the skill completes, **Then** every citation in the narratives resolves to a real artifact in the index.
4. **Given** valid inputs, **When** the skill completes, **Then** the system also produces a `validation_report.md` showing citation resolution stats (total, valid, invalid, coverage %).
5. **Given** valid inputs but the LLM is unavailable or returns a malformed response, **When** the skill runs, **Then** the system enters graceful degradation mode — producing `rcsa_control_narratives.md` populated with raw mapped evidence only (no LLM-generated narratives) and `validation_report.md` noting "LLM unavailable — raw evidence mode."

---

### User Story 3 — Generate Pipeline Documentation (Priority: P2)

A documentation team member provides a codebase or pipeline definition. The skillset generates step-by-step documentation explaining inputs, outputs, transformations, and assumptions — with citations linking each documented step to the source code.

**Why this priority**: Validates the skillset's ability to extend beyond compliance documentation into general technical documentation. Independently demonstrable without needing the RCSA or data dictionary pipelines.

**Independent Test**: Can be fully tested by providing a sample codebase or pipeline definition and verifying the returned documentation covers all pipeline steps with citations to source code.

**Acceptance Scenarios**:

1. **Given** a valid codebase or pipeline definition, **When** the user invokes the skill, **Then** the system returns `pipeline_documentation.md` with step-by-step documentation covering inputs, outputs, transformations, and assumptions.
2. **Given** valid inputs, **When** the documentation is generated, **Then** every documented step includes a citation to the corresponding source code.

---

### User Story 4 — Generate Test Evidence Summary (Priority: P2)

A documentation team member provides test results (pass/fail, coverage stats). The skillset generates a summary of test execution results — total tests, passed, failed, coverage percentage — with links to corresponding test files and code under test.

**Why this priority**: Validates the skillset's ability to produce test-focused audit evidence. Uses similar inputs as the RCSA skill (test catalogs), demonstrating reuse of the artifact-to-doc pattern.

**Independent Test**: Can be fully tested by providing sample test results and verifying the returned summary accurately reflects pass/fail counts and links each result to its test file.

**Acceptance Scenarios**:

1. **Given** valid test results, **When** the user invokes the skill, **Then** the system returns `test_evidence_summary.md` with total tests, passed, failed, and coverage %.
2. **Given** valid inputs, **When** the summary is generated, **Then** every test result links to the corresponding test file and code under test.

---

### User Story 5 — DOCX Output Format (Priority: P3)

A user generates any document and requests DOCX format. The system produces the same content in DOCX in addition to Markdown.

**Why this priority**: A simple output format extension. Independently demonstrable in isolation, but represents the lowest complexity increment over Stories 1–4.

**Independent Test**: Can be fully tested by generating a data dictionary and requesting DOCX output, then verifying the DOCX contains identical content to the Markdown version.

**Acceptance Scenarios**:

1. **Given** a completed document generation, **When** the user requests DOCX format, **Then** the system produces a `.docx` file with identical content to the Markdown version.

---

### User Story 6 — Glossary Mapping (Priority: P3)

A documentation team member provides a glossary alongside a schema file. The system maps field names to consistent glossary labels in the data dictionary, ensuring organizational terminology is applied uniformly.

**Why this priority**: Validates the optional input layer for data dictionary generation. Independently demonstrable without changing the core pipeline.

**Independent Test**: Can be fully tested by providing a schema + glossary and verifying field names are mapped to their corresponding glossary labels in the output.

**Acceptance Scenarios**:

1. **Given** a schema file and a glossary, **When** the data dictionary is generated, **Then** field names are mapped to their corresponding glossary labels.

---

### User Story 7 — Change Detection (Priority: P4)

A documentation team member provides a current schema and a prior version. The system produces a `changes.md` showing added, removed, and modified fields with concise notes.

**Why this priority**: A nice-to-have diff feature. Independently demonstrable but not required for any other story.

**Independent Test**: Can be fully tested by providing a current and prior schema and verifying `changes.md` accurately reflects the differences.

**Acceptance Scenarios**:

1. **Given** a current schema and a prior version, **When** the skill completes, **Then** the system produces `changes.md` showing added, removed, and modified fields with concise notes.

---

### Edge Cases

- **Invalid schema format**: System rejects the input with a clear error message listing valid formats and allows the user to correct without restarting. For demo day, only JSON is supported; YAML and DDL return a clear message indicating they are planned for a future version.
- **Empty schema / no fields**: System returns an error explaining that the schema contains no extractable fields, rather than producing an empty data dictionary.
- **Missing optional inputs (glossary, profiling stats, prior version)**: System proceeds without them; output notes which optional inputs were not provided and which defaults were applied.
- **Control with no evidence**: System explicitly flags a "Gap" statement for that control — never implies compliance without proof. Gap flags must have zero false negatives.
- **All citations invalid**: System produces the validation report showing 0% resolution and flags the output as unreliable; does not suppress the report.
- **Schema with ambiguous or undocumented field names**: System generates best-effort descriptions and marks them as [NEEDS CLARIFICATION] with low confidence scores.
- **Extremely large schema (500+ fields)**: System processes all fields but may chunk the output; QA report notes total field count and processing completeness.
- **Duplicate field names in schema**: System flags duplicates in the QA report and includes both entries with a warning.
- **LLM unavailable or malformed response (RCSA)**: System enters graceful degradation mode — F6 scripts produce raw evidence output using F4 templates populated with extracted data only. No crash, no silent failure. Validation report notes the degradation.
- **Hallucinated citation in LLM output (RCSA)**: Citation is flagged with an inline marker (e.g., `⚠️ [ART-999] (unresolved)`) in the output narrative. Validation report shows count of hallucinated vs. valid citations. Pipeline completes — hallucinated citations are flagged, not silently removed.
- **Unsupported control code in control library**: System rejects the input with a clear error message identifying the unsupported control. Only AC, CM, DQ, IH are supported for demo.
- **Partial evidence for a control (RCSA)**: System generates narrative with available evidence, notes partial coverage, and assigns appropriate confidence tier (not "High"). Pipeline continues — partial evidence is valid, not an error.

---

## Features

### Skill 1 — Data Dictionary Generation

| Feature | Name | Responsibility | Simple Version | Functional Requirements |
|---|---|---|---|---|
| **F1** | SKILL.md — Data Dictionary | Descriptions, confidence scores, clarification flags, glossary interpretation | The LLM thinks | FR-007, FR-008, FR-009, FR-011 |
| **F2** | Scripts — Data Dictionary | Parsing, extracting, validating, citing, timestamping, counting, assembling | The code works | FR-001, FR-005, FR-006, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013 |
| **F3** | Assets — Data Dictionary | Templates that define what the outputs look like | The blank forms | FR-012, FR-013 |

### Skill 2 — RCSA Control Narrative Generation

| Feature | Name | Responsibility | Simple Version | Functional Requirements |
|---|---|---|---|---|
| **F4** | Assets — RCSA | Output templates (narratives + validation report), sample input data (artifact index, test catalog, control library), citation format specification, and control library defining the 4 controls and 11 evidence types. Formalizes the output structures and input contracts for F5 and F6. Zero runtime dependencies. | The blank forms + sample data | FR-021, FR-022 |
| **F5** | SKILL.md — RCSA | Natural language instruction file that orchestrates the 6-step RCSA workflow: validate → build registry → map evidence → generate narratives → validate citations → assemble output. Calls F6 scripts as tools, reasons over structured data, generates auditor-friendly narratives with inline citations, flags gaps, assigns confidence tiers (HIGH / MEDIUM / LOW). | The LLM thinks | FR-015, FR-016, FR-017, FR-018 |
| **F6** | Scripts — RCSA | Deterministic Python 3.11 pipeline (6 scripts, stdlib only). Pre-LLM: validates JSON inputs against F4 schemas, builds in-memory artifact registry, maps evidence to controls. Post-LLM: validates citations against registry, populates F4 templates, writes final Markdown deliverables. Handles graceful degradation when LLM is unavailable. Scripts invoked individually by SKILL.md agent — no standalone pipeline runner. | The code works | FR-002, FR-003, FR-004, FR-005, FR-015, FR-016, FR-019, FR-020, FR-021, FR-022 |

### Build Order

| Order | Feature | Rationale |
|---|---|---|
| 1 | F1 — SKILL.md: Data Dictionary | Understand what the LLM needs to do first |
| 2 | F2 — Scripts: Data Dictionary | Build the code that supports the LLM work |
| 3 | F3 — Assets: Data Dictionary | Create the templates that define output format (completes Skill 1) |
| 4 | F4 — Assets: RCSA | Establish the static foundation — templates, sample data, control library, and citation format that F5 and F6 depend on |
| 5 | F5 — SKILL.md: RCSA | Define the LLM orchestration instructions that reference F4 assets and call F6 scripts |
| 6 | F6 — Scripts: RCSA | Build the deterministic pipeline that validates inputs against F4 schemas, supports F5 orchestration, and produces final outputs (completes Skill 2) |

**Skill 2 Build Order Rationale:** Unlike Skill 1 (which built SKILL.md first), Skill 2 builds Assets (F4) first because the RCSA skill's templates, sample data schemas, and citation format must be locked before F5 can reference them and F6 can validate against them. F4 is the single source of truth for output formatting and control definitions.

### Cross-Feature Dependencies (Skill 2)

| Upstream | Downstream | What's Shared | Contract |
|---|---|---|---|
| F4 (Assets) | F5 (SKILL.md) | Asset file paths, YAML front matter fields, template structure, citation format syntax | Directory structure and templates locked in F4 plan |
| F4 (Assets) | F6 (Scripts) | Control library JSON schema, artifact index + test catalog JSON schemas, template placeholder syntax, sample data for integration testing | JSON schemas and placeholder format locked in F4 plan |
| F5 (SKILL.md) | F6 (Scripts) | LLM response structure, script invocation sequence | Cross-feature contract defined in F5 and F6 plans |

### Cross-Feature Re-validation Gates (Skill 2)

1. **After F5 build** → Verify F5's LLM output instructions match F4's template fields and citation format. Reconcile mismatches.
2. **After F6 plan approval** → Verify F6's input expectations match F4's sample data and JSON schemas. **Blocking gate** — F6 implementation cannot start until this passes.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept schema extracts in JSON format as input for data dictionary generation. YAML and DDL input support is documented as a future extension.
- **FR-002**: System MUST accept artifact indexes (JSON) listing all discovered files, functions, and classes in a repository
- **FR-003**: System MUST accept test catalogs (JSON) listing test names, file paths, and pass/fail status
- **FR-004**: System MUST accept a control library (JSON) defining controls, objectives, and expected evidence types
- **FR-005**: All input validation — file format, schema structure — MUST be handled by deterministic script logic before any LLM processing begins
- **FR-006**: System MUST extract all fields from a schema (field name, type, nullable, constraints/enums)
- **FR-007**: System MUST generate a plain-language description targeting ≤25 words for each field. Descriptions exceeding 25 words are flagged in the QA report but not truncated.
- **FR-008**: System MUST include a citation (source path, evidence refs) for every field description
- **FR-009**: System MUST assign a confidence score to each field description
- **FR-010**: System MUST include a last_verified timestamp for each field
- **FR-011**: If a glossary is provided, system MUST map field names to consistent glossary labels. Glossary mapping is a P3 feature — not included for demo day.
- **FR-012**: System MUST produce `data_dictionary.md` as the primary output; structure and formatting enforced by a defined output template. CSV output format is documented as a future extension.
- **FR-013**: System MUST produce `qa_report.md` showing coverage stats, confidence distribution breakdown (High, Medium, Low, N/A counts with percentages), and flagged items
- **FR-014**: If a prior version is provided, system MAY produce `changes.md` showing added/removed/modified fields
- **FR-015**: System MUST scan a repository and build an index of all artifacts (code files, tests, configs)
- **FR-016**: System MUST map discovered evidence to defined controls (Access Control, Change Management, Data Quality, Incident Handling)
- **FR-017**: System MUST generate auditor-friendly narratives (3–5 sentences per control) with inline citations using `[file_path — description]` format
- **FR-018**: System MUST explicitly flag a "Gap" statement when no evidence exists for a control — system MUST NOT imply compliance without proof. Gap flags must have zero false negatives.
- **FR-019**: System MUST validate that every citation resolves to a real artifact in the index; hallucinated citations are flagged with inline markers, not silently removed
- **FR-020**: System MUST produce a summary table showing which controls have evidence vs. gaps, including confidence tiers (HIGH / MEDIUM / LOW)
- **FR-021**: System MUST produce `rcsa_control_narratives.md` as the primary output; structure and formatting enforced by F4's output template with YAML front matter, summary table, and per-control sections
- **FR-022**: System MUST produce `validation_report.md` showing citation resolution stats (total, valid, invalid, coverage %), citation index, evidence coverage per control, and flagged-for-human-review items
- **FR-023**: System MUST accept a codebase or pipeline definition as input
- **FR-024**: System MUST generate step-by-step documentation explaining inputs, outputs, transformations, and assumptions of a pipeline
- **FR-025**: System MUST include citations linking each documented step to the source code
- **FR-026**: System MUST produce `pipeline_documentation.md` as the primary output; structure and formatting enforced by a defined output template
- **FR-027**: System MUST accept test results (pass/fail, coverage stats) as input
- **FR-028**: System MUST generate a summary of test execution results (total tests, passed, failed, coverage %)
- **FR-029**: System MUST link each test result to the corresponding test file and code under test
- **FR-030**: System MUST produce `test_evidence_summary.md` as the primary output; structure and formatting enforced by a defined output template
- **FR-031**: All primary outputs MUST be in Markdown format
- **FR-032**: System MAY support optional DOCX output format

### FR-to-Feature Traceability (Skill 2)

| FR | F4 (Assets) | F5 (SKILL.md) | F6 (Scripts) | Notes |
|---|---|---|---|---|
| FR-002 | | | ✅ | `validate_input.py` accepts artifact index JSON |
| FR-003 | | | ✅ | `validate_input.py` accepts test catalog JSON |
| FR-004 | | | ✅ | `validate_input.py` accepts control library JSON |
| FR-005 | | | ✅ | `validate_input.py` runs before LLM processing |
| FR-015 | | ✅ | ✅ | `build_registry.py` (F6) builds index; F5 orchestrates |
| FR-016 | | ✅ | ✅ | `map_evidence.py` (F6 deterministic) + F5 (LLM reasoning) |
| FR-017 | | ✅ | | F5 instructs LLM to generate narratives |
| FR-018 | | ✅ | | F5 instructs LLM to flag gaps — zero false negatives |
| FR-019 | | | ✅ | `validate_citations.py` checks every citation |
| FR-020 | | | ✅ | `write_output.py` produces summary table |
| FR-021 | ✅ | | ✅ | F4 provides template; F6 populates and writes it |
| FR-022 | ✅ | | ✅ | F4 provides template; F6 populates and writes it |

### Key Entities

#### P1 — Demo Day (Stories 1 & 2)

- **Schema Extract** — A JSON file containing database/table field definitions (column names, types, constraints, nullability). Primary input for data dictionary generation. JSON format required for demo day; YAML and DDL support documented as future extension.
- **Artifact Index** — A JSON file listing all discovered files, functions, and classes in a repository. Each artifact has `id`, `file_path` (relative), `file_type`, `description`, and optional `lines` field. Primary input for RCSA. Demo scale: 10–20 artifacts.
- **Test Catalog** — A JSON file listing test names, file paths, file types, descriptions, and `controls_relevant` (self-documenting hint mapping tests to controls). Input for RCSA. Demo scale: 5–10 tests.
- **Control Library** — A JSON file defining the four generic compliance controls (AC, CM, DQ, IH), their objectives, and expected evidence types (11 total). Each control includes `id`, `name`, `objective`, and `evidence_types` array. Input for RCSA.
- **Data Dictionary** — Generated Markdown document containing field-level metadata: field_name, type, nullable, constraints/enums, description (≤25 words), source_path(s), evidence_refs, confidence, and last_verified. Primary output of Skill 1.
- **Control Narrative** — Auditor-friendly 3–5 sentence paragraph per compliance control, with inline citations using `[file_path — description]` format. Explicitly flags gaps. Includes confidence tier (HIGH / MEDIUM / LOW). Primary output of Skill 2.
- **QA Report** — Coverage statistics, confidence distribution breakdown, citation checks, and [NEEDS CLARIFICATION] items. Produced alongside the data dictionary.
- **Validation Report** — Citation resolution statistics (total, valid, invalid, coverage %), citation index table, evidence coverage per control, and flagged-for-human-review section. Produced alongside RCSA control narratives.
- **Citation Format** — Standardized syntax: `[file_path — description]` where `file_path` is relative and `description` is a brief human-readable label. Em dash ` — ` (space-emdash-space) separates path from description. Defined in F4's `citation_format.md`.

#### P2 — Documented for Future (Stories 3 & 4)

- **Pipeline Definition** — Codebase or pipeline configuration file describing data flow steps, transformations, inputs, and outputs.
- **Test Results** — Test execution results including pass/fail status and coverage statistics.
- **Pipeline Documentation** — Generated step-by-step Markdown document with citations to source code.
- **Test Evidence Summary** — Generated Markdown summary of test execution results with links to test files.

#### P3 — Future (Story 5)

- **Doc Pack** — Complete bundle of all generated documents from a single repository input.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### Demo Day (P1)

- **SC-001**: Time to generate a data dictionary is reduced from 60–120 min (manual) to ~5–10 min per repo
- **SC-002**: ≥ 95% of fields in the source schema are correctly extracted and present in the generated data dictionary
- **SC-003**: ≥ 90% of field descriptions include a citation to the source schema artifact
- **SC-004**: ≥ 90% of template sections are populated in every generated data dictionary
- **SC-005**: ≥ 85% of true compliance gaps are correctly flagged in RCSA control narratives
- **SC-006**: ≤ 5% of controls or tests referenced in RCSA narratives are invented (not in source artifacts)
- **SC-007**: ≥ 90% of citations in RCSA control narratives resolve to real artifacts
- **SC-008**: ≥ 3 out of 4 compliance controls addressed (with evidence or explicit gap flag) in every RCSA run
- **SC-009**: ≥ 90% structural match when the same skill is run on the same inputs multiple times
- **SC-010**: AI-generated documentation scores ≥ 80% on evaluation rubric vs. human-written ground truth

#### Future (P2/P3, Not Measured for Demo Day)

- **SC-011**: ≥ 90% of pipeline steps documented with inputs, outputs, and transformations
- **SC-012**: ≥ 90% of documented pipeline steps include a citation to source code
- **SC-013**: ≥ 95% of pass/fail counts in test evidence summary match actual test results
- **SC-014**: ≥ 90% of test results linked to corresponding test file and code under test
- **SC-015**: ≥ 90% of applicable document types generated when Doc Pack is invoked

#### Skill 2 — Performance Gates

- **SC-016**: Gap detection — ≥ 85% of true gaps correctly flagged (tested with known-gap inputs)
- **SC-017**: Citation accuracy — ≥ 95% of citations reference real artifacts (measured by F6 `validate_citations` output)
- **SC-018**: Control coverage — 4/4 (100%) controls addressed per run
- **SC-019**: Structural consistency — ≥ 90% match across repeated runs (same input 5x)
- **SC-020**: Narrative quality — ≥ 80% rubric score vs. human-written ground truth
- **SC-021**: Pipeline speed — < 60 seconds for deterministic processing at demo scale

---

## Skill 2 — RCSA Technical Reference

### Architecture

The RCSA skill follows the Claude Agent Skills architecture: **SKILL.md** (F5) orchestrates **Scripts** (F6) and references **Assets** (F4). The SKILL.md is the conductor — it calls scripts as tools and reasons over the structured data they return.

**Pipeline Flow:**

```
1. validate_input.py    (F6)  →  Validates JSON inputs against F4 schemas
2. build_registry.py    (F6)  →  Builds in-memory artifact registry
3. map_evidence.py      (F6)  →  Maps artifacts/tests to controls, flags gaps
4. orchestrate_llm.py   (F6)  →  Formats evidence for LLM consumption
5. SKILL.md             (F5)  →  LLM generates narratives, assigns confidence, flags gaps
6. validate_citations.py(F6)  →  Validates every citation against registry
7. write_output.py      (F6)  →  Populates F4 templates, writes final deliverables
```

### Controls (Demo Scope)

| Control ID | Control Name | Objective | Evidence Types |
|---|---|---|---|
| **AC** | Access Control | Ensure system access is restricted to authorized users through authentication, authorization, and session management | `auth_config`, `rbac_policy`, `session_management` |
| **CM** | Change Management | Ensure all changes to production systems follow approved processes with rollback capability | `change_approval_record`, `deployment_config`, `rollback_procedure` |
| **DQ** | Data Quality | Ensure data inputs are validated and transformations preserve integrity | `input_validation_rule`, `data_transform_test` |
| **IH** | Incident Handling | Ensure security incidents are detected, responded to, and reviewed | `monitoring_config`, `incident_response_plan`, `postmortem_record` |

### Confidence Tiers

| Tier | Criteria |
|---|---|
| **HIGH** | ≥ 2 artifacts AND ≥ 1 test mapped, 0 hallucinated citations |
| **MEDIUM** | ≥ 1 artifact OR ≥ 1 test mapped, 0 hallucinated citations |
| **LOW** | Any evidence exists but hallucinated citations detected |
| **GAP** | No evidence mapped to this control |

### Graceful Degradation

If the LLM is unavailable or returns a malformed response, F6 scripts produce raw evidence output using F4 templates populated with extracted data only. The validation report notes "LLM unavailable — raw evidence mode." Pre-LLM scripts (validate_input, build_registry, map_evidence) function independently of LLM availability. No crash, no silent failure.

### Sample Data Coverage Design

F4 sample data is intentionally designed with specific coverage patterns to test gap detection:

| Control | Sample Evidence Provided | Intentional Gaps |
|---|---|---|
| **AC** | All 3 types present | None — full coverage |
| **CM** | All 3 types present | None — full coverage |
| **DQ** | `input_validation_rule` present | `data_transform_test` missing — gap flagged |
| **IH** | `monitoring_config` present | `incident_response_plan` and `postmortem_record` missing — gaps flagged |

### Demo-Scale Constraints

- 10–20 artifacts in sample artifact index
- 5–10 tests in sample test catalog
- 4 controls in control library (AC, CM, DQ, IH)
- 11 evidence types total
- < 60 seconds for deterministic pipeline portions
- Python 3.11 standard library only — zero third-party dependencies
- All files UTF-8 encoded
- No PII, secrets, or real Synchrony identifiers in sample data

### Open Research Questions (F6)

These require team decisions before F6 implementation begins:

| RQ | Topic | Status | Impact |
|---|---|---|---|
| RQ-001 | How data flows between F6 scripts via the SKILL.md agent | Needs team input | Blocks F6 Phase 1 design |
| RQ-002 | Exact citation format F5 will produce | Cross-feature contract | Blocks `validate_citations.py` design |
| RQ-003 | LLM response structure (free-form, delimited, or JSON) | Cross-feature contract | Blocks `orchestrate_llm.py` design |
| RQ-004 | Confidence tier thresholds | Needs team review | Blocks `map_evidence.py` design |
| RQ-005 | Exact F4 schema structures | Blocked by F4 completion | Blocks `validate_input.py` implementation |

### Testing Strategy (Skill 2)

**F4 (Assets)** — Two-tier validation:
- Tier 1 (during F4 dev): JSON parse checks, schema field verification, UTF-8 encoding, directory inventory
- Tier 2 (after F6): F6's input validator and output assembler consume F4 assets end-to-end

**F6 (Scripts)** — Three-tier validation:
- Tier 1 (unit): Each script tested independently with valid/invalid inputs. No LLM required.
- Tier 2 (integration with mocks): Full pipeline with mocked LLM responses (success, malformed, empty). Verifies graceful degradation.
- Tier 3 (end-to-end): Full pipeline with live LLM via F5 in Cursor. Requires F5 integration.
