from typing import Tuple, List
from app.models.student import Student


def calculate_profile_completeness(student: Student) -> Tuple[int, bool, List[str]]:
    """Calculates student profile completeness percentage (0-100%), completeness boolean flag,

    and returns a list of missing profile fields.

    Criteria evaluated (6 items):
    1. full_name
    2. branch
    3. graduation_year
    4. cgpa
    5. backlogs
    6. skills (at least 1 skill tag)
    """
    missing_fields = []
    fulfilled_count = 0

    if student.full_name and student.full_name.strip():
        fulfilled_count += 1
    else:
        missing_fields.append("full_name")

    if student.branch and student.branch.strip():
        fulfilled_count += 1
    else:
        missing_fields.append("branch")

    if student.graduation_year is not None:
        fulfilled_count += 1
    else:
        missing_fields.append("graduation_year")

    if student.cgpa is not None:
        fulfilled_count += 1
    else:
        missing_fields.append("cgpa")

    if student.backlogs is not None:
        fulfilled_count += 1
    else:
        missing_fields.append("backlogs")

    if student.skills and len(student.skills) >= 1:
        fulfilled_count += 1
    else:
        missing_fields.append("skills")

    total_criteria = 6
    completeness_percentage = int((fulfilled_count / total_criteria) * 100)
    is_profile_complete = (len(missing_fields) == 0)

    return completeness_percentage, is_profile_complete, missing_fields
