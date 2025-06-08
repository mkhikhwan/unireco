from django.db.models import Prefetch
from app.models import (
    Programme, UserPreference, UserData, EntryRequirement, DegreeField, Tag, TagDegreeField
)
from app.utils import convert_letter_to_value
import math
from typing import List, Tuple

class Recommender:
    def __init__(self, user):
        """
        Initializes the recommender for a given user.
        """
        self.user = user
        self.user_data = UserData.objects.filter(user=user).first()
        self.preferences = self.get_user_preferences()

    def set_programs(self, programs):
        """
        Sets the list of available programs along with their entry requirements.

        Parameters
        ----------
        programs : list
            A list of dictionaries, where each dictionary represents a program.

            Example:
            [
                {
                    "id": int,
                    "name": str,
                    "entry_requirement": dict
                },
                ...
            ]

            entry_requirement : dict
                Entry requirements for the program.

                Structure:
                {
                    "id": int,
                    "program_id": int,

                    "diploma": dict or None
                        {
                            "cgpa": float,
                            "NEC": list of str  # NEC codes representing accepted diploma fields
                        },

                    "matriculation": dict or None
                        {
                            "cgpa": float
                        },

                    "spm_requirements": dict or None
                        {
                            "general_requirements": list
                                A list of compulsory SPM subjects.
                                Example:
                                [
                                    {
                                        "id": int,
                                        "subject": str,
                                        "grade": str
                                    },
                                    ...
                                ],

                            "programme_requirements": list of list
                                A list of requirement groups where each inner list represents an OR condition.
                                Example:
                                [
                                    [
                                        {"id": int, "subject": str, "grade": str}
                                    ],
                                    [
                                        {"id": int, "subject": str, "grade": str},
                                        {"id": int, "subject": str, "grade": str}
                                    ]
                                ]
                        }
                }

        Returns
        -------
        None
        """
        self.programs = programs

    def get_user_preferences(self):
        """
        Fetch user preferences as a dictionary: { tag_id: preference_score }
        """
        preferences = UserPreference.objects.filter(user=self.user)
        return {pref.tag_id: pref.preference_score for pref in preferences}
    
    def get_tags_for_subfield(self, degree_field):
        """
        Returns a dictionary of tags and their relevancy scores for a given subfield (DegreeField).
        
        Args:
            degree_field (DegreeField): The subfield to fetch tags for.
        
        Returns:
            dict: { tag_id: relevancy_score }
        """
        tag_links = TagDegreeField.objects.filter(degree_field=degree_field).select_related("tag")
        return {tag_link.tag_id: tag_link.relevancy_score for tag_link in tag_links}
    
    def calculate_compatibility_score(self, degree_field)-> float:
        tag_weights = self.get_tags_for_subfield(degree_field)  # {tag_id: relevancy_score}
        user_preferences = self.get_user_preferences()          # {tag_id: preference_score}

        score = 0
        riasec_values = []
        riasec_score = 0
        riasec_maximum_farthest = 9.80
        max_possible = 0  # To normalize score later

        for tag_id, tag_weight in tag_weights.items():
            user_score = user_preferences.get(tag_id)

            if tag_id in {1, 2, 3, 4, 5, 6}:
                # Get RIASEC values
                temp = (user_score - tag_weight) ** 2
                riasec_values.append(temp)
            else:
                # For non-RIASEC tags, use existing method (user preference * weight)
                score += tag_weight * user_score
                max_possible += tag_weight

        # Calculate RIASEC score
        if(len(riasec_values) == 6):
            eucSum = sum(riasec_values)
            euclidean_distance = math.sqrt(eucSum)
            riasec_score = 1 - euclidean_distance / riasec_maximum_farthest

            # final score
            score += riasec_score
            max_possible += 1
            final_score = score / max_possible
            return final_score

        return 0
        
    def get_all_subfield_scores(self) -> List[Tuple[Programme, float]]:
        """
        Calculates compatibility scores for all DegreeField subfields
        and returns them sorted from most to least compatible.

        Returns:
            List of tuples: [(degree_field, score), ...]
        """
        subfields = DegreeField.objects.all()
        scored_fields = []

        for subfield in subfields:
            score = self.calculate_compatibility_score(subfield)
            scored_fields.append((subfield, score))

        # Sort by score descending (most compatible first)
        scored_fields.sort(key=lambda x: x[1], reverse=True)

        return scored_fields[:3]

    def isProgramQualified(self, program):
        # Get Programme Entry Requirements
        entry_req = program.entry_requirement
        if not entry_req:
            return False

        program_diploma_data = entry_req.diploma or {}
        program_stpm_data = entry_req.stpm or {}
        program_matriculation_data = entry_req.matriculation or {}

        # Get User's Academic Data
        user_data = self.user_data
        user_diploma = self.user_data.diploma_qualification or None
        user_matriculation = self.user_data.matriculation_qualification or None
        user_stpm = self.user_data.stpm_qualification or None

        # Diploma Path
        if user_diploma:
            print(f"\n🔎 START CHECK: Diploma Path for User: {self.user}, Program ID: {program.id}")
            passRequirements = evaluate(user_data, program_diploma_data)
            status = "✅ PASSED" if passRequirements else "❌ FAILED"
            print(f"🔚 END CHECK: Diploma Path for User: {self.user}, Program ID: {program.id} → {status}\n")
            return passRequirements
        elif user_matriculation:
            print(f"\n🔎 START CHECK: Matriculation Path for User: {self.user}, Program ID: {program.id}")
            passRequirements = evaluate(user_data, program_matriculation_data)
            status = "✅ PASSED" if passRequirements else "❌ FAILED"
            print(f"🔚 END CHECK: Matriculation Path for User: {self.user}, Program ID: {program.id} → {status}\n")
            return passRequirements
        elif user_stpm:
            print(f"\n🔎 START CHECK: STPM Path for User: {self.user}, Program ID: {program.id}")
            passRequirements = evaluate(user_data, program_stpm_data)
            status = "✅ PASSED" if passRequirements else "❌ FAILED"
            print(f"🔚 END CHECK: STPM Path for User: {self.user}, Program ID: {program.id} → {status}\n")
            return passRequirements
        
        return False

def evaluate(user_data, condition, depth=0)-> bool:
    indent = "    " * depth  # 4 spaces per level

    if "atleast" in condition:
        atleast = condition["atleast"]
        qualification = atleast["qualification"].lower()
        required_subjects = atleast["subjects"]
        count = atleast["count"]
        min_grade = convert_letter_to_value(atleast["grade"])

        if qualification == "spm":
            spm_results = user_data.spm_qualification
            spm_grades = {s["id"]: s["grade"] for s in spm_results}
            return check_subject_grade_requirement(
                spm_grades, required_subjects, min_grade, count, indent, "spm")

        if qualification == "matriculation":
            matriculation_results = user_data.matriculation_qualification.get("subjects")
            matriculation_grades = {m["id"]: m["grade"] for m in matriculation_results}
            return check_subject_grade_requirement(
                matriculation_grades, required_subjects, min_grade, count, indent, "matriculation")

        if qualification == "stpm":
            stpm_results = user_data.stpm_qualification.get("subjects")
            stpm_grades = {s["id"]: s["grade"] for s in stpm_results}
            return check_subject_grade_requirement(
                stpm_grades, required_subjects, min_grade, count, indent, "stpm")

    elif "abovecgpa" in condition:
        cgpa_rule = condition["abovecgpa"]
        qualification = cgpa_rule["qualification"].lower()
        cgpa_value = cgpa_rule["value"]

        # Map qualification to the appropriate user_data field
        qualification_map = {
            "diploma": user_data.diploma_qualification,
            "matriculation": user_data.matriculation_qualification,
            "stpm": user_data.stpm_qualification,
        }

        user_qualification = qualification_map.get(qualification)

        if user_qualification:
            user_cgpa = float(user_qualification.get("cgpa"))
            if user_cgpa >= cgpa_value:
                print(f"{indent}✅ {qualification.title()}: CGPA {user_cgpa} meets the requirement of {cgpa_value}.")
                return True
            else:
                print(f"{indent}❌ {qualification.title()}: CGPA {user_cgpa} does not meet the requirement of {cgpa_value}.")
                return False
        else:
            print(f"{indent}❌ {qualification.title()}: Qualification data not found.")
            return False

    elif "nec_in" in condition:
        nec_rule = condition["nec_in"]
        qualification = nec_rule["qualification"].lower()
        if qualification == "diploma":
            diploma_qualification = user_data.diploma_qualification
            nec_category = diploma_qualification.get("nec_category")

            if nec_category in nec_rule["nec_codes"]:
                print(f"{indent}✅ Diploma: NEC Category {nec_category} is valid.")
                return True
            else:
                print(f"{indent}❌ Diploma: NEC Category {nec_category} is not in the valid codes {nec_rule['nec_codes']}.")
                return False

    elif "AND" in condition:
        print(f"{indent}Evaluating AND condition...")
        result = all(evaluate(user_data, sub_condition, depth + 1) for sub_condition in condition["AND"])
        print(f"{indent}AND evaluation result: {result}")
        return result

    elif "OR" in condition:
        print(f"{indent}Evaluating OR condition...")
        result = any(evaluate(user_data, sub_condition, depth + 1) for sub_condition in condition["OR"])
        print(f"{indent}OR evaluation result: {result}")
        return result

    return False

# Helper functions
def check_subject_grade_requirement(
    user_grades: dict,
    required_subjects: list,
    min_grade: float,
    count: int,
    indent: str,
    qualification_label: str
) -> bool:
    grade_count = 0
    missing_or_failed = []

    for subject_id_str in required_subjects:
        subject_id = int(subject_id_str)
        raw_grade = user_grades.get(subject_id)
        user_grade = convert_letter_to_value(raw_grade)

        if raw_grade is None:
            missing_or_failed.append(f"Subject ID {subject_id}: Not found")
        elif user_grade < min_grade:
            missing_or_failed.append(f"Subject ID {subject_id}: Grade {raw_grade} too low")

        if user_grade is not None and user_grade >= min_grade:
            grade_count += 1

    passed = grade_count >= count
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{indent}{status} - {qualification_label.upper()}: {grade_count}/{count} required subjects met the minimum grade")

    if not passed:
        for reason in missing_or_failed:
            print(f"{indent} --> {reason}")

    return passed
