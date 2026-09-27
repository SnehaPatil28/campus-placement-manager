# System Test Cases & Evaluation Matrix

## 1. Test Scenarios Suite

| ID | Test Scenario | Steps | Expected Result | Pass/Fail Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Eligible student applies successfully | 1. Student with CGPA 8.2, AIML, 0 backlogs logs in.<br>2. Navigates to Drive requiring CGPA 7.5, AIML.<br>3. Clicks Apply. | Application created with status `APPLIED`. Success notification generated. | HTTP 201 Created |
| **TC-02** | Student fails CGPA requirement | 1. Student with CGPA 6.8 logs in.<br>2. Checks eligibility for Drive requiring CGPA 7.5. | Eligibility returns `is_eligible: false` with reason "Minimum CGPA 7.5 required, your CGPA is 6.8". Apply blocked. | HTTP 200 with `is_eligible: false` |
| **TC-03** | Student fails Branch requirement | 1. Civil branch student attempts to apply for CSE/IT drive. | Eligibility engine flags branch mismatch. Application blocked. | Reason: "Branch Civil not in [CSE, IT]" |
| **TC-04** | Student attempts duplicate application | 1. Student already applied to Drive X attempts POST `/applications` again for Drive X. | Backend rejects request with duplicate application error. | HTTP 400 Bad Request: "Application already submitted for this drive" |
| **TC-05** | Application attempt after deadline | 1. Student attempts to apply for drive where `deadline < current_timestamp`. | Backend rejects application with deadline expired message. | HTTP 400 Bad Request: "Drive deadline has expired" |
| **TC-06** | Recruiter shortlists applicant | 1. Recruiter views applicants for their drive.<br>2. Clicks Shortlist on Candidate A. | Candidate A status changes from `APPLIED` to `SHORTLISTED`. | Application status `SHORTLISTED` in DB |
| **TC-07** | Recruiter schedules interview | 1. Recruiter schedules interview round for shortlisted candidate. | Interview record created with status `PENDING`. Candidate application status updated to `INTERVIEW`. | Interview created with mode, date, link |
| **TC-08** | Student passes interview and is selected | 1. Recruiter marks interview result `PASSED`.<br>2. Transitions candidate status to `SELECTED`. | Candidate status updated to `SELECTED`. Candidate eligible for formal Offer. | DB application status `SELECTED` |
| **TC-09** | Candidate fails interview & cannot be selected | 1. Recruiter marks interview result `FAILED`.<br>2. Recruiter attempts to set application status to `SELECTED`. | Backend validation blocks selection transition. | HTTP 400 Bad Request: "Cannot select candidate with failed interview result" |
| **TC-10** | Role authorization enforcement | 1. Student attempts to POST to `/drives` or `/companies`. | Backend middleware rejects request. | HTTP 403 Forbidden: "Insufficient permissions" |
