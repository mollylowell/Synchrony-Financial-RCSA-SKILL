"""F6 Script 5: Validate Citations.

Extracts all inline citations from the LLM's narrative output using the
[file_path — description] regex pattern, resolves each file_path against
the artifact registry's file_path_index, and produces a CitationValidationResult.

Unresolved citations are reported (not treated as errors that stop the pipeline).
"""

import argparse
import json
import re
import sys


SCRIPT_ID = "CITATIONS"

CITATION_REGEX = re.compile(r"\[([^\]]+?)\s\u2014\s([^\]]+?)\]")


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


def run(llm_response, registry_data):
    """Validate all citations in the LLM response against the artifact registry.

    Args:
        llm_response: LLMResponse dict (output of orchestrate_llm.py parse mode).
        registry_data: ArtifactRegistry dict (output of build_registry.py).

    Returns:
        CitationValidationResult dict.
    """
    log("INFO", "Starting validate_citations.py")

    registry = registry_data.get("registry", registry_data)
    file_path_index = registry.get("file_path_index", {})

    if llm_response.get("status") == "degraded":
        log("INFO", "LLM response is degraded \u2014 no citations to validate")
        result = {
            "status": "success",
            "total_citations": 0,
            "resolved": 0,
            "unresolved": 0,
            "resolution_rate": 0.0,
            "citations": [],
            "unresolved_list": [],
        }
        log("INFO", f"Completed \u2014 status: {result['status']}")
        return result

    narratives = llm_response.get("narratives", {})
    all_citations = []
    unresolved_list = []

    for ctrl_id, narrative_data in narratives.items():
        narrative_text = narrative_data.get("narrative_text", "")
        matches = CITATION_REGEX.findall(narrative_text)

        for file_path_raw, description in matches:
            file_path = file_path_raw.strip()
            resolved_to = file_path_index.get(file_path)
            is_resolved = resolved_to is not None

            citation_entry = {
                "citation_text": f"{file_path} \u2014 {description.strip()}",
                "file_path_extracted": file_path,
                "resolved_to": resolved_to,
                "resolved": is_resolved,
                "control_id": ctrl_id,
            }
            all_citations.append(citation_entry)

            if not is_resolved:
                log("WARN", f"VALIDATION_ERROR: Citation '{file_path}' in control "
                    f"{ctrl_id} does not resolve to any artifact or test in the registry")
                unresolved_list.append({
                    "citation_text": citation_entry["citation_text"],
                    "file_path_extracted": file_path,
                    "control_id": ctrl_id,
                })

    total = len(all_citations)
    resolved_count = sum(1 for c in all_citations if c["resolved"])
    unresolved_count = total - resolved_count
    resolution_rate = resolved_count / total if total > 0 else 0.0

    result = {
        "status": "success",
        "total_citations": total,
        "resolved": resolved_count,
        "unresolved": unresolved_count,
        "resolution_rate": round(resolution_rate, 4),
        "citations": all_citations,
        "unresolved_list": unresolved_list,
    }

    log("INFO", f"Validated {total} citations: {resolved_count} resolved, "
        f"{unresolved_count} unresolved (rate: {resolution_rate:.1%})")
    log("INFO", f"Completed \u2014 status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Validate RCSA citations against registry")
    parser.add_argument("--llm-response", required=True,
                        help="Path to LLM response JSON (output of orchestrate_llm.py parse mode)")
    parser.add_argument("--registry", required=True,
                        help="Path to registry JSON (output of build_registry.py)")
    args = parser.parse_args()

    llm_response = read_json_file(args.llm_response)
    registry_data = read_json_file(args.registry)

    result = run(llm_response, registry_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
