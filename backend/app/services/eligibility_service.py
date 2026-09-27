from typing import Tuple, List
from app.models.student import Student
from app.models.drive import PlacementDrive
from app.services.drive_service import parse_csv_list


def evaluate_student_eligibility(student: Student, drive: PlacementDrive) -> Tuple[bool, List[str]]:
    """Evaluates student eligibility against placement drive criteria.

    Runs 5 backend business rules:
    1. CGPA Rule: student.cgpa >= drive.min_cgpa
    2. Backlogs Rule: student.backlogs <= drive.max_backlogs
    3. Graduation Year Rule: student.graduation_year == drive.graduation_year
    4. Allowed Branch Rule: student.branch in drive.allowed_branches
    5. Required Skills Rule: drive.required_skills subset of student.skills

    Returns:
    - is_eligible: bool (True if all 5 rules pass)
    - failure_reasons: List[str] (descriptive explanation of failing criteria)
    """
    reasons: List[str] = []

    # Rule 1: CGPA Rule
    if student.cgpa is None:
        reasons.append("Profile incomplete: CGPA is missing.")
    elif student.cgpa < drive.min_cgpa:
        reasons.append(f"Required CGPA: {drive.min_cgpa:.1f} | Your CGPA: {student.cgpa:.1f}")

    # Rule 2: Backlogs Rule
    if student.backlogs is None:
        reasons.append("Profile incomplete: Backlog count is missing.")
    elif student.backlogs > drive.max_backlogs:
        reasons.append(f"Maximum Allowed Backlogs: {drive.max_backlogs} | Your Backlogs: {student.backlogs}")

    # Rule 3: Graduation Year Rule
    if student.graduation_year is None:
        reasons.append("Profile incomplete: Graduation year is missing.")
    elif student.graduation_year != drive.graduation_year:
        reasons.append(f"Required Graduation Year: {drive.graduation_year} | Your Graduation Year: {student.graduation_year}")

    # Rule 4: Allowed Branch Rule
    allowed_branches = parse_csv_list(drive.allowed_branches)
    allowed_branches_upper = [b.upper() for b in allowed_branches]
    if not student.branch or not student.branch.strip():
        reasons.append("Profile incomplete: Academic branch is missing.")
    elif student.branch.strip().upper() not in allowed_branches_upper:
        reasons.append(f"Allowed Branches: {', '.join(allowed_branches)} | Your Branch: {student.branch}")

    # Rule 5: Required Skills Rule
    required_skills = parse_csv_list(drive.required_skills)
    student_skills_set = {s.skill_name.strip().upper() for s in student.skills} if student.skills else set()

    missing_skills = []
    for req_skill in required_skills:
        if req_skill.upper() not in student_skills_set:
            missing_skills.append(req_skill)

    if missing_skills:
        reasons.append(f"Missing Required Skills: {', '.join(missing_skills)}")

    is_eligible = (len(reasons) == 0)
    return is_eligible, reasons
