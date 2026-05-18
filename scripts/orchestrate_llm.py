"""F6 Script 4: Orchestrate LLM Invocation.

Dual-mode script:
  - Format mode: packages mapped evidence into an LLM prompt string
  - Parse mode: parses the raw LLM Markdown response into structured LLMResponse

F6 never calls the LLM directly; F5 owns LLM invocation.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone


SCRIPT_ID = "LLM"

CITATION_REGEX = re.compile(r"\[([^\]]+?)\s\u2014\s([^\]]+?)\]")
CONFIDENCE_REGEX = re.compile(r"\*\*Confidence\*\*:\s*(HIGH|MEDIUM|LOW|GAP)", re.IGNORECASE)
SECTION_REGEX = re.compile(
    r"^##\s+(?:(?P<id_first>[A-Z]{2,4})\s*[—–-]\s*(?P<name_from_id>.+?)|"
    r"(?P<name_first>.+?)\s*\((?P<id_from_name>[A-Z]{2,4})\))\s*$",
    re.MULTILINE,
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
        log("ERROR", f"PARSE_ERROR: {file_path} is not valid JSON \u2014 {e}")
        sys.exit(1)


def run_format(mapped_evidence):
    """Format mapped evidence into an LLM prompt string.

    Args:
        mapped_evidence: MappedEvidence dict (output of map_evidence.py).

    Returns:
        A prompt string for the LLM.
    """
    log("INFO", "Starting orchestrate_llm.py (format mode)")

    mappings = mapped_evidence.get("mappings", [])
    lines = []

    lines.append("# RCSA Control Narrative Generation")
    lines.append("")
    lines.append("Generate a citation-backed narrative for each control below. "
                 "Follow these rules strictly:")
    lines.append("")
    lines.append("## Output Format")
    lines.append("")
    lines.append("For each control, produce a section with this exact structure:")
    lines.append("")
    lines.append("```")
    lines.append("## [CONTROL_ID] \u2014 [Control Name]")
    lines.append("")
    lines.append("**Confidence**: [HIGH|MEDIUM|LOW|GAP]")
    lines.append("")
    lines.append("[3-5 sentence narrative with inline citations]")
    lines.append("")
    lines.append("---")
    lines.append("```")
    lines.append("")
    lines.append("## Citation Format")
    lines.append("")
    lines.append("Use this exact format for inline citations:")
    lines.append("`[file_path \u2014 description]`")
    lines.append("")
    lines.append("Example: `[auth/oauth_config.yaml \u2014 OAuth2 provider configuration]`")
    lines.append("")
    lines.append("Only cite artifacts and tests listed in the evidence below. "
                 "Never invent file paths or cite external sources.")
    lines.append("")
    lines.append("## Confidence Tier Rubric")
    lines.append("")
    lines.append("| Tier | Criteria |")
    lines.append("|---|---|")
    lines.append("| HIGH | Multiple artifacts + tests covering all evidence types |")
    lines.append("| MEDIUM | Some evidence types covered, others missing |")
    lines.append("| LOW | Few artifacts, few or no tests |")
    lines.append("| GAP | Zero artifacts AND zero tests mapped |")
    lines.append("")
    lines.append("## Anti-Hallucination Rules")
    lines.append("")
    lines.append("1. Never imply compliance without cited evidence")
    lines.append("2. Never cite artifacts not listed below")
    lines.append("3. If a control has no evidence (gap_flag: true), produce a [GAP] statement")
    lines.append("4. Prefer explicit gap flags over uncertain claims")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Controls and Evidence")
    lines.append("")

    for mapping in mappings:
        ctrl_id = mapping["control_id"]
        ctrl_name = mapping["control_name"]
        ctrl_obj = mapping["control_objective"]
        gap_flag = mapping.get("gap_flag", False)

        lines.append(f"### {ctrl_id} \u2014 {ctrl_name}")
        lines.append(f"**Objective**: {ctrl_obj}")
        lines.append(f"**Gap Flag**: {'true' if gap_flag else 'false'}")
        lines.append("")

        artifacts = mapping.get("mapped_artifacts", [])
        if artifacts:
            lines.append("**Mapped Artifacts:**")
            for art in artifacts:
                lines.append(f"- `{art['file_path']}` ({art['file_type']}) \u2014 {art['description']} "
                             f"[evidence type: {art.get('evidence_type_matched', 'unknown')}]")
            lines.append("")

        tests = mapping.get("mapped_tests", [])
        if tests:
            lines.append("**Mapped Tests:**")
            for tst in tests:
                lines.append(f"- `{tst['file_path']}` \u2014 {tst['description']}")
            lines.append("")

        coverage = mapping.get("evidence_type_coverage", {})
        missing = [et for et, ids in coverage.items() if not ids]
        if missing:
            lines.append(f"**Missing Evidence Types**: {', '.join(missing)}")
            lines.append("")

        if gap_flag:
            lines.append("> **INSTRUCTION**: This control has NO evidence. "
                         "Produce a [GAP] narrative with confidence GAP.")
            lines.append("")

        lines.append("---")
        lines.append("")

    prompt = "\n".join(lines)
    log("INFO", f"Formatted prompt for {len(mappings)} controls "
        f"({sum(len(m.get('mapped_artifacts', [])) for m in mappings)} artifacts, "
        f"{sum(len(m.get('mapped_tests', [])) for m in mappings)} tests)")
    log("INFO", "Completed \u2014 status: success")
    return prompt


def _split_into_sections(markdown_text):
    """Split LLM markdown response into per-control sections."""
    matches = list(SECTION_REGEX.finditer(markdown_text))
    if not matches:
        return {}

    sections = {}
    for i, match in enumerate(matches):
        ctrl_id = match.group("id_first") or match.group("id_from_name")
        if not ctrl_id:
            continue
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        sections[ctrl_id] = markdown_text[start:end].strip()

    return sections


def _extract_confidence(section_text):
    """Extract confidence tier from a control section."""
    m = CONFIDENCE_REGEX.search(section_text)
    if m:
        return m.group(1).upper()
    return "UNAVAILABLE"


def _extract_citations(section_text):
    """Extract all citations from a control section. Returns list of (file_path, description)."""
    return CITATION_REGEX.findall(section_text)


def _extract_narrative(section_text):
    """Extract the narrative text from a control section (everything after Confidence line)."""
    lines = section_text.split("\n")
    narrative_lines = []
    past_confidence = False
    for line in lines:
        if CONFIDENCE_REGEX.search(line):
            past_confidence = True
            continue
        if line.startswith("## "):
            continue
        if past_confidence:
            stripped = line.strip()
            if stripped == "---":
                break
            narrative_lines.append(line)

    text = "\n".join(narrative_lines).strip()
    return text


def _build_path_to_entry_index(mappings):
    """Build path -> {id, kind} index from mapped evidence entries.

    If multiple different IDs map to the same path, mark as ambiguous by storing
    id as None. This avoids writing incorrect IDs into contract fields.
    """
    index = {}

    for mapping in mappings:
        for art in mapping.get("mapped_artifacts", []):
            file_path = art.get("file_path")
            entry_id = art.get("id")
            if not file_path or not entry_id:
                continue
            existing = index.get(file_path)
            if existing and existing["id"] != entry_id:
                index[file_path] = {"id": None, "kind": "ambiguous"}
            elif not existing:
                index[file_path] = {"id": entry_id, "kind": "artifact"}

        for tst in mapping.get("mapped_tests", []):
            file_path = tst.get("file_path")
            entry_id = tst.get("id")
            if not file_path or not entry_id:
                continue
            existing = index.get(file_path)
            if existing and existing["id"] != entry_id:
                index[file_path] = {"id": None, "kind": "ambiguous"}
            elif not existing:
                index[file_path] = {"id": entry_id, "kind": "test"}

    return index


def _extract_control_section_fallback(markdown_text, control_id):
    """Best-effort extraction of one control section from malformed markdown."""
    pattern = re.compile(
        rf"^##\s+(?:"
        rf"{re.escape(control_id)}(?:\s*[—–-]\s*.*)?"
        rf"|.+?\(\s*{re.escape(control_id)}\s*\)"
        rf")\s*$.*?"
        rf"(?=^##\s+(?:"
        rf"[A-Z]{{2,4}}(?:\s*[—–-]\s*.*)?"
        rf"|.+?\(\s*[A-Z]{{2,4}}\s*\)"
        rf")\s*$|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown_text)
    if not match:
        return None
    return match.group(0).strip()


def _build_unavailable_narrative(mapping_info):
    return {
        "confidence": "UNAVAILABLE",
        "narrative_text": "",
        "artifacts_cited": [],
        "tests_cited": [],
        "citation_paths_extracted": [],
        "unresolved_citation_paths": [],
        "evidence_types_covered": [],
        "gap_flag": mapping_info.get("gap_flag", False),
    }


def _parse_control_section(section, mapping_info, path_to_entry_index):
    confidence = _extract_confidence(section)
    narrative_text = _extract_narrative(section)
    citations = _extract_citations(section)

    artifacts_cited = []
    tests_cited = []
    citation_paths_extracted = []
    unresolved_citation_paths = []
    for fp, _desc in citations:
        fp_clean = fp.strip()
        citation_paths_extracted.append(fp_clean)
        resolved_entry = path_to_entry_index.get(fp_clean)
        if not resolved_entry or resolved_entry["id"] is None:
            unresolved_citation_paths.append(fp_clean)
            continue

        resolved_id = resolved_entry["id"]
        if resolved_entry["kind"] == "test":
            tests_cited.append(resolved_id)
        else:
            artifacts_cited.append(resolved_id)

    ev_types_covered = []
    coverage = mapping_info.get("evidence_type_coverage", {})
    for et_id, art_ids in coverage.items():
        if art_ids:
            ev_types_covered.append(et_id)

    return {
        "confidence": confidence,
        "narrative_text": narrative_text,
        "artifacts_cited": artifacts_cited,
        "tests_cited": tests_cited,
        # Debug-only fields; contract fields above remain IDs only.
        "citation_paths_extracted": citation_paths_extracted,
        "unresolved_citation_paths": unresolved_citation_paths,
        "evidence_types_covered": ev_types_covered,
        "gap_flag": mapping_info.get("gap_flag", False),
    }


def run_parse(llm_response_text, mapped_evidence):
    """Parse raw LLM response into structured LLMResponse.

    Args:
        llm_response_text: Raw Markdown string from the LLM (or empty/None for degradation).
        mapped_evidence: MappedEvidence dict for context and fallback.

    Returns:
        LLMResponse dict.
    """
    log("INFO", "Starting orchestrate_llm.py (parse mode)")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    mappings = mapped_evidence.get("mappings", [])
    expected_controls = {m["control_id"]: m for m in mappings}
    path_to_entry_index = _build_path_to_entry_index(mappings)

    if not llm_response_text or not llm_response_text.strip():
        log("WARN", "LLM_ERROR: Empty response received \u2014 entering degraded mode")
        result = {
            "status": "degraded",
            "reason": "LLM unavailable \u2014 raw evidence provided without narratives",
            "narratives": {},
            "yaml_front_matter": {
                "title": "RCSA Control Narrative Assessment \u2014 DEGRADED MODE",
                "generated": timestamp,
                "controls_assessed": len(expected_controls),
                "controls_passing": 0,
                "controls_low_confidence": 0,
                "controls_gap": 0,
                "framework": "Custom Demo Controls",
                "mode": "degraded",
            },
            "raw_markdown": None,
            "mapped_evidence_passthrough": mapped_evidence,
        }
        log("INFO", "Completed \u2014 status: degraded")
        return result

    sections = _split_into_sections(llm_response_text)

    if not sections:
        log("WARN", "LLM_ERROR: Could not parse standard control sections \u2014 attempting per-control fallback parsing")
        narratives = {}
        parsed_controls = 0
        for ctrl_id, mapping_info in expected_controls.items():
            section = _extract_control_section_fallback(llm_response_text, ctrl_id)
            if section:
                narratives[ctrl_id] = _parse_control_section(
                    section, mapping_info, path_to_entry_index
                )
                parsed_controls += 1
            else:
                narratives[ctrl_id] = _build_unavailable_narrative(mapping_info)

        controls_passing = sum(
            1 for n in narratives.values() if n["confidence"] in ("HIGH", "MEDIUM")
        )
        controls_low = sum(
            1 for n in narratives.values() if n["confidence"] == "LOW"
        )
        controls_gap = sum(
            1 for n in narratives.values() if n["confidence"] == "GAP"
        )

        result = {
            "status": "success",
            "narratives": narratives,
            "yaml_front_matter": {
                "title": "RCSA Control Narrative Assessment",
                "generated": timestamp,
                "controls_assessed": len(expected_controls),
                "controls_passing": controls_passing,
                "controls_low_confidence": controls_low,
                "controls_gap": controls_gap,
                "framework": "Custom Demo Controls",
            },
            "raw_markdown": llm_response_text,
            "parse_warning": (
                "LLM response malformed for standard parsing; fallback per-control "
                f"extraction parsed {parsed_controls}/{len(expected_controls)} controls"
            ),
        }
        log("INFO", f"Completed \u2014 status: {result['status']}")
        return result

    narratives = {}
    for ctrl_id in expected_controls:
        mapping_info = expected_controls.get(ctrl_id, {})
        if ctrl_id in sections:
            narratives[ctrl_id] = _parse_control_section(
                sections[ctrl_id], mapping_info, path_to_entry_index
            )
        else:
            log("WARN", f"Control {ctrl_id} missing from LLM response \u2014 marking as UNAVAILABLE")
            narratives[ctrl_id] = _build_unavailable_narrative(mapping_info)

    controls_passing = sum(
        1 for n in narratives.values() if n["confidence"] in ("HIGH", "MEDIUM")
    )
    controls_low = sum(
        1 for n in narratives.values() if n["confidence"] == "LOW"
    )
    controls_gap = sum(
        1 for n in narratives.values() if n["confidence"] == "GAP"
    )

    result = {
        "status": "success",
        "narratives": narratives,
        "yaml_front_matter": {
            "title": "RCSA Control Narrative Assessment",
            "generated": timestamp,
            "controls_assessed": len(expected_controls),
            "controls_passing": controls_passing,
            "controls_low_confidence": controls_low,
            "controls_gap": controls_gap,
            "framework": "Custom Demo Controls",
        },
        "raw_markdown": llm_response_text,
    }

    log("INFO", f"Parsed {len(sections)} control sections from LLM response "
        f"(passing={controls_passing}, low={controls_low}, gap={controls_gap})")
    log("INFO", f"Completed \u2014 status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Orchestrate LLM for RCSA narratives")
    parser.add_argument("--mapped-evidence", required=True,
                        help="Path to mapped evidence JSON (output of map_evidence.py)")
    parser.add_argument("--mode", required=True, choices=["format", "parse"],
                        help="'format' to build LLM prompt, 'parse' to parse LLM response")
    parser.add_argument("--llm-response", default=None,
                        help="Path to LLM response file (required for parse mode)")
    args = parser.parse_args()

    mapped_evidence = read_json_file(args.mapped_evidence)

    if args.mode == "format":
        prompt = run_format(mapped_evidence)
        print(prompt)
    elif args.mode == "parse":
        if args.llm_response is None:
            log("ERROR", "INTERNAL_ERROR: --llm-response is required for parse mode")
            sys.exit(1)

        try:
            with open(args.llm_response, "r", encoding="utf-8-sig") as f:
                llm_text = f.read()
        except FileNotFoundError:
            log("WARN", f"LLM_ERROR: Response file not found at {args.llm_response} "
                "\u2014 entering degraded mode")
            llm_text = ""

        result = run_parse(llm_text, mapped_evidence)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
