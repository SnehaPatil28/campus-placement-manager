# AI Usage & Development Attribution

## 1. Overview
This document tracks the usage of AI assistance (Antigravity Senior Software Engineer & Solution Architect) during the development of the **College Placement Manager** for the Thinqloud assessment.

---

## 2. Prompts & Architectural Iterations

### Architectural Planning Prompt
> *"Act as my Senior Software Engineer & Solution Architect. Design a College Placement Manager system emphasizing business workflow understanding over raw code generation."*

### Key Concepts Structured by AI
- **Eligibility Engine Architecture**: Formulated clean backend rule evaluation returning boolean status + explicit breakdown of failure reasons.
- **Application State Machine**: Enforced rigid state transitions (`APPLIED` -> `SHORTLISTED` -> `INTERVIEW` -> `PASSED` -> `SELECTED` -> `OFFERED`).
- **Database Schema**: Normalization of entities (`users`, `students`, `recruiters`, `companies`, `placement_drives`, `applications`, `interviews`, `offers`, `skills`).

---

## 3. Human Modifications & Engineering Decisions
- **Backend Validation Strictness**: Ensured frontend checks were duplicated on the backend server to prevent client-side bypass.
- **Data Isolation**: Added company scoping checks for Recruiter endpoints (`recruiter.company_id == drive.company_id`).
- **Simplified Technology Choices**: Kept stack lean (React, FastAPI, SQLite) without unnecessary microservices or heavy message brokers.
