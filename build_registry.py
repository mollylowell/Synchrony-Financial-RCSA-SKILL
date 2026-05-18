"""F6 Script 2: Build Artifact Registry.

Builds an in-memory artifact registry from the 3 validated JSON input files,
providing O(1) lookup dictionaries keyed by ID and a reverse file_path index
used by validate_citations.py to resolve LLM citations.
"""

import argparse
import json
import sys


SCRIPT_ID = "REGISTRY"


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


def run(control_library_path, artifact_index_path, test_catalog_path):
    """Build artifact registry from the 3 input files. Returns ArtifactRegistry dict."""
    log("INFO", "Starting build_registry.py")

    artifact_data = read_json_file(artifact_index_path)
    test_data = read_json_file(test_catalog_path)

    artifacts = {}
    tests = {}
    file_path_index = {}

    for art in artifact_data.get("artifacts", []):
        entry = {
            "id": art["id"],
            "file_path": art["file_path"],
            "file_type": art["file_type"],
            "description": art["description"],
            "source": "artifact_index",
        }
        artifacts[art["id"]] = entry
        file_path_index[art["file_path"]] = art["id"]

    for tst in test_data.get("tests", []):
        entry = {
            "id": tst["id"],
            "file_path": tst["file_path"],
            "file_type": tst["file_type"],
            "description": tst["description"],
            "controls_relevant": tst["controls_relevant"],
            "source": "test_catalog",
        }
        tests[tst["id"]] = entry
        file_path_index[tst["file_path"]] = tst["id"]

    total_artifacts = len(artifacts)
    total_tests = len(tests)

    result = {
        "status": "success",
        "registry": {
            "artifacts": artifacts,
            "tests": tests,
            "file_path_index": file_path_index,
            "stats": {
                "total_artifacts": total_artifacts,
                "total_tests": total_tests,
                "total_entries": total_artifacts + total_tests,
            },
        },
    }

    log("INFO", f"Registry built: {total_artifacts} artifacts, {total_tests} tests, "
        f"{total_artifacts + total_tests} file_path_index entries")
    log("INFO", f"Completed — status: {result['status']}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Build RCSA artifact registry")
    parser.add_argument("--control-library", required=True, help="Path to control library JSON")
    parser.add_argument("--artifact-index", required=True, help="Path to artifact index JSON")
    parser.add_argument("--test-catalog", required=True, help="Path to test catalog JSON")
    args = parser.parse_args()

    result = run(args.control_library, args.artifact_index, args.test_catalog)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
