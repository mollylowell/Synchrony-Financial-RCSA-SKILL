---
title: "RCSA Control Narratives"
generated: "{{generated}}"
skill_version: "{{skill_version}}"
total_controls: {{total_controls}}
overall_confidence: "{{overall_confidence}}"
---

# RCSA Control Narratives

## Summary

| Control | Confidence Tier | Evidence Found | Gaps Identified |
|---|---|---|---|
{{#each controls}}
| {{control_name}} ({{control_id}}) | {{confidence_tier}} | {{evidence_found}} | {{gaps_identified}} |
{{/each}}

---

{{#each controls}}
## {{control_name}} ({{control_id}})

**Objective**: {{control_objective}}

**Confidence**: {{confidence_tier}}

### Narrative

{{narrative_text}}

{{#if has_gaps}}
### Gaps

{{#each gaps}}
> ⚠️ **GAP**: {{evidence_type_label}} (`{{evidence_type_id}}`) — no matching evidence found
{{/each}}
{{/if}}

### Evidence

{{#each matched_evidence}}
- {{description}} [{{file_path}} — {{evidence_label}}]
{{/each}}

---

{{/each}}
