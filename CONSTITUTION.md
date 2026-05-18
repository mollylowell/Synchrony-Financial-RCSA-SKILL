# Project Constitution: Synchrony Documentation Automation Skillset

**Owners**:  Molly Lowell , Whitney Robinson , Sheila Green  

---

## 1. Core Principles

### Principle 1: Accuracy Over Speed
We prioritize correctness and traceability over fast output. Every generated document must include citations, confidence scores, and explicit gap flags. The system must never imply compliance without proof.

### Principle 2: Graceful Degradation
If the LLM goes offline, our scripts can still extract raw data, schema facts, and test results. We lose the narrative but keep the data — which is better than total failure in an audit context. In degraded mode, the team can manually write short narratives using the extracted data as input.

### Principle 3: Simplicity First
We keep the system file-based and script-driven. No microservices, no cloud deployment, no frontend UI. Claude is the interface. We prove core functionality works before adding complexity.

### Principle 4: Audit-Ready by Default
Every output is designed to be reviewed by an auditor or compliance team. Reports include QA checks, validation reports, and flagged items — not just generated text.

---

## 2. Tech Stack & Platform Rules

### LLM / Agent Framework
- **Minimal case (demo day promise):** Claude Agent Skills (SKILL.md + scripts + assets)
- **Ideal case (documented, not promised):** Support for all mainstream agent frameworks — Codex, Gemini CLI, Google, Antigravity, Copilot/Cursor
- **Rationale:** Claude is the easiest way to deploy an agent skill and is the most universal. The ideal case may be included in documentation as a future extension.

### Tooling Language
- **Minimal case:** Python
- **Ideal case (documented, not promised):** MPCs and APIs
- **Rationale:** The team is most familiar with Python, and it handles file parsing, validation, and structured output generation well.

### Data Storage
- File-based, with outputs saved as structured Markdown (and optional DOCX)
- No expensive database hosting
- Keeps the system simple and aligned with the goal of generating documentation

### API Cost & Risk
- Since prompts and files are file-based, we are not paying for expensive database hosting.
- We use Claude for the demo, but the system is designed to support multiple frameworks, so API risk is accepted short-term but not a long-term limitation.

### Third-Party Dependency Risk
- Since our agent skills are backed by code-based logic, if Claude goes offline, although we will lose the narrative and the descriptions that are LLM-powered, our scripts can still extract the raw data, schema facts, and test results.
- We would lose the narrative but keep the data, which is better than a total failure in an audit context.

### Team Debugging Capability
- If the AI narrative breaks, any team member can manually edit the Markdown templates or check the JSON input files (schemas, test catalogs) to ensure the data is correct even if the agent is struggling.
- The system is designed to not rely too heavily on complex coding by using AI-assisted development and structured workflows. While not everyone on the team is strong in Python, we are still able to troubleshoot issues by using prompt engineering, checking the JSON inputs, and reviewing the Markdown outputs. This allows us to work together to fix problems even if we are not making major changes to the underlying code.

---

## 3. Security, Privacy & Data Boundaries

### What Data Gets Sent to the LLM
- Only the prompt (task instructions), the specific file structure being analyzed, and the Markdown template are sent to Claude.
- We are only comfortable sending the metadata needed for the LLM to write the narratives.
- We do NOT send the entire raw dataset or large codebases.

### What Gets Stored After a Run
- Our system does not store inputs permanently on Claude.
- Outputs are stored locally as generated Markdown documentation files.
- While Claude may temporarily store input data for security monitoring reasons, it would be for a short period of time and is not stored by our system.

### LLM Provider Training Policy
- No — Anthropic does not train on API inputs.
- They only train if you explicitly allow it, which we will NOT opt into.

### Logging & Access
- **What gets logged:** The system generates four primary reports (Data Dictionary, RCSA Control Narratives, Pipeline Documentation, Test Evidence Summaries) and two secondary logs (qa_report.md, validation_report.md).
- **Who has access:** During development, access is restricted to our team and our professor. Upon handoff in Week 7, access is transferred entirely to Synchrony's internal documentation and risk/compliance teams.
- **Sensitive information risk:** If a developer accidentally leaves a secret (like a password) in the code, and the AI cites that line of code in a Validation Report, that secret could appear in our logs. The fix: Never-Ever Rules and .gitignore.

### Never-Ever Rules
- Never send raw PII to the LLM
- Never send API keys or credentials
- Never send full source code or raw datasets
- Never commit secrets to the repo
- Never opt into LLM provider training on our data

---

## 4. Out of Scope

### Features Not Included in Demo

| What's Out | Why | Future Status |
|---|---|---|
| Full documentation generation for all artifact types | We are only promising data dictionary generation and RCSA-style control narratives | Pipeline documentation and test evidence summaries are documented as future extensions |
| Automatic repository scanning (full repository ingestion) | Scanning a whole repository is hard — many languages, thousands of files, potential sensitive information | Immediate next steps after demo |
| Documentation for multiple different use cases | We are only showing our demo for our selected public dataset on Kaggle | Documentation phase (next priority) |
| Deployment features | Demo day focuses on demonstrating the documentation generation workflows | Immediate next steps after demo |

### Technical Approaches Intentionally Not Used

| Approach | Why Not |
|---|---|
| Microservices | Unnecessary complexity for a 6-week prototype |
| Cloud deployment | Not needed for demo; future extension |
| Frontend UI | Claude itself is the interface — proves core functionality without added complexity |
| Standalone API | Not needed for demo; future extension |
| Real-time processing | Not applicable to batch documentation generation |
| Agent harness libraries | Kept the system simple with file-based workflow |

As a next step, this system could be expanded into a full user interface, such as a web application or dashboard, to make it more accessible for non-technical users. However, given the time constraints of this project, using Claude as the interface allows us to stay focused on producing accurate, audit-ready documentation.

### Handoff Boundary — Where Our Project Ends

Synchrony's responsibility begins when adapting this prototype for real-world use. This includes:
- Integrating the system with their internal data sources
- Ensuring compliance with their security and data governance policies
- Handling sensitive data appropriately
- Modifying the system to fit their specific data formats and infrastructure

We are NOT responsible for:
- Production deployment
- Integration with internal systems
- Enforcing enterprise security requirements
- Guaranteeing compatibility with all of Synchrony's existing data and workflows

Our goal is to provide a proof of concept that demonstrates feasibility, which Synchrony can then extend and adapt within their environment.

---

## 5. Governance

### Decision-Making
- We will be respectful of one another and will hear everyone's opinion out.
- If there is a disagreement that we cannot come to an agreement on, the majority vote will rule while also being very willing to compromise.
- If we cannot come up with a solution or do not know the best path, we will ask our professor for advice on technical questions.

### Spec & Constitution Changes
- The whole team needs to agree in order to change the spec or constitution.
- We will run proposed changes by our professor to ensure they are feasible.
- If a new feature is proposed, it must be discussed as a team and evaluated based on scope, timeline, and alignment with the constitution.
- Only approved changes are added, and all updates are documented so the team stays aligned.

### Definition of Done
A task is "done" when:
1. All team members have reviewed the work together
2. It has been run to ensure consistency and accuracy
3. It passes the evaluation rubric
4. Every person in the group signs off that they are confident the task is complete

### Accountability
- Speak within the group first and make sure everyone clearly understands their role and what they need to accomplish in the timeframe.
- If someone isn't pulling their weight, make sure they understand what they are supposed to be doing and work as a team to resolve it.

---

*This is a living document. Every time the AI misbehaves in a predictable way, that's feedback for a Constitution update. The PM owns this document, but the whole team enforces it.*
