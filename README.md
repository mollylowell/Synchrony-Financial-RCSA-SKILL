# Synchrony Documentation Automation Skillset

**An AI-powered agent skillset that transforms technical repository artifacts into audit-ready compliance documentation.**

---

## Table of Contents

- [Overview](#overview)
- [What It Does](#what-it-does)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Skills & Workflows](#skills--workflows)
  - [Skill 1: Data Dictionary Generation](#skill-1-data-dictionary-generation)
  - [Skill 2: RCSA Control Narratives](#skill-2-rcsa-control-narratives)
- [Architecture](#architecture)
- [Component Inventory](#component-inventory)
- [Usage Examples](#usage-examples)
- [Quality Assurance](#quality-assurance)
- [Design Principles](#design-principles)
- [Known Risks & Limitations](#known-risks--limitations)
- [Roadmap & Future Extensions](#roadmap--future-extensions)
- [Demo Details](#demo-details)

---

## Overview

The **Synchrony Documentation Automation Skillset** is designed for financial institutions' documentation and risk/compliance teams. It automates the generation of audit-ready compliance documentation from technical artifacts—schemas, code files, test catalogs, and control libraries—reducing manual documentation effort from 60–120 minutes to 5–10 minutes while improving consistency, traceability, and audit readiness.

Built on the **Claude Agent Skills architecture**, the skillset combines deterministic Python scripts with AI-powered reasoning to produce structured markdown reports with citations, confidence scores, and validation checks.

This repository contains Skill 2 (RCSA Control Narrative Generation), owned and built by Molly Lowell. This skill is part of a larger two-skill Synchrony Documentation Automation Skillset built on Claude's Agent Skills architecture


---

## What It Does

The skillset accepts technical repository artifacts and produces two primary deliverables:

1. **Data Dictionary** — Complete field-level metadata with plain-language descriptions, confidence scores, citations, and clarification flags
2. **RCSA Control Narratives** — Evidence-backed control narratives mapping repository artifacts to compliance controls

Both outputs are:
- ✅ Audit-ready with full citation trails
- ✅ Confidence-scored (High/Medium/Low)
- ✅ QA-validated with coverage statistics
- ✅ Traceable to source code and evidence

---

## Key Features

### Skill 1: Data Dictionary Generation
- Accepts JSON schema files describing database tables
- Generates plain-language field descriptions (≤25 words)
- Produces confidence scores for each field
- Includes evidence citations linking descriptions to source metadata
- Flags fields requiring human clarification
- Outputs QA report with coverage statistics
- Optional comparison report against ground truth (UCI Credit Card dataset)

### Skill 2: RCSA Control Narratives
- Accepts three JSON files: artifact index, test catalog, control library
- Maps repository evidence to four generic controls:
  - Access Control
  - Change Management
  - Data Quality
  - Incident Handling
- Generates narrative descriptions with confidence scoring
- Validates all citations to source artifacts
- Produces QA report with gap analysis
- Supports graceful degradation when evidence is incomplete

### Cross-Skill Capabilities
- **Zero third-party dependencies** — Python 3.11 standard library only
- **Confidence tiers** — High/Medium/Low scoring with calibration
- **Citation validation** — Every claim links to source evidence
- **Graceful degradation** — Produces output even with incomplete input
- **Audit-ready output** — Structured markdown with validation metadata

---

## Project Structure

```
synchrony-doc-automation/
├── .gitignore
├── README.md                          ← You are here
├── skills/
│   ├── data-dictionary/               ← Skill 1
│   │   ├── SKILL.md                   ← F1: LLM instruction file
│   │   ├── scripts/                   ← F2: Python pipeline scripts
│   │   │   ├── validate_input.py
│   │   │   ├── extract_fields.py
│   │   │   ├── attach_citations.py
│   │   │   ├── generate_qa_report.py
│   │   │   └── assemble_output.py
│   │   ├── assets/                    ← F3: Templates and examples
│   │   │   ├── field_template.md
│   │   │   ├── qa_report_template.md
│   │   │   └── sample_schema.json
│   │   └── output/                    ← Generated files (.gitignore)
│   │       ├── intermediate/          ← Runtime intermediate files
│   │       └── final/                 ← Final deliverables
│   │
│   └── rcsa/                          ← Skill 2
│       ├── SKILL.md                   ← F5: LLM instruction file
│       ├── scripts/                   ← F6: Python pipeline scripts
│       │   ├── validate_input.py
│       │   ├── build_registry.py
│       │   ├── map_evidence.py
│       │   ├── generate_narratives.py
│       │   ├── validate_citations.py
│       │   └── assemble_output.py
│       ├── assets/                    ← F4: Templates and examples
│       │   ├── narrative_template.md
│       │   ├── qa_report_template.md
│       │   ├── sample_artifact_index.json
│       │   ├── sample_test_catalog.json
│       │   └── sample_control_library.json
│       └── output/                    ← Generated files (.gitignore)
│
├── docs/                              ← Detailed specifications
│   ├── data-dictionary-master.md
│   ├── rcsa-masterplan.md
│   ├── project-level-spec.md
│   └── proposal-1-pager.md
│
└── tests/                             ← Test data and validation
    ├── sample_data/
    └── gold_standard/
```

---

## Getting Started

### Prerequisites

- Python 3.11 (standard library only — no pip dependencies)
- JSON schema files (for Skill 1) or artifact/test/control JSON files (for Skill 2)
- Text editor or IDE for reviewing markdown output

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/whitneyrobinson-creator/Synchronyproject.git
   cd synchrony-doc-automation
   ```

2. Verify Python version:
   ```bash
   python --version  # Should be 3.11+
   ```

3. No additional dependencies to install — you're ready to go!

### Quick Start: Skill 1 (Data Dictionary)

1. Prepare your JSON schema file (see `skills/data-dictionary/assets/sample_schema.json` for format)
2. Run the pipeline:
   ```bash
   python skills/data-dictionary/scripts/validate_input.py your_schema.json
   python skills/data-dictionary/scripts/extract_fields.py
   python skills/data-dictionary/scripts/attach_citations.py
   python skills/data-dictionary/scripts/generate_qa_report.py
   python skills/data-dictionary/scripts/assemble_output.py
   ```
3. Review outputs in `skills/data-dictionary/output/final/`:
   - `data_dictionary.md` — Your complete data dictionary
   - `qa_report.md` — Quality and coverage statistics

### Quick Start: Skill 2 (RCSA Control Narratives)

1. Prepare three JSON files:
   - `artifact_index.json` — List of repository artifacts (10–20 for demo)
   - `test_catalog.json` — Test files and their control relevance (5–10 for demo)
   - `control_library.json` — Compliance controls to map against
2. Run the pipeline:
   ```bash
   python skills/rcsa/scripts/validate_input.py artifact_index.json test_catalog.json control_library.json
   python skills/rcsa/scripts/build_registry.py
   python skills/rcsa/scripts/map_evidence.py
   python skills/rcsa/scripts/generate_narratives.py
   python skills/rcsa/scripts/validate_citations.py
   python skills/rcsa/scripts/assemble_output.py
   ```
3. Review outputs in `skills/rcsa/output/final/`:
   - `rcsa_control_narratives.md` — Your control narratives
   - `qa_report.md` — Gap analysis and coverage statistics

---

## Skills & Workflows

### Skill 1: Data Dictionary Generation

**Purpose:** Transform database schemas into audit-ready data dictionaries in 5–10 minutes.

**Input:** JSON schema file with table metadata and field definitions

**Output:**
- `data_dictionary.md` — Complete data dictionary with:
  - Field name, type, constraints
  - Plain-language description (≤25 words)
  - Confidence score (High/Medium/Low)
  - Evidence citations
  - Clarification flags for fields needing human review
- `qa_report.md` — Coverage statistics and metadata availability summary
- `comparison_report.md` (optional) — Side-by-side comparison against ground truth

**Key Workflow Steps:**
1. **Validate Input** — Confirm schema structure and required keys
2. **Extract Fields** — Parse schema and standardize field metadata
3. **Attach Citations** — Link descriptions to source metadata signals
4. **Generate QA Report** — Calculate coverage, confidence distribution, and flags
5. **Assemble Output** — Produce final markdown documents

**Quality Metrics:**
- Completeness: All fields documented
- Description quality: Clear, concise, audit-ready
- Confidence calibration: Accurate High/Medium/Low scoring
- Citation coverage: Every description cites evidence
- Flag accuracy: Correct identification of fields needing clarification
- Consistency: Uniform formatting and terminology

---

### Skill 2: RCSA Control Narratives

**Purpose:** Map repository evidence to compliance controls and generate audit-ready control narratives.

**Input:** Three JSON files:
- `artifact_index.json` — Repository artifacts (code, tests, configs)
- `test_catalog.json` — Test files and control relevance
- `control_library.json` — Compliance controls (Access, Change Management, Data Quality, Incident Handling)

**Output:**
- `rcsa_control_narratives.md` — Control narratives with:
  - Narrative description for each control
  - Confidence scores
  - Evidence citations linking to artifacts and tests
  - Gap identification for controls with insufficient evidence
- `qa_report.md` — Gap analysis, coverage statistics, and validation summary

**Key Workflow Steps:**
1. **Validate Input** — Confirm all three JSON files have required structure
2. **Build Registry** — Create in-memory artifact and test registry
3. **Map Evidence** — Link artifacts and tests to controls
4. **Generate Narratives** — AI produces control descriptions with citations
5. **Validate Citations** — Verify all citations point to valid artifacts
6. **Assemble Output** — Produce final markdown documents

**Supported Controls:**
- **Access Control** — Who can access what, and how is access managed?
- **Change Management** — How are code and configuration changes controlled?
- **Data Quality** — How is data quality validated and monitored?
- **Incident Handling** — How are incidents detected and responded to?

---

## Architecture

### Three-Part Skill Design

Each skill follows the **Claude Agent Skills architecture**:

1. **SKILL.md (F1/F5)** — LLM instruction file
   - Defines reasoning tasks for Claude
   - Specifies output format and quality criteria
   - Includes confidence scoring rules and citation requirements

2. **Scripts (F2/F6)** — Deterministic Python pipeline
   - Handles all parsing, validation, and citation logic
   - Manages file I/O and data transformation
   - Validates AI output before assembly
   - No third-party dependencies (Python 3.11 stdlib only)

3. **Assets (F3/F4)** — Templates, examples, and sample data
   - Field and narrative templates
   - QA report templates
   - Sample input files for testing
   - Gold standard examples for comparison

### Design Philosophy

- **Deterministic work in code** — Parsing, validation, citing, timestamping
- **Reasoning work in AI** — Description generation, confidence scoring, gap analysis
- **Graceful degradation** — Produces output even with incomplete input
- **Audit-ready by design** — Every claim is cited, every score is justified
- **Zero external dependencies** — Portable, secure, reproducible

---

## Component Inventory

### Skill 1: Data Dictionary

| Component | Type | Purpose |
|-----------|------|---------|
| `SKILL.md` | LLM Instructions | Defines how Claude generates field descriptions and confidence scores |
| `validate_input.py` | Script | Validates JSON schema structure and required keys |
| `extract_fields.py` | Script | Parses schema and standardizes field metadata |
| `attach_citations.py` | Script | Links descriptions to source metadata signals |
| `generate_qa_report.py` | Script | Calculates coverage, confidence distribution, and flags |
| `assemble_output.py` | Script | Produces final markdown documents |
| `field_template.md` | Asset | Template for individual field entries |
| `qa_report_template.md` | Asset | Template for QA report structure |
| `sample_schema.json` | Asset | Example input schema (UCI Credit Card dataset) |

### Skill 2: RCSA Control Narratives

| Component | Type | Purpose |
|-----------|------|---------|
| `SKILL.md` | LLM Instructions | Defines how Claude generates control narratives and maps evidence |
| `validate_input.py` | Script | Validates all three input JSON files |
| `build_registry.py` | Script | Creates in-memory artifact and test registry |
| `map_evidence.py` | Script | Links artifacts and tests to controls |
| `generate_narratives.py` | Script | Invokes Claude to generate control descriptions |
| `validate_citations.py` | Script | Verifies all citations point to valid artifacts |
| `assemble_output.py` | Script | Produces final markdown documents |
| `narrative_template.md` | Asset | Template for control narrative entries |
| `qa_report_template.md` | Asset | Template for gap analysis and coverage |
| `sample_artifact_index.json` | Asset | Example artifact index (10–20 artifacts) |
| `sample_test_catalog.json` | Asset | Example test catalog (5–10 tests) |
| `sample_control_library.json` | Asset | Example control library (4 generic controls) |

---

## Usage Examples

### Example 1: Generate a Data Dictionary

**Input:** `my_database_schema.json`
```json
{
  "table_name": "customers",
  "source_file": "schema.sql",
  "fields": [
    {
      "field_name": "customer_id",
      "type": "INTEGER",
      "constraints": "PRIMARY KEY, NOT NULL",
      "description": "Unique identifier for each customer"
    },
    {
      "field_name": "created_at",
      "type": "TIMESTAMP",
      "constraints": "NOT NULL",
      "description": "Account creation timestamp"
    }
  ]
}
```

**Command:**
```bash
cd skills/data-dictionary
python scripts/validate_input.py ../../my_database_schema.json
python scripts/extract_fields.py
python scripts/attach_citations.py
python scripts/generate_qa_report.py
python scripts/assemble_output.py
```

**Output:** `output/final/data_dictionary.md`
```markdown
# Data Dictionary: customers

## customer_id
- **Type:** INTEGER
- **Constraints:** PRIMARY KEY, NOT NULL
- **Description:** Unique identifier assigned to each customer at account creation.
- **Confidence:** High
- **Citation:** schema.sql, line 12
- **Last Verified:** 2026-04-24

## created_at
- **Type:** TIMESTAMP
- **Constraints:** NOT NULL
- **Description:** Timestamp recording when the customer account was first created.
- **Confidence:** High
- **Citation:** schema.sql, line 15
- **Last Verified:** 2026-04-24

...
```

### Example 2: Generate RCSA Control Narratives

**Input:** Three JSON files
- `artifact_index.json` — 15 repository artifacts
- `test_catalog.json` — 8 test files
- `control_library.json` — 4 controls

**Command:**
```bash
cd skills/rcsa
python scripts/validate_input.py ../../artifact_index.json ../../test_catalog.json ../../control_library.json
python scripts/build_registry.py
python scripts/map_evidence.py
python scripts/generate_narratives.py
python scripts/validate_citations.py
python scripts/assemble_output.py
```

**Output:** `output/final/rcsa_control_narratives.md`
```markdown
# RCSA Control Narratives

## Access Control
**Narrative:** Access to production systems is controlled through role-based access control (RBAC) 
implemented in `auth_service.py`. User roles are defined in the control library and enforced at 
the API gateway layer. Access logs are maintained in `audit_logs.py` and reviewed quarterly.

**Confidence:** High
**Evidence:**
- `auth_service.py` (lines 45–120) — RBAC implementation
- `test_access_control.py` (lines 1–50) — Access control test suite
- `audit_logs.py` (lines 200–250) — Audit logging

**Gaps:** None identified

## Change Management
**Narrative:** Code changes are managed through a Git-based workflow with mandatory code review...

...
```

---

## Quality Assurance

### QA Report Structure

Both skills produce `qa_report.md` with:

- **Coverage Statistics**
  - Total fields/controls processed
  - Fields/controls with complete metadata
  - Fields/controls with limited metadata
  - Fields/controls with no metadata

- **Confidence Distribution**
  - Count of High-confidence items
  - Count of Medium-confidence items
  - Count of Low-confidence items

- **Clarification Flags**
  - List of fields/controls flagged [NEEDS CLARIFICATION]
  - Reason for each flag

- **Citation Validation**
  - Total citations generated
  - Citations validated successfully
  - Citations with warnings or errors

- **Pipeline Summary**
  - Execution timestamp
  - Processing duration
  - Any errors or warnings encountered

### Validation Checkpoints

1. **Input Validation** — Schema/JSON structure confirmed
2. **Field/Artifact Extraction** — All items parsed correctly
3. **Citation Attachment** — Every description links to evidence
4. **Confidence Scoring** — Scores calibrated and justified
5. **Output Assembly** — Markdown formatting validated

---

## Design Principles

### Audit Readiness First
- Every claim is cited to source evidence
- Confidence scores are calibrated and justified
- Clarification flags identify gaps requiring human review
- Output is structured for compliance review

### Deterministic + AI Hybrid
- Deterministic work (parsing, validation, citing) in Python
- Reasoning work (description generation, scoring) in Claude
- Clear separation of concerns
- Reproducible results

### Graceful Degradation
- Produces output even with incomplete input
- Flags gaps rather than failing
- Supports placeholder values in degraded mode
- Maintains audit trail of what was missing

### Zero External Dependencies
- Python 3.11 standard library only
- No pip packages required
- Portable across environments
- Secure and reproducible

### Confidence Tiers
- **High** — Complete metadata, clear evidence
- **Medium** — Partial metadata, some inference required
- **Low** — Minimal metadata, significant inference required

---

## Known Risks & Limitations

### Out of Scope (Not Supported)

This skillset is **not** responsible for:
- **Production deployment** — This is a prototype for demonstration. Synchrony's team will handle production integration.
- **Integration with internal systems** — The skillset produces standalone markdown files. Synchrony will integrate with their internal data sources, workflows, and systems.
- **Enterprise security enforcement** — Synchrony's security and data governance policies must be applied during integration.
- **Compatibility with all Synchrony data** — The demo uses a public Kaggle dataset (UCI Credit Card). Real-world data may have different structures, formats, or scale.

### LLM Dependency

- **Claude availability required** — The skillset depends on Claude API access for description generation and narrative creation.
- **LLM failure mode** — If Claude is unavailable, the system gracefully degrades:
  - Produces output with placeholder values
  - Flags all LLM-generated content as [PLACEHOLDER]
  - QA report notes that LLM content is missing
  - Team can manually fill in descriptions or re-run when Claude is available
- **No offline mode** — The system cannot generate descriptions without Claude.

### Data Privacy & Security

- **Metadata only sent to LLM** — Only schema metadata, file structure, and markdown templates are sent to Claude. Raw datasets and large codebases are NOT sent.
- **No permanent storage on Claude** — Outputs are stored locally as markdown files. Claude may temporarily store inputs for security monitoring (per Anthropic's policy), but our system does not store data on Claude.
- **No training on inputs** — Anthropic does not train on API inputs by default. We have NOT enabled training on our inputs.
- **Sensitive data handling** — Users must ensure no sensitive data (passwords, API keys, PII) is included in schema metadata or artifact descriptions.

### Demo Scale Constraints

- **Single schema for Skill 1** — Demo uses UCI Credit Card dataset (25 fields). Larger schemas (500+ fields) may exceed performance budgets.
- **Limited artifact scope for Skill 2** — Demo uses 10–20 artifacts and 5–10 tests. Larger repositories may require optimization.
- **Four generic controls** — Demo covers Access Control, Change Management, Data Quality, and Incident Handling. Custom or domain-specific controls require SKILL.md customization.
- **Performance budget** — Each skill execution should complete in <5 minutes. Very large inputs may exceed this.

### Input Format Limitations

- **JSON only for demo** — Skill 1 accepts JSON schemas. YAML and DDL formats are planned for future versions and will return a clear error message indicating they are not yet supported.
- **Schema validation required** — Invalid schema format will be rejected with a clear error message. Users must correct the input and re-run.
- **Empty schema handling** — Schemas with no extractable fields will be rejected with an error explaining the issue.

### Graceful Degradation Behavior

- **Missing optional inputs** — If glossaries, profiling stats, or prior versions are not provided, the system proceeds without them and notes which defaults were applied.
- **Incomplete evidence** — If a control has no supporting artifacts or tests, the system explicitly flags a "Gap" statement rather than implying compliance without proof.
- **LLM output validation** — If Claude's output fails validation, the system retries up to 2 times (3 total attempts). If all attempts fail, it fills placeholders and continues.
- **Missing templates** — If required template files are missing, the pipeline stops with a clear error. This is a setup issue, not graceful degradation.

### Accuracy-First Trade-Offs

- **Prioritizes correctness over speed** — The system may take longer to ensure descriptions are accurate and citations are valid.
- **Never implies compliance without proof** — If evidence is insufficient, the system flags a gap rather than generating a plausible-sounding but unverified narrative.
- **Zero false negatives on gaps** — Gap flags must be 100% accurate. The system will not hide missing evidence.
- **Confidence scoring is conservative** — Items are marked "Low confidence" when metadata is ambiguous or undocumented, even if the system could generate a plausible description.

### Hallucination Prevention

- **Citation validation** — Every citation is validated against the artifact registry. Invalid citations are flagged in the QA report.
- **All citations invalid** — If all citations fail validation, the system produces a validation report showing 0% resolution and flags the output as unreliable. It does not suppress the report.
- **Ambiguous field names** — Fields with undocumented or ambiguous names are marked [NEEDS CLARIFICATION] with Low confidence scores.

### Team Skill Requirements

- **Python knowledge helpful but not required** — The system is designed for teams without strong Python expertise. Troubleshooting can be done via:
  - Prompt engineering (adjusting SKILL.md)
  - Checking JSON inputs
  - Reviewing markdown outputs
- **JSON format understanding required** — Users must be able to create and validate JSON input files.
- **Markdown review required** — Users should review markdown output for accuracy before using in compliance documentation.

---

## Roadmap & Future Extensions

### Documented for Post-Demo Extension (Not in May 7 Demo)

- **Pipeline Documentation** — Generate step-by-step documentation from codebases with source citations
- **Test Evidence Summary** — Summarize test results (pass/fail, coverage) with links to test files
- **Hooks & Sub-agents** — Trigger skills automatically and chain them together. Examples: using data dictionary output as input to RCSA skill for enhanced linkage, and scaling skills to handle enterprise-level datasets (currently tested up to ~100 fields)
- **More Skills** — Extend the control library with domain-specific controls without rebuilding the system
- **YAML/DDL Input Support** — Accept YAML and DDL formats in addition to JSON
- **CSV/DOCX Output** — Export data dictionaries and narratives to CSV and Word formats

### Integration Layer (Post-Demo)

- Integration with Synchrony's internal data sources and systems
- Compliance with Synchrony's security and data governance policies

---

## Demo Details

### Demo Date
**May 7, 2026**

### Demo Scope
- **Skill 1:** Data Dictionary generation on UCI Credit Card dataset
- **Skill 2:** RCSA Control Narratives on sample artifact/test/control files
- **Deliverables:** Live demonstration, evaluation summary, repository handoff, sign-off

### Demo Scale Constraints
- Skill 1: Single schema file (UCI Credit Card dataset)
- Skill 2: 10–20 artifacts, 5–10 tests, 4 controls
- Performance budget: <5 minutes per skill execution
- Output validation: 6 quality categories (completeness, description quality, confidence calibration, citation coverage, flag accuracy, consistency)

### Evaluation Criteria
Output will be scored against human-reviewed gold standard examples across:
1. **Completeness** — All fields/controls documented
2. **Description Quality** — Clear, concise, audit-ready
3. **Confidence Calibration** — Accurate High/Medium/Low scoring
4. **Citation Coverage** — Every claim cites evidence
5. **Flag Accuracy** — Correct identification of gaps
6. **Consistency** — Uniform formatting and terminology

---

## Support & Documentation

For complete documentation, refer to the repository structure:
- **SKILL.md files** — LLM instruction files for each skill (define reasoning tasks and output formats)
- **Python scripts** — Fully commented pipeline code showing exactly how data flows through the system
- **Assets/** — Templates, sample inputs, and gold standard examples
- **docs/** — Detailed specifications and project planning documents
- **tests/** — Test data and validation examples

The entire repository is designed to be self-documenting and auditable.

---

## License & Contact

**Project Lead:** Sheila Green
**Skill Owners:** Molly Lowell and Whitney Robinson  
**Demo Deadline:** May 7, 2026

---
