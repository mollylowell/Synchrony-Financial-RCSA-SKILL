# Citation Format Specification

**Feature**: F4 — Templates, Sample Data, and Control Library
**Last updated**: 2026-04-12
**Status**: Locked — F5 and F6 must conform to this spec

---

## Citation Syntax

Inline citations use bracket notation with the file path and a human-readable description:

```
[file_path — description]
```

### Rules

- **File path**: Relative path to the evidence artifact (must not start with `/`)
- **Separator**: ` — ` (space, em dash, space)
- **Description**: Brief human-readable label explaining what the artifact provides as evidence
- Citations appear inline within per-control narrative text
- Each citation must resolve to a real file in the artifact index

### Examples

```markdown
Authentication is enforced via OAuth 2.0 configuration
[auth/oauth_config.yaml — OAuth 2.0 authentication configuration] with
role-based access defined in [auth/rbac_roles.yaml — RBAC role definitions].
```

```markdown
Change management is supported by the deployment rollback procedure
[deploy/rollback.md — Rollback procedure documentation] and version-controlled
release scripts [deploy/release.sh — Automated release script].
```

```markdown
Data quality validation relies on input schema enforcement
[validation/input_schema.json — Input validation schema]. No matching artifact
was found for data transformation testing.
```

---

## Multi-File Evidence

When a single evidence claim spans multiple files, use separate citations for each file:

```markdown
Incident detection is supported by alert configuration
[monitoring/alert_rules.yaml — Alert rule definitions] and escalation
procedures [monitoring/escalation_policy.json — Escalation policy].
```

Each citation is independent — no grouping syntax required.

---

## Citation Resolution

Every citation in the narratives document must resolve to an entry in the **Citation Index** table within `validation_report.md`:

| Citation | File Path | Status |
|---|---|---|
| `[auth/oauth_config.yaml — OAuth 2.0 authentication configuration]` | `auth/oauth_config.yaml` | ✅ Valid |
| `[auth/rbac_roles.yaml — RBAC role definitions]` | `auth/rbac_roles.yaml` | ✅ Valid |
| `[deploy/rollback.md — Rollback procedure documentation]` | `deploy/rollback.md` | ❌ Invalid — file not found |

- **Valid**: File path exists in the artifact index
- **Invalid**: File path does not resolve — flagged for human review

---

## Validation Rules

1. Every citation in the narratives must appear in the Citation Index
2. Every citation file path must be relative (no absolute paths)
3. The description portion is informational — validation checks the file path only
4. F6's citation validator extracts the file path from each citation and checks it against the artifact index

---

## Cross-References

- Template structures using this format: `templates/rcsa_control_narratives_template.md`
- Validation report resolving citations: `templates/validation_report_template.md`
- F5 SKILL.md produces citations in this format
- F6 scripts validate citations against this spec
