"""F6 Script 6: Write Output Files.

Generates the two final Markdown deliverables:
  - rcsa_control_narratives.md
  - validation_report.md

Uses the F4/F5 template files as the base structure and fills dynamic content.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


SCRIPT_ID = "OUTPUT"
SKILL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NARRATIVES_TEMPLATE_CANDIDATES = [
    os.path.join(SKILL_ROOT, "rcsa_control_narratives_template.md"),
    os.path.join(SKILL_ROOT, "assets", "rcsa_control_narratives_template.md"),
]
VALIDATION_TEMPLATE_CANDIDATES = [
    os.path.join(SKILL_ROOT, "validation_report_template.md"),
    os.path.join(SKILL_ROOT, "assets", "validation_report_template.md"),
]

NARRATIVE_SUMMARY_LOOP_BLOCK = (
    "{{#each controls}}\n"
    "| {{control_name}} ({{control_id}}) | {{confidence_tier}} | {{evidence_found}} | {{gaps_identified}} |\n"
    "{{/each}}"
)
NARRATIVE_CONTROL_LOOP_BLOCK = (
    "{{#each controls}}\n"
    "## {{control_name}} ({{control_id}})\n\n"
    "**Objective**: {{control_objective}}\n\n"
    "**Confidence**: {{confidence_tier}}\n\n"
    "### Narrative\n\n"
    "{{narrative_text}}\n\n"
    "{{#if has_gaps}}\n"
    "### Gaps\n\n"
    "{{#each gaps}}\n"
    "> ⚠️ **GAP**: {{evidence_type_label}} (`{{evidence_type_id}}`) — no matching evidence found\n"
    "{{/each}}\n"
    "{{/if}}\n\n"
    "### Evidence\n\n"
    "{{#each matched_evidence}}\n"
    "- {{description}} [{{file_path}} — {{evidence_label}}]\n"
    "{{/each}}\n\n"
    "---\n\n"
    "{{/each}}"
)

VALIDATION_CITATION_LOOP_BLOCK = (
    "{{#each citations}}\n"
    "| [{{file_path}} — {{description}}] | `{{file_path}}` | {{lines}} | {{status}} |\n"
    "{{/each}}"
)
VALIDATION_CONTROL_LOOP_BLOCK = (
    "{{#each controls}}\n"
    "| {{control_name}} ({{control_id}}) | {{expected_count}} | {{matched_count}} | {{unmatched_count}} | {{coverage_pct}} |\n"
    "{{/each}}"
)
VALIDATION_FLAGS_BLOCK = (
    "{{#if has_flags}}\n"
    "{{#each flags}}\n"
    "- **{{flag_type}}**: {{flag_description}}\n"
    "{{/each}}\n"
    "{{else}}\n"
    "No items flagged. All citations resolved and all expected evidence types matched.\n"
    "{{/if}}"
)


def log(level, message):
    print(f"[F6-{SCRIPT_ID}] {level}: {message}", file=sys.stderr)


def read_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        log("ERROR", f"FILE_NOT_FOUND: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log("ERROR", f"PARSE_ERROR: {file_path} is not valid JSON — {e}")
        sys.exit(1)


def _load_template(candidate_paths):
    for path in candidate_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read(), path
    raise FileNotFoundError(f"No template found in candidates: {candidate_paths}")


def _replace_placeholders(template_text, values):
    rendered = template_text
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    return rendered


def _overall_confidence(narratives):
    confidences = {n.get("confidence", "UNAVAILABLE") for n in narratives.values()}
    if "GAP" in confidences:
        return "MIXED"
    if confidences == {"HIGH"}:
        return "HIGH"
    if "LOW" in confidences:
        return "LOW"
    if "MEDIUM" in confidences or "HIGH" in confidences:
        return "MEDIUM"
    return "UNAVAILABLE"


def _build_narratives_md(llm_response, mapped_evidence):
    """Build rcsa_control_narratives.md from the narratives template."""
    fm = llm_response.get("yaml_front_matter", {})
    narratives = llm_response.get("narratives", {})
    mappings = mapped_evidence.get("mappings", [])
    is_degraded = llm_response.get("status") == "degraded"
    timestamp = fm.get("generated", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    template, template_path = _load_template(NARRATIVES_TEMPLATE_CANDIDATES)
    log("INFO", f"Using narratives template: {template_path}")

    rendered = _replace_placeholders(
        template,
        {
            "generated": timestamp,
            "skill_version": "1.0",
            "total_controls": len(mappings),
            "overall_confidence": _overall_confidence(narratives),
        },
    )

    summary_rows = []
    control_sections = []

    for mapping in mappings:
        ctrl_id = mapping["control_id"]
        ctrl_name = mapping["control_name"]
        ctrl_obj = mapping.get("control_objective", "")
        narr = narratives.get(ctrl_id, {})
        confidence = narr.get("confidence", "UNAVAILABLE")
        gap = narr.get("gap_flag", mapping.get("gap_flag", False))

        # Demo-day blocker fix: summary must use cited evidence, not mapped counts.
        art_count = len(narr.get("artifacts_cited", []))
        tst_count = len(narr.get("tests_cited", []))
        evidence_found = f"{art_count} artifacts, {tst_count} tests"
        gaps_identified = "Yes" if (gap or confidence == "GAP") else "No"
        summary_rows.append(
            f"| {ctrl_name} ({ctrl_id}) | {confidence} | {evidence_found} | {gaps_identified} |"
        )

        section_lines = [
            f"## {ctrl_name} ({ctrl_id})",
            "",
            f"**Objective**: {ctrl_obj}",
            "",
            f"**Confidence**: {confidence}",
            "",
            "### Narrative",
            "",
        ]
        narrative_text = narr.get("narrative_text", "")
        if narrative_text and not is_degraded:
            section_lines.append(narrative_text)
        elif is_degraded:
            section_lines.append("*LLM unavailable — raw evidence listing provided.*")
        else:
            section_lines.append("[GAP] No narrative text available.")
        section_lines.append("")

        coverage = mapping.get("evidence_type_coverage", {})
        missing = [et_id for et_id, ids in coverage.items() if not ids]
        if missing:
            section_lines.extend(["### Gaps", ""])
            for et_id in missing:
                section_lines.append(f"> ⚠️ **GAP**: {et_id} (`{et_id}`) — no matching evidence found")
            section_lines.append("")

        section_lines.extend(["### Evidence", ""])
        for art in mapping.get("mapped_artifacts", []):
            section_lines.append(
                f"- {art['description']} [{art['file_path']} — {art.get('evidence_type_matched', 'mapped evidence')}]"
            )
        for tst in mapping.get("mapped_tests", []):
            section_lines.append(f"- {tst['description']} [{tst['file_path']} — test evidence]")
        if not mapping.get("mapped_artifacts", []) and not mapping.get("mapped_tests", []):
            section_lines.append("- No evidence entries mapped.")
        section_lines.extend(["", "---", ""])
        control_sections.append("\n".join(section_lines))

    rendered = rendered.replace(NARRATIVE_SUMMARY_LOOP_BLOCK, "\n".join(summary_rows))
    rendered = rendered.replace(NARRATIVE_CONTROL_LOOP_BLOCK, "\n".join(control_sections).rstrip())
    return rendered.rstrip() + "\n"


def _build_validation_report_md(citation_validation, mapped_evidence, llm_response):
    """Build validation_report.md from the validation template."""
    is_degraded = llm_response.get("status") == "degraded"
    timestamp = llm_response.get("yaml_front_matter", {}).get(
        "generated", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    mappings = mapped_evidence.get("mappings", [])

    total_citations = citation_validation.get("total_citations", 0)
    resolved = citation_validation.get("resolved", 0)
    unresolved = citation_validation.get("unresolved", 0)
    resolution_rate = citation_validation.get("resolution_rate", 0.0)
    citations = citation_validation.get("citations", [])

    template, template_path = _load_template(VALIDATION_TEMPLATE_CANDIDATES)
    log("INFO", f"Using validation template: {template_path}")

    rendered = _replace_placeholders(
        template,
        {
            "generated": timestamp,
            "total_citations": total_citations,
            "valid_citations": resolved,
            "invalid_citations": unresolved,
            "resolution_rate": f"{resolution_rate:.0%}",
        },
    )

    citation_rows = []
    if citations:
        for c in citations:
            fp = c.get("file_path_extracted", "")
            citation_text = c.get("citation_text", "")
            description = citation_text.split(" — ", 1)[1] if " — " in citation_text else ""
            status = "✅ Yes" if c.get("resolved") else "❌ No"
            citation_rows.append(f"| [{fp} — {description}] | `{fp}` | N/A | {status} |")
    else:
        citation_rows.append("| [N/A — no citations found] | `N/A` | N/A | N/A |")

    coverage_rows = []
    warnings = []
    for mapping in mappings:
        ctrl_id = mapping["control_id"]
        ctrl_name = mapping["control_name"]
        art_count = mapping.get("artifact_count", 0)
        tst_count = mapping.get("test_count", 0)
        coverage = mapping.get("evidence_type_coverage", {})

        covered = [et for et, ids in coverage.items() if ids]
        missing = [et for et, ids in coverage.items() if not ids]

        expected_count = len(coverage)
        matched_count = len(covered)
        unmatched_count = len(missing)
        coverage_pct = f"{round((matched_count / expected_count) * 100)}%" if expected_count else "0%"
        coverage_rows.append(
            f"| {ctrl_name} ({ctrl_id}) | {expected_count} | {matched_count} | {unmatched_count} | {coverage_pct} |"
        )

        for missing_id in missing:
            warnings.append(
                f"{ctrl_id}: Missing evidence type `{missing_id}` — "
                f"no matching artifacts found (artifacts={art_count}, tests={tst_count})"
            )

    if warnings:
        warning_lines = "\n".join(f"- **Coverage**: {w}" for w in warnings)
    else:
        warning_lines = "No items flagged. All citations resolved and all expected evidence types matched."
    if is_degraded:
        warning_lines = (
            "- **Degraded Mode**: LLM was unavailable; report generated from deterministic pipeline only.\n"
            + warning_lines
        )

    rendered = rendered.replace(VALIDATION_CITATION_LOOP_BLOCK, "\n".join(citation_rows))
    rendered = rendered.replace(VALIDATION_CONTROL_LOOP_BLOCK, "\n".join(coverage_rows))
    rendered = rendered.replace(VALIDATION_FLAGS_BLOCK, warning_lines)
    return rendered.rstrip() + "\n"


def run(llm_response, citation_validation, mapped_evidence, output_dir):
    """Write the two output Markdown files."""
    log("INFO", "Starting write_output.py")

    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        log("ERROR", f"WRITE_ERROR: Cannot create output directory {output_dir} — {e}")
        sys.exit(1)

    narratives_path = os.path.join(output_dir, "rcsa_control_narratives.md")
    report_path = os.path.join(output_dir, "validation_report.md")

    narratives_content = _build_narratives_md(llm_response, mapped_evidence)
    report_content = _build_validation_report_md(
        citation_validation, mapped_evidence, llm_response
    )

    try:
        with open(narratives_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(narratives_content)
        log("INFO", f"Written: {narratives_path}")
    except OSError as e:
        log("ERROR", f"WRITE_ERROR: Cannot write {narratives_path} — {e}")
        sys.exit(1)

    try:
        with open(report_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(report_content)
        log("INFO", f"Written: {report_path}")
    except OSError as e:
        log("ERROR", f"WRITE_ERROR: Cannot write {report_path} — {e}")
        sys.exit(1)

    result = {
        "status": "success",
        "output_files": [narratives_path, report_path],
    }

    log("INFO", f"Completed — status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Write RCSA output Markdown files")
    parser.add_argument("--llm-response", required=True,
                        help="Path to LLM response JSON (output of orchestrate_llm.py)")
    parser.add_argument("--citation-validation", required=True,
                        help="Path to citation validation JSON (output of validate_citations.py)")
    parser.add_argument("--mapped-evidence", required=True,
                        help="Path to mapped evidence JSON (output of map_evidence.py)")
    parser.add_argument("--output-dir", required=True,
                        help="Directory to write output files to")
    args = parser.parse_args()

    llm_response = read_json_file(args.llm_response)
    citation_validation = read_json_file(args.citation_validation)
    mapped_evidence = read_json_file(args.mapped_evidence)

    result = run(llm_response, citation_validation, mapped_evidence, args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
