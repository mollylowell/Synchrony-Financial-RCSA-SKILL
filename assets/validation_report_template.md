---
title: "Validation Report"
generated: "{{generated}}"
total_citations: {{total_citations}}
valid_citations: {{valid_citations}}
invalid_citations: {{invalid_citations}}
resolution_rate: "{{resolution_rate}}"
---

# Validation Report

## Citation Index

| Citation | File Path | Lines | Status |
|---|---|---|---|
{{#each citations}}
| [{{file_path}} — {{description}}] | `{{file_path}}` | {{lines}} | {{status}} |
{{/each}}

---

## Evidence Coverage

| Control | Expected Types | Matched | Unmatched | Coverage % |
|---|---|---|---|---|
{{#each controls}}
| {{control_name}} ({{control_id}}) | {{expected_count}} | {{matched_count}} | {{unmatched_count}} | {{coverage_pct}} |
{{/each}}

---

## Flagged for Human Review

{{#if has_flags}}
{{#each flags}}
- **{{flag_type}}**: {{flag_description}}
{{/each}}
{{else}}
No items flagged. All citations resolved and all expected evidence types matched.
{{/if}}
