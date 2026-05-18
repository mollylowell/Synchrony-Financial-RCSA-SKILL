---
name: rcsa
description: Generates citation-backed RCSA (Risk and Control Self-Assessment) control narratives from pre-processed mapped evidence. Detects compliance gaps, assigns confidence tiers, and produces audit-ready documentation. Use when asked to generate RCSA narratives, run RCSA control analysis, or create control narratives.
---

# RCSA Control Narrative Generation

This skill orchestrates a 6-step workflow that transforms repository artifacts into audit-ready RCSA control narratives. It calls deterministic scripts for data processing and uses LLM reasoning for narrative generation and output assembly.

**What this skill does:**

- Validates inputs, builds an artifact registry, and maps evidence to controls (via scripts)
- Generates 3–5 sentence auditor-friendly narratives per control with inline citations
- Assigns confidence tiers (HIGH / MEDIUM / LOW) based on evidence strength
- Flags explicit GAP statements when evidence is missing or insufficient
- Produces a summary table for at-a-glance compliance posture
- Outputs two Markdown documents: `rcsa_control_narratives.md` and `validation_report.md`

**What this skill does NOT do:**

- Parse raw repository files (scripts handle this)
- Validate input format or map evidence (scripts handle this)
- Validate citations post-generation (scripts handle this)
- Suggest remediation for compliance gaps
- Use external knowledge or assumptions about the repository

## Assets

This skill depends on static assets in the skill root:

| Asset | Path | Purpose |
|---|---|---|
| Control Library | `sample_control_library.json` | Defines the 4 controls and their expected evidence types |
| Artifact Index | `sample_artifact_index.json` | Provides artifact file paths and metadata used for evidence mapping |
| Test Catalog | `sample_test_catalog.json` | Provides test evidence and control relevance mappings |
| Narratives Template | `rcsa_control_narratives_template.md` | Output structure for the primary deliverable |
| Validation Report Template | `validation_report_template.md` | Output structure for the QA deliverable |
| Citation Format Spec | `citation_format.md` | Canonical syntax rules for inline citations |

## Workflow Overview

Execute these 6 steps in order. Do not skip steps or reorder them.

| Step | Name | Type | Input | Output |
|---|---|---|---|---|
| 1 | Validate Inputs | `[SCRIPT]` | Control library + repository file listing | Validation result (pass/fail) |
| 2 | Build Artifact Registry | `[SCRIPT]` | Repository files + control library | Artifact registry with snippets |
| 3 | Map Evidence to Controls | `[SCRIPT]` | Artifact registry + control library | Mapped evidence per control |
| 4 | Generate Narratives | `[LLM]` | Control library + artifact registry + mapped evidence | Draft narratives + confidence tiers + GAP flags |
| 5 | Validate Citations | `[SCRIPT]` | Draft narratives + artifact registry | Citation validation results |
| 6 | Assemble Final Output | `[LLM]` | Draft narratives + validation results | `rcsa_control_narratives.md` + `validation_report.md` |

Steps 1–3 and 5 are deterministic script calls. Steps 4 and 6 are LLM reasoning.

---

## Error Handling Rules

These rules apply to every step in the workflow.

**Script errors — stop immediately:**
If any `[SCRIPT]` step returns an error or `status: "fail"`, stop the workflow immediately. Report the exact error message to the user. Do not proceed to the next step. Do not attempt to work around the error.

**No LLM fallback:**
Never fall back to LLM reasoning when a script fails. The LLM must not attempt to replicate what the script would have done. Scripts exist because their work is deterministic — the LLM cannot reliably substitute for them.

**Unparseable script output:**
If a script returns output that cannot be parsed (malformed YAML, missing expected fields), report that the script output was unparseable. Do not guess at the intended output.

**LLM uncertainty:**
If a `[LLM]` step encounters data it cannot interpret, flag the specific issue and ask the user for guidance. Do not guess.

**Error message format:**
All error messages must include: (1) which step failed, (2) what the error was, and (3) what the user should do next.

---

## Step 1: Validate Inputs `[SCRIPT]`

Call `validate_input` with the control library and the raw repository file listing.

**Expected input to script:**
- `control_library` — the control definitions file
- Raw repository file listing

**Expected output from script:**

```yaml
validation:
  status: "pass"   # or "fail"
  errors: []        # empty if pass; list of error strings if fail
```

**Branching logic:**
- If `status` is `"pass"` — proceed to Step 2.
- If `status` is `"fail"` — stop the workflow. Report every error from the `errors` list to the user. Do not attempt to reason over invalid data.

**What the script validates:** Required fields are present in the control library, no duplicate control IDs, each control ID matches the format `^[A-Z]{2,4}$`, and `evidence_types` is non-empty for each control.

---

## Step 2: Build Artifact Registry `[SCRIPT]`

Call `build_registry` with the raw repository files and the control library.

**Expected input to script:**
- Raw repository files
- Control library (for `evidence_types` reference)

**Expected output from script:**

```yaml
artifacts:
  - id: "ART-001"
    file_path: "src/auth/login.py"
    artifact_type: "auth_config"
    snippet: |
      <relevant code/config excerpt>
    snippet_line_range: "12-19"
    file_size_bytes: 2048         # optional
    last_modified: "2026-03-15"   # optional
```

**Field definitions:**

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique identifier, format: `ART-[NUMBER]` |
| `file_path` | Yes | Relative path from repository root |
| `artifact_type` | Yes | Must match an `evidence_types` value from the control library |
| `snippet` | Yes | Relevant excerpt extracted by the script |
| `snippet_line_range` | Yes | Line range of the snippet, format: `"start-end"` |
| `file_size_bytes` | No | Full file size (informational) |
| `last_modified` | No | Last modification date (informational) |

**Edge case — empty registry:**
If the script returns `artifacts: []` (no artifacts found), note that all controls will be flagged as GAP in Step 4. Still proceed to Step 3.

---

## Step 3: Map Evidence to Controls `[SCRIPT]`

Call `map_evidence` with the artifact registry and the control library.

**Expected input to script:**
- Artifact registry (from Step 2)
- Control library

**Expected output from script:**

```yaml
mappings:
  - control_id: "AC"
    control_name: "Access Control"
    mapped_artifacts:
      - artifact_id: "ART-001"
        artifact_type: "auth_config"
        relevance: "direct"
      - artifact_id: "ART-002"
        artifact_type: "rbac_policy"
        relevance: "direct"
  - control_id: "DQ"
    control_name: "Data Quality"
    mapped_artifacts: []
```

**Key rules:**
- Every control in the control library appears in the mappings, even if `mapped_artifacts` is empty.
- `relevance` values: `"direct"` means the artifact type exactly matches a control's evidence type. `"indirect"` means a partial or inferred match.
- A single artifact may appear in multiple controls' `mapped_artifacts`.

After receiving the mapped evidence, proceed to Step 4.

---

## Confidence Tier Rubric

Consult this rubric when assigning confidence tiers in Step 4.

| Tier | Criteria | What It Signals |
|---|---|---|
| **HIGH** | >= 2 artifacts with `"direct"` relevance supporting the control objective | Strong evidence — multiple artifacts corroborate the control |
| **MEDIUM** | 1 artifact with `"direct"` relevance, OR >= 2 artifacts with `"indirect"` relevance | Moderate evidence — something exists but coverage is incomplete |
| **LOW** | 1 artifact with `"indirect"` relevance only | Weak evidence — barely supports the control; needs human review |
| **GAP** | `mapped_artifacts` is empty — zero artifacts mapped | No evidence found — this is a separate binary flag, not a confidence tier |

**Edge cases:**

| Situation | Outcome |
|---|---|
| 3 direct artifacts | HIGH |
| 2 artifacts: 1 direct + 1 indirect | HIGH (>= 2 total with at least 1 direct) |
| 2 indirect artifacts | MEDIUM |
| 1 direct artifact | MEDIUM |
| 1 indirect artifact | LOW |
| 0 artifacts | GAP flag |
| Metadata says one thing but snippet shows another | Drop one tier, note the mismatch |
| Same artifact in 3 controls | Counts for all 3 |
| All 4 controls have 0 artifacts | 4 GAP flags |

**Rules:**
- The snippet is ground truth. If the artifact's metadata (type, description) contradicts what the snippet actually shows, trust the snippet and lower confidence by one tier. Note the mismatch in the validation report.
- Never inflate confidence. If the evidence is weak, say so.
- Every control gets exactly one outcome: a confidence tier (HIGH / MEDIUM / LOW) or a GAP flag. Never both.

---

## Citation Format Rules

The canonical citation format is defined in `citation_format.md`. The following rules are restated here for quick reference during narrative generation.

**Syntax:**

```
[file_path — description]
```

- `file_path` is the relative path to the evidence artifact, exactly as it appears in the artifact registry. Do not modify the path.
- ` — ` (space, em dash, space) separates the path from the description.
- `description` is a brief human-readable label explaining what the artifact provides as evidence.

**Rules:**
1. Only cite artifacts present in the artifact registry. Never invent citations.
2. Each factual claim in the narrative should trace to a specific artifact.
3. Use the exact `file_path` from the registry — no modifications, no abbreviations.
4. Multi-control artifacts: if a single artifact maps to multiple controls, cite it in every control where it appears. Note the overlap in each narrative.
5. Multi-file evidence: use separate citations per file. No grouping syntax.

**Example:**

```markdown
Authentication is enforced via OAuth 2.0 configuration
[auth/oauth_config.yaml — OAuth2 provider configuration] with role-based
access defined in [auth/rbac_roles.yaml — RBAC role definitions].
```

---

## Anti-Hallucination and Evidence Exclusion Rules

These rules are hard constraints. They override any other instruction.

**Rule 1 — Never imply compliance without proof.**
If evidence is insufficient for a control, flag it as GAP or assign a low confidence tier. Never fill the gap with reasoning, speculation, or external knowledge.

**Rule 2 — Exclude ambiguous evidence.**
If an artifact's snippet is ambiguous — it does not clearly support the control objective — exclude it from the narrative entirely. Flag it for human review in the validation report. Do not include ambiguous evidence with caveats or hedging language. A hedged citation is still a citation, and it might be wrong.

**Rule 3 — No external knowledge.**
Use only the artifacts and snippets provided by the pipeline. No assumptions about what the repository "probably" contains. No general knowledge about compliance frameworks. No reference to industry standards or best practices unless they appear in the provided evidence.

**Rule 4 — No remediation suggestions.**
When flagging a GAP, state what is missing. Never suggest how to fix it. Remediation requires domain knowledge about the organization's specific compliance environment, which the LLM does not have.

**Rule 5 — Zero false negatives target.**
It is better to flag a control as GAP incorrectly than to claim compliance incorrectly. When in doubt, flag.

---

## GAP Statement Template

Use this structure when a control is flagged as GAP.

**When to use:** `mapped_artifacts` is empty for a control, OR all mapped artifacts were excluded per the evidence exclusion rules above.

**Structure:**

```markdown
## {control_name} ({control_id})

**Confidence**: GAP
**Artifacts Cited**: 0

[GAP] No artifacts were mapped to the {control_name} control. No evidence of
{list expected evidence types from the control library} was found in the
repository. This control requires human review to determine whether evidence
exists outside the scanned artifacts or whether remediation is needed.
```

**Rules:**
- GAP controls do not get a narrative section. Only the GAP statement.
- Do not suggest remediation steps.
- Do not speculate about evidence that might exist elsewhere.
- List the specific expected evidence types from the control library so the reader knows what was looked for.

**Edge case — all artifacts excluded due to ambiguity:**
If a control had artifacts mapped but all were excluded as ambiguous, use this modified statement:

```markdown
[GAP] Artifacts were identified for the {control_name} control but were
excluded due to ambiguity. The following evidence types were expected:
{list expected evidence types}. Flagged for human review.
```

---

## Step 4: Generate Narratives `[LLM]`

This is the core reasoning step. Process each control from the mapped evidence.

**For each control in the mapped evidence:**

1. Read the control's `objective` from the control library.
2. Read the `mapped_artifacts` list.
3. For each mapped artifact, look up its `snippet` in the artifact registry.

**If `mapped_artifacts` is empty:**
- Assign GAP flag.
- Write a GAP statement using the GAP Statement Template above.
- Skip narrative generation for this control.
- Do not write a compliance narrative.

**If `mapped_artifacts` is not empty:**
- Read each artifact's snippet carefully. The snippet is ground truth.
- If any artifact's snippet contradicts its metadata (type or description), trust the snippet. Lower the confidence tier by one level and note the mismatch.
- If any artifact's snippet is ambiguous (does not clearly support the control objective), exclude it from the narrative. Flag it for human review. Do not include it with caveats.
- If after exclusions the `mapped_artifacts` list is effectively empty, assign GAP flag and write a GAP statement (use the ambiguity edge case template).
- Otherwise, write a 3–5 sentence narrative:
  - Synthesize the evidence from the remaining artifacts.
  - Include inline citations for each factual claim using the citation format `[file_path — description]`.
  - Explain how each artifact supports the control objective.
  - If an artifact maps to multiple controls, note the overlap.
- Assign a confidence tier per the Confidence Tier Rubric.

**Narrative tone:** Professional, auditor-friendly, factual. No hedging language. No speculation. No filler.

**After processing all controls, proceed to Step 5.**

---

## Summary Table Instructions

After generating narratives for all controls (Step 4), build the summary table. This table appears in the final output immediately after the YAML front matter, before any per-control sections.

**Columns:**

| Column | Description |
|---|---|
| Control ID | Short identifier (e.g., `AC`) |
| Control Name | Human-readable name (e.g., "Access Control") |
| Confidence | `HIGH`, `MEDIUM`, `LOW`, or `GAP` |
| Artifacts | Count of artifacts cited in the narrative |
| Status | Visual indicator (see below) |

**Status indicators:**
- `HIGH` or `MEDIUM` confidence: `✅ Assessed`
- `LOW` confidence: `⚠️ Weak Evidence`
- `GAP`: `🔴 No Evidence`

**Rules:**
- One row per control, in the same order they appear in the control library input.
- Every control in the input must appear in the table. No controls may be omitted, even if flagged as GAP.
- The confidence tier and artifact count in the table must exactly match the values in the corresponding per-control section. No discrepancies.
- If all four controls are GAP, the table still appears with four rows — all showing `GAP` / `0` / `🔴 No Evidence`.

---

## Step 5: Validate Citations `[SCRIPT]`

Call `validate_citations` with the draft narratives from Step 4 and the artifact registry.

**Expected input to script:**
- Draft narratives (complete text from Step 4)
- Artifact registry (from Step 2)

**Expected output from script:**

```yaml
citation_validation:
  total_citations: 4
  resolved: 4
  unresolved: 0
  resolution_rate: 1.0
  citations:
    - citation_text: "src/auth/login.py — credential validation..."
      file_path: "src/auth/login.py"
      artifact_id: "ART-001"
      resolved: true
      match_type: "exact"
  unresolved_list: []
```

**Branching logic:**
- If `unresolved` is `0` — proceed to Step 6.
- If `unresolved` > `0` — fix every broken citation before proceeding. For each unresolved citation:
  - Remove the citation if the claim can stand without it.
  - Replace with a valid artifact from the registry if an appropriate one exists.
  - If neither option works, flag the issue explicitly in the narrative text.
  - Never leave an unresolved citation in the final output.

---

## Output Structure: `rcsa_control_narratives.md`

This is the primary deliverable — the auditor-facing document. Build it using the structure defined below, referencing the template at `rcsa_control_narratives_template.md`.

**YAML Front Matter:**

```yaml
---
title: "RCSA Control Narrative Assessment"
generated: "<ISO 8601 timestamp>"
controls_assessed: <total number of controls>
controls_passing: <controls with HIGH or MEDIUM confidence>
controls_low_confidence: <controls with LOW confidence>
controls_gap: <controls with zero evidence>
framework: "Custom Demo Controls"
---
```

**Document sections in order:**

1. **Summary Table** — the table built per the Summary Table Instructions above.
2. **Per-control sections** — one section per control, in control library order. Each section contains:
   - Heading: `## {control_name} ({control_id})`
   - `**Confidence**`: the tier assigned
   - `**Artifacts Cited**`: count of artifacts referenced
   - `**Evidence Types Covered**`: which of the control's expected evidence types were matched
   - Narrative paragraph (3–5 sentences with inline citations) OR GAP statement
   - Horizontal rule (`---`) after each section

---

## Output Structure: `validation_report.md`

This is the secondary deliverable — the QA/technical report. Build it using the structure defined below, referencing the template at `validation_report_template.md`.

**Header fields:**

```markdown
# Validation Report

**Generated**: <ISO 8601 timestamp>
**SKILL.md Version**: 1.0
**Controls Assessed**: <count>
```

**Sections in order:**

1. **Citation Resolution** — table showing every citation from the narratives:

| Column | Description |
|---|---|
| Citation | The full citation text |
| Artifact ID | The matching artifact ID from the registry |
| File Path | The file path extracted from the citation |
| Resolved | ✅ Yes or ❌ No |
| Match Type | `Exact` or other match type |

   Followed by summary statistics: Total Citations, Resolved, Unresolved, Resolution Rate.

2. **Confidence Scoring Audit** — table showing how each control's confidence tier was calculated:

| Column | Description |
|---|---|
| Control ID | The control identifier |
| Confidence | The assigned tier |
| Direct Artifacts | Count of artifacts with `"direct"` relevance |
| Indirect Artifacts | Count of artifacts with `"indirect"` relevance |
| Rubric Match | Explanation of why this tier was assigned |

3. **Excluded Evidence** (optional — include only when artifacts were excluded):

| Column | Description |
|---|---|
| Artifact ID | The excluded artifact |
| Control ID | Which control it was excluded from |
| Reason Excluded | Why it was excluded (e.g., ambiguous snippet) |

4. **Warnings** (optional — include only when warnings exist):
   Bullet list of concerns such as low evidence type coverage for a control, metadata/snippet mismatches, or controls with only indirect evidence.

---

## Step 6: Assemble Final Output `[LLM]`

Build both output documents from the results of Steps 4 and 5.

**Building `rcsa_control_narratives.md`:**

1. Write the YAML front matter. Count controls in each category (passing, low confidence, gap) from the Step 4 results.
2. Insert the summary table.
3. Insert per-control sections in control library order.
4. If Step 5 found unresolved citations, incorporate the fixes made after Step 5. Every citation in the final document must be resolved.
5. Verify the document is a complete, standalone Markdown file. A reader should understand it without seeing the intermediate data.

**Building `validation_report.md`:**

1. Write the header with generation timestamp and metadata.
2. Populate the Citation Resolution table from Step 5 results.
3. Populate the Confidence Scoring Audit table from Step 4 results (artifact counts, relevance, tier assignment rationale).
4. Include the Excluded Evidence section only if artifacts were excluded during Step 4.
5. Include the Warnings section only if there are concerns to flag (e.g., controls with low evidence type coverage, metadata/snippet mismatches).
6. Verify the document is complete and standalone.

**Final checks before delivering output:**
- Both documents are valid Markdown with correct heading hierarchy.
- All citations in the narratives document are resolved (verified in Step 5).
- The summary table values match the per-control sections exactly.
- YAML front matter counts are accurate.
- No unresolved citations, no hallucinated artifacts, no compliance claims without proof.

---

## Requirement Traceability

This section maps each functional requirement (FR) and success criterion (SC) from the F5 spec to the SKILL.md sections that implement it.

### Functional Requirements

| FR | Requirement | Implemented In |
|---|---|---|
| FR-001 | Inline citations in narratives (3–5 sentences per control) | Citation Format Rules, Step 4: Generate Narratives |
| FR-002 | Explicit GAP flagging when evidence is missing | GAP Statement Template, Step 4: Generate Narratives |
| FR-003 | Never imply compliance without proof | Anti-Hallucination Rules (Rule 1), Confidence Tier Rubric |
| FR-004 | Summary table showing evidence vs. gaps | Summary Table Instructions |
| FR-005 | All four controls processed in every run | Step 3 (every control appears in mappings), Summary Table Instructions (completeness rule) |
| FR-006 | Only provided evidence — no external knowledge | Anti-Hallucination Rules (Rule 3), Step 4: Generate Narratives |
| FR-007 | Citations reference real artifacts from registry | Citation Format Rules (Rule 1), Step 2: Build Registry, Step 5: Validate Citations |
| FR-008 | Prefer GAP flags over uncertain claims | Anti-Hallucination Rules (Rule 5), Confidence Tier Rubric, GAP Statement Template |
| FR-009 | Follow output templates from F4 assets | Output Structure: rcsa_control_narratives.md, Output Structure: validation_report.md |
| FR-010 | Orchestration sequence (validate → build → map → generate → validate → assemble) | Workflow Overview, Steps 1–6 |

### Success Criteria

| SC | Criteria | Enforced By |
|---|---|---|
| SC-001 | >= 85% gap detection accuracy | Anti-Hallucination Rules (Rule 5: zero false negatives target), GAP Statement Template |
| SC-002 | <= 5% hallucinated artifacts | Citation Format Rules (Rule 1: only cite registry artifacts), Step 5: Validate Citations |
| SC-003 | All 4 controls addressed every run | Step 3 (all controls in mappings), Summary Table Instructions (completeness rule) |
| SC-004 | >= 90% structural consistency across runs | Output Structure sections (fixed YAML fields, table columns, section headings) |
| SC-005 | All required sections present in output | Step 6: Assemble Final Output (final checks) |
