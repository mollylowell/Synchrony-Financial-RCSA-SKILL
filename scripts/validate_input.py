"""F6 Script 1: Validate Input Files.

Validates the 3 JSON input files (control library, artifact index, test catalog)
for existence, JSON parsing, required fields, ID formats, duplicates, and
cross-references before any pipeline processing begins.
"""

import argparse
import json
import re
import sys


SCRIPT_ID = "VALIDATE"
CONTROL_ID_PATTERN = re.compile(r"^[A-Z]{2,4}$")
ARTIFACT_ID_PATTERN = re.compile(r"^ART-\d{3}$")
TEST_ID_PATTERN = re.compile(r"^TST-\d{3}$")


def log(level, message):
    print(f"[F6-{SCRIPT_ID}] {level}: {message}", file=sys.stderr)


def _validate_control_library(data):
    errors = []
    if "controls" not in data:
        errors.append("Missing required key: 'controls'")
        return errors
    controls = data["controls"]
    if not isinstance(controls, list) or len(controls) == 0:
        errors.append("'controls' must be a non-empty array")
        return errors

    seen_ids = {}
    for i, ctrl in enumerate(controls):
        prefix = f"controls[{i}]"
        for field in ("id", "name", "objective"):
            if field not in ctrl or not isinstance(ctrl.get(field), str) or not ctrl[field].strip():
                errors.append(f"Missing or empty required field: {prefix}.{field}")

        ctrl_id = ctrl.get("id", "")
        if ctrl_id and not CONTROL_ID_PATTERN.match(ctrl_id):
            errors.append(
                f"Invalid control ID '{ctrl_id}' at {prefix}.id "
                f"— must match pattern ^[A-Z]{{2,4}}$"
            )
        if ctrl_id in seen_ids:
            errors.append(
                f"Duplicate control ID '{ctrl_id}' at {prefix} "
                f"and controls[{seen_ids[ctrl_id]}]"
            )
        else:
            seen_ids[ctrl_id] = i

        if "evidence_types" not in ctrl or not isinstance(ctrl.get("evidence_types"), list) or len(ctrl.get("evidence_types", [])) == 0:
            errors.append(f"'{prefix}.evidence_types' must be a non-empty array")
        else:
            et_ids = set()
            for j, et in enumerate(ctrl["evidence_types"]):
                et_prefix = f"{prefix}.evidence_types[{j}]"
                for field in ("id", "label", "description"):
                    if field not in et or not isinstance(et.get(field), str) or not et[field].strip():
                        errors.append(f"Missing or empty required field: {et_prefix}.{field}")
                et_id = et.get("id", "")
                if et_id in et_ids:
                    errors.append(f"Duplicate evidence_type ID '{et_id}' within {prefix}")
                et_ids.add(et_id)

    return errors


def _validate_artifact_index(data):
    errors = []
    if "artifacts" not in data:
        errors.append("Missing required key: 'artifacts'")
        return errors
    artifacts = data["artifacts"]
    if not isinstance(artifacts, list) or len(artifacts) == 0:
        errors.append("'artifacts' must be a non-empty array")
        return errors

    seen_ids = {}
    seen_paths = {}
    for i, art in enumerate(artifacts):
        prefix = f"artifacts[{i}]"
        for field in ("id", "file_path", "file_type", "description"):
            if field not in art or not isinstance(art.get(field), str) or not art[field].strip():
                errors.append(f"Missing or empty required field: {prefix}.{field}")

        art_id = art.get("id", "")
        if art_id and not ARTIFACT_ID_PATTERN.match(art_id):
            errors.append(
                f"Invalid artifact ID '{art_id}' at {prefix}.id "
                f"— must match pattern ART-NNN"
            )
        if art_id in seen_ids:
            errors.append(
                f"Duplicate artifact ID '{art_id}' at {prefix} "
                f"and artifacts[{seen_ids[art_id]}]"
            )
        else:
            seen_ids[art_id] = i

        fp = art.get("file_path", "")
        if fp in seen_paths:
            errors.append(
                f"Duplicate file_path '{fp}' at {prefix} "
                f"and artifacts[{seen_paths[fp]}]"
            )
        else:
            seen_paths[fp] = i

    return errors


def _validate_test_catalog(data, valid_control_ids):
    errors = []
    if "tests" not in data:
        errors.append("Missing required key: 'tests'")
        return errors
    tests = data["tests"]
    if not isinstance(tests, list) or len(tests) == 0:
        errors.append("'tests' must be a non-empty array")
        return errors

    seen_ids = {}
    seen_paths = {}
    for i, tst in enumerate(tests):
        prefix = f"tests[{i}]"
        for field in ("id", "file_path", "file_type", "description"):
            if field not in tst or not isinstance(tst.get(field), str) or not tst[field].strip():
                errors.append(f"Missing or empty required field: {prefix}.{field}")

        tst_id = tst.get("id", "")
        if tst_id and not TEST_ID_PATTERN.match(tst_id):
            errors.append(
                f"Invalid test ID '{tst_id}' at {prefix}.id "
                f"— must match pattern TST-NNN"
            )
        if tst_id in seen_ids:
            errors.append(
                f"Duplicate test ID '{tst_id}' at {prefix} "
                f"and tests[{seen_ids[tst_id]}]"
            )
        else:
            seen_ids[tst_id] = i

        fp = tst.get("file_path", "")
        if fp in seen_paths:
            errors.append(
                f"Duplicate file_path '{fp}' at {prefix} "
                f"and tests[{seen_paths[fp]}]"
            )
        else:
            seen_paths[fp] = i

        cr = tst.get("controls_relevant")
        if not isinstance(cr, list) or len(cr) == 0:
            errors.append(f"'{prefix}.controls_relevant' must be a non-empty array")
        elif valid_control_ids is not None:
            for ref in cr:
                if ref not in valid_control_ids:
                    errors.append(
                        f"{prefix}.controls_relevant contains '{ref}' "
                        f"which is not a valid control ID"
                    )

    return errors


def run(control_library_path, artifact_index_path, test_catalog_path):
    """Validate all 3 input JSON files. Returns a ValidationResult dict."""
    log("INFO", "Starting validate_input.py")

    files_validated = []
    overall_pass = True

    file_specs = [
        ("control_library", control_library_path),
        ("artifact_index", artifact_index_path),
        ("test_catalog", test_catalog_path),
    ]

    loaded = {}
    for name, path in file_specs:
        entry = {"file": name, "status": "pass", "errors": []}
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                loaded[name] = json.load(f)
        except FileNotFoundError:
            entry["status"] = "fail"
            entry["errors"].append(f"FILE_NOT_FOUND: {path}")
            log("ERROR", f"FILE_NOT_FOUND: {name} not found at {path}")
        except json.JSONDecodeError as e:
            entry["status"] = "fail"
            entry["errors"].append(f"PARSE_ERROR: {path} is not valid JSON — {e}")
            log("ERROR", f"PARSE_ERROR: {path} is not valid JSON — {e}")
        files_validated.append(entry)

    cl_entry = files_validated[0]
    ai_entry = files_validated[1]
    tc_entry = files_validated[2]

    valid_control_ids = None
    if "control_library" in loaded:
        errs = _validate_control_library(loaded["control_library"])
        if errs:
            cl_entry["status"] = "fail"
            cl_entry["errors"].extend(errs)
            for e in errs:
                log("ERROR", f"SCHEMA_ERROR: control_library — {e}")
        else:
            valid_control_ids = {
                c["id"] for c in loaded["control_library"]["controls"]
            }

    if "artifact_index" in loaded:
        errs = _validate_artifact_index(loaded["artifact_index"])
        if errs:
            ai_entry["status"] = "fail"
            ai_entry["errors"].extend(errs)
            for e in errs:
                log("ERROR", f"VALIDATION_ERROR: artifact_index — {e}")

    if "test_catalog" in loaded:
        errs = _validate_test_catalog(loaded["test_catalog"], valid_control_ids)
        if errs:
            tc_entry["status"] = "fail"
            tc_entry["errors"].extend(errs)
            for e in errs:
                log("ERROR", f"VALIDATION_ERROR: test_catalog — {e}")

    for entry in files_validated:
        if entry["status"] == "fail":
            overall_pass = False

    result = {
        "status": "pass" if overall_pass else "fail",
        "files_validated": files_validated,
    }

    log("INFO", f"Completed — status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Validate RCSA input JSON files")
    parser.add_argument("--control-library", required=True, help="Path to control library JSON")
    parser.add_argument("--artifact-index", required=True, help="Path to artifact index JSON")
    parser.add_argument("--test-catalog", required=True, help="Path to test catalog JSON")
    args = parser.parse_args()

    result = run(args.control_library, args.artifact_index, args.test_catalog)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
