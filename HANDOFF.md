# Automated Audit Documentation Generator

**Prepared by**: Molly, Sheila, Whitney

**Project type**: Compliance Automation Tool

**Domain**: Audit & Compliance Documentation

**Engagement**: Synchrony Financial — Documentation & Compliance Teams

---

## Executive Summary

The Automated Audit Documentation Generator converts structured technical artifacts—JSON schemas, code files, test catalogs, and control libraries—into audit-ready compliance documentation. The system reduces manual data dictionary creation from 60–120 minutes to ~5–10 minutes per schema while ensuring every output includes source citations and explicit gap flags. Two core skills power the system: a Data Dictionary Generator that produces field-level metadata with confidence scores, and an RCSA Control Narrative Generator that maps evidence to compliance controls with inline citations.

---

## The Challenge

Synchrony's documentation and compliance teams face a time-intensive manual process for generating audit-ready documentation:

- **Data Dictionary Creation**: Manually documenting database schema fields takes 60–120 minutes per schema, with inconsistent citation practices and no systematic gap identification
- **Control Narrative Development**: Mapping technical evidence (code, tests, artifacts) to compliance controls requires manual cross-referencing, leading to incomplete coverage and unverified citations
- **Audit Readiness**: Current outputs lack structured metadata, confidence scoring, and explicit flags for missing evidence, making audit review inefficient
- **Scalability**: As systems grow, manual documentation processes become bottlenecks for compliance reporting

---

## Our Solution

### Architecture

The system operates as a two-phase pipeline combining deterministic processing with LLM-powered reasoning:

**Phase 1: Deterministic Processing** — Python scripts validate, extract, and prepare data from structured inputs (JSON schemas, artifact indexes, test catalogs, control libraries)

**Phase 2: LLM Reasoning** — Claude generates descriptions, narratives, and citations with explicit confidence scoring and gap identification

The system includes two independent skills that can be deployed separately:

1. **Data Dictionary Skill** — Transforms database schemas into field-level metadata with descriptions, citations, and confidence scores
2. **RCSA Skill** — Maps technical artifacts and tests to compliance controls, generating evidence-backed narratives

**How it works:**

```
Input Files (JSON)
    ↓
Validation Scripts (validate_input.py)
    ↓
Extraction & Preparation (extract_fields.py, build_registry.py, map_evidence.py)
    ↓
LLM Orchestration (Claude via SKILL.md system prompt)
    ↓
Citation Validation (validate_citations.py)
    ↓
Output Generation (write_output.py)
    ↓
Markdown Reports with Metadata & Citations
```

### Key Design Decisions

- **JSON-First Input Format**: Structured JSON input ensures consistent validation and enables programmatic processing without manual parsing
- **Manual LLM Integration**: Users load SKILL.md as a system prompt in Claude Desktop, maintaining transparency and control over LLM reasoning
- **Citation Validation Layer**: Post-processing scripts verify every citation resolves to a real artifact, preventing hallucinated references
- **Confidence Scoring**: All outputs include HIGH/MEDIUM/LOW confidence ratings, enabling auditors to prioritize review efforts
- **Graceful Degradation**: If Claude API is unavailable, the system outputs raw evidence without narratives, maintaining partial functionality
- **Modular Skills Architecture**: Each skill (Data Dictionary, RCSA) operates independently with its own validation, processing, and output pipelines

---

## Technical Approach

### Prerequisites & Installation

**Requirements:**
- Python 3.10+
- Claude API access (for LLM reasoning tasks)

**Installation:**

```bash
# Clone the repository
git clone https://github.com/whitneyrobinson-creator/Synchronyproject.git
cd Synchronyproject

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Claude API key
export CLAUDE_API_KEY="your-api-key-here"
```

### Data Dictionary Skill — Complete Pipeline

**Step 1: Input Preparation**
- User identifies a database schema and exports it as JSON
- File format includes field name, type, constraints, and description
- Place file in: `skills/data_dictionary/assets/sample-data/`

**Step 2: Validation & Extraction**

```bash
cd skills/data_dictionary
python scripts/validate_input.py assets/sample-data/your-schema.json
python scripts/extract_fields.py
```

System checks JSON validity, required fields, and recognized field types. Produces `intermediate/extracted_fields.json`.

**Step 3: LLM Reasoning (Manual)**
1. Open Claude Desktop
2. Load `skills/data_dictionary/SKILL.md` as system prompt
3. Paste contents of `intermediate/extracted_fields.json` as user input
4. Claude generates field descriptions (≤25 words) with citations and confidence scores
5. Save output to `intermediate/llm_output.json`

**Step 4: Post-Processing & Output**

```bash
python scripts/merge_descriptions.py
python scripts/add_timestamps.py
python scripts/assemble_output.py
python scripts/write_output.py
```

Produces:
- `output/data_dictionary.md` — Final data dictionary with all metadata
- `output/qa_report.md` — Coverage stats and confidence distribution

### RCSA Control Narrative Skill — Complete Pipeline

**Step 1: Input Preparation**
- User gathers three JSON files: artifact_index.json, test_catalog.json, control_library.json
- Place all files in: `skills/rcsa/assets/sample-data/`

**Step 2: Validation, Registry Building & Evidence Mapping**

```bash
cd skills/rcsa
python scripts/validate_input.py assets/sample-data/artifact_index.json assets/sample-data/test_catalog.json assets/sample-data/control_library.json
python scripts/build_registry.py
python scripts/map_evidence.py
```

Produces `intermediate/mapped_evidence.json` with evidence linked to each control.

**Step 3: LLM Reasoning (Manual)**
1. Open Claude Desktop
2. Load `skills/rcsa/SKILL.md` as system prompt
3. Paste contents of `intermediate/mapped_evidence.json` as user input
4. Claude generates control narratives (3–5 sentences) with inline citations and gap flags
5. Save output to `intermediate/llm_output.json`

**Step 4: Citation Validation & Output**

```bash
python scripts/validate_citations.py
python scripts/write_output.py
```

Produces:
- `output/rcsa_control_narratives.md` — Control narratives with summary table
- `output/validation_report.md` — Citation resolution stats and coverage

---

## Deliverables

| Deliverable | Format | Location | Purpose |
|---|---|---|---|
| data_dictionary.md | Markdown table | `skills/data_dictionary/output/` | Field-level metadata with citations and confidence scores |
| qa_report.md | Markdown report | `skills/data_dictionary/output/` | Coverage stats, confidence distribution, flagged items |
| rcsa_control_narratives.md | Markdown report | `skills/rcsa/output/` | Control narratives with evidence mapping and confidence levels |
| validation_report.md | Markdown report | `skills/rcsa/output/` | Citation resolution stats and coverage percentage |
| SKILL.md files | Markdown prompts | `skills/[skill]/SKILL.md` | LLM instruction files for Claude Desktop |
| Python scripts | Python modules | `skills/[skill]/scripts/` | Validation, extraction, processing, and output generation |

---

## Results

### Performance Metrics

| Metric | Baseline | Target | Status |
|---|---|---|---|
| Time to generate data dictionary | 60–120 minutes (manual) | 5–10 minutes | ✓ Achieved |
| Field extraction accuracy | — | ≥95% of fields | ✓ Validated |
| Citation coverage | — | ≥90% of descriptions | ✓ Validated |
| Gap flag accuracy | — | Zero false negatives | ✓ Validated |

### Known Limitations & Workarounds

| Limitation | Impact | Workaround |
|---|---|---|
| JSON input only | Users cannot provide YAML or DDL schemas | Validate and convert schemas to JSON format before processing |
| Markdown output only | Limited formatting options | Export markdown to Word/PDF as needed |
| LLM dependency | System requires Claude API access | Graceful degradation mode available; outputs raw evidence without narratives |
| Large schemas (>100 fields) | Performance degradation | Process in batches of 50 fields |
| Claude API timeout | System enters degradation mode | Retry with smaller input or check API status |

### Edge Cases

| Edge Case | Current Behavior | Recommended Handling |
|---|---|---|
| Malformed JSON input | Script fails with validation error | Validate JSON syntax before running |
| Missing required fields | Script skips field and logs warning | Ensure all required fields present in input |
| All citations invalid | Validation report shows 0% resolution | Review artifact_index.json for accuracy |

---

## Engagement Details

### Project Team

| Role | Name | Email | Responsibility |
|---|---|---|---|
| Project Manager | Sheila Green | sheila.green@student.fairfield.edu | Overall project ownership and coordination post-handoff |
| Skill Owner | Whitney Robinson | whitney.robinson@student.fairfield.edu | Technical questions and maintenance |
| Skill Owner | Molly Lowell | molly.lowell@student.fairfield.edu | Business decisions about system usage and extensions |

### Future Extensions (Documented but Not Included in Current Release)

- **Pipeline Documentation** (P2) — Generate step-by-step documentation from codebase with citations
- **Test Evidence Summary** (P2) — Generate test execution summary with coverage stats and links
- **Repository Scanning** — Automatic artifact index generation from full repository
- **CLI Packaging** — Command-line interface for production deployment
- **YAML & DDL Input Support** — Expand input format compatibility
- **CSV & DOCX Output Formats** — Additional export options

### Maintenance & Support

**How to Update:**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

**How to Extend:**
- Add new input format: Create new parser in `scripts/validate_input.py`
- Add new output format: Create new template in `assets/templates/`
- Modify processing logic: Edit corresponding script in `scripts/`

**Common Troubleshooting:**
- "File not found" error → Verify file exists and path is correct
- JSON validation error → Validate JSON syntax using online validator
- LLM output missing citations → Verify SKILL.md is loaded correctly in Claude Desktop
- All citations invalid → Verify artifact_index.json contains exact file paths

---

## Applicability

This solution is designed for organizations that need to:

- **Generate audit-ready documentation** from technical artifacts with verifiable citations
- **Reduce manual documentation effort** while maintaining compliance rigor
- **Scale compliance processes** as systems and control requirements grow
- **Maintain citation integrity** through automated validation and gap identification

The system is particularly valuable for:
- Financial services firms (like Synchrony) with strict audit and compliance requirements
- Organizations managing multiple systems with complex control mappings
- Teams seeking to reduce documentation bottlenecks in compliance workflows
- Auditors requiring structured, cited evidence for control assessments

**Ideal Use Cases:**
- Generating data dictionaries from database schemas
- Mapping technical evidence to compliance controls (SOX, HIPAA, PCI-DSS, etc.)
- Creating audit-ready control narratives with explicit gap identification
- Documenting system changes and their compliance implications

---

*For a detailed discussion of this approach or to explore how it applies to your specific use case, contact:*

- *Sheila Green (PM) — sheila.green@student.fairfield.edu*
- *Whitney Robinson (Skill Owner) — whitney.robinson@student.fairfield.edu*
- *Molly Lowell (Skill Owner) — molly.lowell@student.fairfield.edu*
