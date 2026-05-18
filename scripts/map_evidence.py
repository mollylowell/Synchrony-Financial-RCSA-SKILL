"""F6 Script 3: Map Evidence to Controls.

Maps artifacts and tests to compliance controls using keyword/path-based
heuristics for artifact-to-evidence-type matching, and direct controls_relevant
lookups for test-to-control mapping. Produces MappedEvidence with gap detection.
"""

import argparse
import json
import re
import sys


SCRIPT_ID = "MAP"
ABSOLUTE_SCORE_THRESHOLD = 2
RELATIVE_SCORE_WINDOW = 1


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


def _tokenize(text):
    """Extract lowercase keyword tokens from text, splitting on non-alpha characters."""
    return set(re.findall(r"[a-z]{3,}", text.lower()))


def _prefix_match_count(set_a, set_b):
    """Count how many tokens in set_a are prefixes of tokens in set_b (or vice versa).

    Only counts pairs where neither is already an exact match and the prefix
    is at least 4 characters long.
    """
    count = 0
    for a in set_a:
        if a in set_b:
            continue
        if len(a) < 4:
            continue
        for b in set_b:
            if len(b) < 4:
                continue
            if a.startswith(b) or b.startswith(a):
                count += 1
                break
    return count


def _score_artifact_for_evidence_type(artifact, evidence_type, control_context_tokens=None):
    """Score how well an artifact matches an evidence type using keyword overlap.

    Uses three scoring layers:
    1. Description keyword overlap (exact + prefix/stem matching)
    2. Evidence type ID token matching (requires majority match to earn bonus)
    3. Directory-segment bonus (first path directory matches control context)

    Args:
        artifact: Artifact dict with file_path and description.
        evidence_type: Evidence type dict with id, label, description.
        control_context_tokens: Optional set of tokens from the control's name,
            objective, and ALL evidence type descriptions combined, used as
            a domain-level relevance signal.

    Returns a score >= 0. Higher means better match.
    """
    et_id_tokens = set(evidence_type["id"].lower().split("_"))
    et_desc_tokens = _tokenize(evidence_type["description"])
    et_label_tokens = _tokenize(evidence_type["label"])
    et_all = et_id_tokens | et_desc_tokens | et_label_tokens

    art_desc_tokens = _tokenize(artifact["description"])
    art_path_tokens = _tokenize(artifact["file_path"])
    art_all = art_desc_tokens | art_path_tokens

    # Layer 1: description overlap (exact + prefix)
    exact_overlap = art_all & et_all
    score = len(exact_overlap)
    score += _prefix_match_count(art_all, et_all)

    # Layer 2: ID token bonus (only when >50% of ID tokens match)
    id_exact = art_all & et_id_tokens
    id_prefix = _prefix_match_count(art_all, et_id_tokens)
    id_match_count = len(id_exact) + id_prefix
    if len(et_id_tokens) > 1 and id_match_count / len(et_id_tokens) >= 0.5:
        score += id_match_count * 3

    # Layer 3: Directory-segment bonus
    # The first path directory is the strongest domain signal. If it matches
    # tokens in the broader control context, this artifact likely belongs here.
    if control_context_tokens:
        dir_segment = artifact["file_path"].split("/")[0].lower()
        dir_tokens = _tokenize(dir_segment) if len(dir_segment) >= 3 else set()
        if dir_segment and len(dir_segment) >= 3:
            dir_tokens.add(dir_segment)

        for dt in dir_tokens:
            for ct in control_context_tokens:
                if len(dt) >= 4 and len(ct) >= 4 and (dt.startswith(ct) or ct.startswith(dt)):
                    score += 5
                    break
            else:
                continue
            break

        ctrl_exact = art_all & control_context_tokens
        ctrl_prefix = _prefix_match_count(art_all, control_context_tokens)
        score += len(ctrl_exact) + ctrl_prefix

    return score


def _find_best_evidence_type(artifact, evidence_types, control_tokens=None):
    """Find the best matching evidence type for an artifact. Returns (et_id, score) or (None, 0)."""
    best_et = None
    best_score = 0

    for et in evidence_types:
        score = _score_artifact_for_evidence_type(artifact, et, control_tokens)
        if score > best_score:
            best_score = score
            best_et = et["id"]

    return best_et, best_score


def run(registry_data, control_library_data):
    """Map evidence to controls. Returns MappedEvidence dict.

    Args:
        registry_data: ArtifactRegistry dict (the 'registry' key contents or full result).
        control_library_data: Parsed control library JSON.
    """
    log("INFO", "Starting map_evidence.py")

    registry = registry_data.get("registry", registry_data)
    artifacts_dict = registry.get("artifacts", {})
    tests_dict = registry.get("tests", {})
    controls = control_library_data.get("controls", [])

    # Build per-control keyword context from name + objective + all evidence type descriptions
    ctrl_token_map = {}
    for ctrl in controls:
        tokens = _tokenize(ctrl["name"]) | _tokenize(ctrl["objective"])
        for et in ctrl.get("evidence_types", []):
            tokens |= set(et["id"].lower().split("_"))
            tokens |= _tokenize(et["description"])
            tokens |= _tokenize(et["label"])
        ctrl_token_map[ctrl["id"]] = tokens

    # Phase 1: For each artifact, retain meaningful matches across controls.
    # Keep only each control's best evidence_type for that artifact.
    # Then keep matches that pass:
    #   1) absolute score threshold, and
    #   2) relative-to-best score window.
    artifact_matches = {}  # art_id -> [{control_id, evidence_type_id, score}, ...]
    for art_id, art in artifacts_dict.items():
        per_control_candidates = []
        artifact_best_score = 0
        for ctrl in controls:
            ctrl_tokens = ctrl_token_map.get(ctrl["id"], set())
            et_id, score = _find_best_evidence_type(
                art, ctrl.get("evidence_types", []), ctrl_tokens
            )
            if et_id and score > 0:
                per_control_candidates.append({
                    "control_id": ctrl["id"],
                    "evidence_type_id": et_id,
                    "score": score,
                })
                if score > artifact_best_score:
                    artifact_best_score = score

        retained = []
        if artifact_best_score > 0:
            min_relative_score = artifact_best_score - RELATIVE_SCORE_WINDOW
            for candidate in per_control_candidates:
                if candidate["score"] < ABSOLUTE_SCORE_THRESHOLD:
                    continue
                if candidate["score"] < min_relative_score:
                    continue
                retained.append(candidate)

        if retained:
            artifact_matches[art_id] = retained

    # Phase 2: Build per-control mappings
    all_mapped_artifact_ids = set()
    all_mapped_test_ids = set()
    mappings = []

    for ctrl in controls:
        ctrl_id = ctrl["id"]
        ctrl_name = ctrl["name"]
        ctrl_objective = ctrl["objective"]
        evidence_types = ctrl.get("evidence_types", [])

        mapped_artifacts = []
        evidence_type_coverage = {et["id"]: [] for et in evidence_types}

        for art_id, matches in artifact_matches.items():
            for match in matches:
                if match["control_id"] != ctrl_id:
                    continue
                art = artifacts_dict[art_id]
                mapped_artifacts.append({
                    "id": art["id"],
                    "file_path": art["file_path"],
                    "file_type": art["file_type"],
                    "description": art["description"],
                    "evidence_type_matched": match["evidence_type_id"],
                    "match_score": match["score"],
                    "source": art.get("source", "artifact_index"),
                })
                evidence_type_coverage[match["evidence_type_id"]].append(art["id"])
                all_mapped_artifact_ids.add(art_id)

        mapped_tests = []
        for tst_id, tst in tests_dict.items():
            if ctrl_id in tst.get("controls_relevant", []):
                mapped_tests.append({
                    "id": tst["id"],
                    "file_path": tst["file_path"],
                    "description": tst["description"],
                    "source": tst.get("source", "test_catalog"),
                })
                all_mapped_test_ids.add(tst_id)

        gap_flag = len(mapped_artifacts) == 0 and len(mapped_tests) == 0

        if gap_flag:
            log("WARN", f"Control {ctrl_id} has 0 mapped artifacts and 0 mapped tests — gap detected")
        elif len(mapped_tests) == 0:
            log("WARN", f"Control {ctrl_id} has 0 mapped tests")

        mappings.append({
            "control_id": ctrl_id,
            "control_name": ctrl_name,
            "control_objective": ctrl_objective,
            "mapped_artifacts": mapped_artifacts,
            "mapped_tests": mapped_tests,
            "evidence_type_coverage": evidence_type_coverage,
            "gap_flag": gap_flag,
            "artifact_count": len(mapped_artifacts),
            "test_count": len(mapped_tests),
        })

    unmapped_artifacts = [
        aid for aid in artifacts_dict if aid not in all_mapped_artifact_ids
    ]
    unmapped_tests = [
        tid for tid in tests_dict if tid not in all_mapped_test_ids
    ]

    controls_with_evidence = sum(1 for m in mappings if not m["gap_flag"])
    controls_with_gaps = sum(1 for m in mappings if m["gap_flag"])
    total_artifact_control_links = sum(len(matches) for matches in artifact_matches.values())

    result = {
        "status": "success",
        "mappings": mappings,
        "summary": {
            "total_controls": len(mappings),
            "controls_with_evidence": controls_with_evidence,
            "controls_with_gaps": controls_with_gaps,
            "total_artifacts_mapped": len(all_mapped_artifact_ids),
            "total_artifact_control_links": total_artifact_control_links,
            "total_tests_mapped": len(all_mapped_test_ids),
            "unmapped_artifacts": unmapped_artifacts,
            "unmapped_tests": unmapped_tests,
        },
    }

    log("INFO", f"Mapped {len(all_mapped_artifact_ids)} artifacts and "
        f"{total_artifact_control_links} artifact-control links, "
        f"{len(all_mapped_test_ids)} tests across {len(mappings)} controls "
        f"({controls_with_gaps} gaps)")
    log("INFO", f"Completed — status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Map evidence to RCSA controls")
    parser.add_argument("--registry", required=True, help="Path to registry JSON (output of build_registry.py)")
    parser.add_argument("--control-library", required=True, help="Path to control library JSON")
    args = parser.parse_args()

    registry_data = read_json_file(args.registry)
    control_library_data = read_json_file(args.control_library)

    result = run(registry_data, control_library_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
