from app.utils import convert_letter_to_value


class Recommender:
    def __init__(self):
        """
        Initializes the Recommender class.

        Attributes:
        - programs (list): List of programs available for recommendation.
        - tags (list): List of all possible tags (attributes).
        - program_attributes (list): List of program-tag relationships with relevancy scores.
        - user_preferences (list): List of user preferences mapping tag_id to preference score.
        """
        self.programs = []  # List of programs available for recommendation
        self.tags = []  # List of all possible tags (attributes)
        self.program_attributes = []  # List of program-tag relationships with relevancy scores
        self.user_preferences = []  # List of user preferences mapping tag_id to preference score
        self.user_data = []  # List of user qualifications

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

    def set_tags(self, tags):
        """
        Sets the list of available tags (attributes).

        **Needs:**
        - tags (list): A list of dictionaries, where each dictionary represents a tag.
          Example:
          [
              {"id": int, "name": str},
              ...
          ]

        **Returns:**
        - None
        """
        self.tags = tags

    def set_program_attributes(self, program_attributes):
        """
        Sets the list of program attributes that define how relevant each tag is to a program.

        **Needs:**
        - program_attributes (list): A list of dictionaries, where each dictionary represents a program-tag relationship.
          Example:
          [
              {"id": int, "program_id": int, "tag_id": int, "relevancy_score": int},
              ...
          ]

        **Returns:**
        - None
        """
        self.program_attributes = program_attributes

    def set_user_preferences(self, user_preferences):
        """
        Sets the user's preference scores for different tags.

        **Needs:**
        - user_preferences (list): A list of dictionaries, where each dictionary represents a user's preference for a tag.
          Example:
          [
              {"tag_id": int, "preference_score": int},
              ...
          ]

        **Returns:**
        - None
        """
        self.user_preferences = user_preferences

    def set_user_data(self, user_qualifications):
        """
        Sets the user's qualifications.

        **Needs:**
        - user_qualifications (dict): A dictionary representing a user's qualifications.
          Example:
          {
              "id": int,
              "full_name": str or None,
              "spm_qualification": list or None,  # List of SPM subjects with grades
              "stpm_qualification": list or None,  # List of STPM subjects with grades
              "matriculation_qualification": list or None,  # List of matriculation subjects with grades
              "diploma_qualification": dict or None,  # Diploma details
              "user_id": int
          }

          Example of `spm_qualification`:
          [
              {
                  "subject_id": str,
                  "subject_name": str,
                  "grade": str
              },
              ...
          ]

          Example of `diploma_qualification`:
          {
              "diploma_institute": str,
              "diploma_name": str,
              "nec_category": str or None,
              "cgpa": str
          }

        **Returns:**
        - None
        """
        self.user_qualifications = user_qualifications

    def filter_programs_on_qualifications(self):
        qualified_programmes = []

        if not self.programs:
            raise ValueError("No programs available for filtering.")

        print("Starting program qualification filtering...")

        for program in self.programs:
            print(f"\nProcessing program: {program.get('name', 'Unknown Program')} (ID: {program.get('id')})")
            pass_SPM = False
            pass_diploma = False
            pass_matriculation = False

            # SPM Qualification
            user_spm_qualification = self.user_qualifications.get("spm_qualification", [])
            program_spm_qualification = program.get("entry_requirement", {}).get("spm")

            if user_spm_qualification and program_spm_qualification:
                pass_general_requirements = False
                pass_programme_requirements = False

                programme_general_requirements = program_spm_qualification.get("general_requirements", [])
                if isPassSpmGeneralRequirements(user_spm_qualification, programme_general_requirements):
                    pass_general_requirements = True
                    print("- Passed general SPM requirements.")

                programme_requirements = program_spm_qualification.get("programme_requirements", [])
                if isPassSpmProgrammeRequirements(user_spm_qualification, programme_requirements):
                    pass_programme_requirements = True
                    print("- Passed program-specific SPM requirements.")

                if pass_general_requirements and pass_programme_requirements:
                    pass_SPM = True
                    print("✔ SPM qualification passed.")
                else:
                    print("✘ SPM qualification failed.")

            # Matriculation check placeholder
            # TODO: Add logic here in the future

            # Diploma Qualification
            user_diploma_qualification = self.user_qualifications.get("diploma_qualification")
            program_diploma_qualification = program.get("entry_requirement", {}).get("diploma")

            if user_diploma_qualification and program_diploma_qualification:
                isAboveCGPA = float(user_diploma_qualification.get("cgpa", 0)) >= float(program_diploma_qualification.get("cgpa", 0))
                isInNEC = user_diploma_qualification.get("nec_category") in program_diploma_qualification.get("NEC", [])

                if isAboveCGPA and isInNEC:
                    pass_diploma = True
                    print("✔ Diploma qualification passed.")

            if pass_SPM and (pass_diploma or pass_matriculation):
                qualified_programmes.append(program)
                print(f"✅ Program '{program.get('name', 'Unknown Program')}' qualified.")

        print(f"\nTotal qualified programs: {len(qualified_programmes)}")
        return qualified_programmes

    def calculate_recommendations(self, programs=None):
        """
        Calculates program recommendations based on user preferences and program attributes.

        **Needs:**
        - No direct input. Uses the attributes:
          - self.programs
          - self.program_attributes
          - self.user_preferences

        **Returns:**
        - program_scores (dict): A dictionary mapping program IDs to their calculated relevance scores.
          Example:
          {
              program_id: score,
              ...
          }
        """

        try:
            program_scores = {program["id"]: 0 for program in programs}

            for preference in self.user_preferences:
                tag_id = preference["tag_id"]

                for program in self.program_attributes:
                    if program["tag_id"] == tag_id:
                        program_id = program["program_id"]
                        # print(f"Program ID: {program_id}, Tag ID: {tag_id}, Relevancy Score: {program['relevancy_score']}, User Preference Score: {preference['preference_score']}")
                        program_scores[program_id] = program_scores[program_id] + (preference["preference_score"] * program["relevancy_score"])

            return program_scores
        except Exception as e:
            print(f"An error occurred while calculating recommendations: {e}")
            return None

    def process_recommendations(self):
        """
        Processes the recommendations and returns the top 5 recommended programs.

        **Needs:**
        - No direct input. Uses the output of `calculate_recommendations()`.

        **Returns:**
        - sorted_programs (list): A list of tuples containing the top 5 program IDs and their scores, sorted by relevance.
          Example:
          [
              (program_id, score),
              ...
          ]
        """
        # Filter programmes based on qualifications
        qualified_programs = self.filter_programs_on_qualifications()

        if len(qualified_programs) == 0:
            print("No programs qualified based on user qualifications.")
            return []
        
        # Calculate the program scores based on user preferences
        program_scores = self.calculate_recommendations(qualified_programs)
        print(f"Program scores: {program_scores}")

        # Sort the programs by their scores in descending order and get the top 5
        sorted_programs = sorted(program_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        return sorted_programs

# Helper functions
def isUserPassSubject(user_spm_qualification, required_subject):
    # A user passes the subject if:
    # 1. User has the required subject
    # 2. User has the required grade for the subject

    required_subject_id = required_subject["id"]
    required_subject_grade = required_subject["grade"]
    required_subject_grade_value = convert_letter_to_value(required_subject_grade)

    if required_subject_id is None:
        raise ValueError("required_subject_id is None.")

    user_grade = next((item for item in user_spm_qualification if item["subject_id"] == required_subject_id), None)
    if user_grade is None:
        # User does not have the required subject
        return False

    user_grade_value = convert_letter_to_value(user_grade["grade"])
    if user_grade_value is None:
        raise ValueError("user_grade_value is None.")

    if user_grade_value < required_subject_grade_value:
        # User has not met the required grade for the subject
        return False
    
    return True


def isPassSpmGeneralRequirements(user_spm_qualification, programme_general_requirements):
    print("Checking general SPM requirements...")
    # It is assumed that the user passed, unless proven otherwise
    # If checks fail, return False early
    # A user passes the requirements if:
    # 1. User has the required subject
    # 2. User has the required grade for the subject
    # 3. User has all the required subjects
    # 3a. If one of the required subjects is not in the user's qualification, then the user does not pass the requirements

    for required_subject in programme_general_requirements:
        try:
            if not isUserPassSubject(user_spm_qualification, required_subject):
                # User does not pass this subject
                return False
        except KeyError as e:
            print(f"[KeyError] Missing key in subject {required_subject}: {e}")
            return False
        except ValueError as e:
            print(f"[ValueError] Invalid data in subject {required_subject}: {e}")
            return False
        except Exception as e:
            print(f"[Unexpected Error] while checking subject {required_subject}: {e}")
            return False

    print("  ✔ Passed all general SPM subject requirements.")
    return True


def isPassSpmProgrammeRequirements(user_spm_qualification, programme_requirements):
    print("Checking program-specific SPM requirements...")
    # It is assumed that the user DID NOT pass, unless proven otherwise
    # If checks fail, return False early

    # Programme requirements are divided into multiple groups, in which each group contains one or more subjects
    # A user passes the requirements if:
    # 1. A user passes the requirements of at least one of the groups
    # 2. A user passes the requirements of a group if:
    # 2a. User has all required subjects with required grades

    for path_index, path in enumerate(programme_requirements):
        isPassPathRequirements = True

        for path_subject in path:
            try:
                if not isUserPassSubject(user_spm_qualification, path_subject):
                    # User does not pass this subject
                    isPassPathRequirements = False
                    break
            except KeyError as e:
                print(f"[KeyError] Missing key in subject {path_subject}: {e}")
                isPassPathRequirements = False
                break
            except ValueError as e:
                print(f"[ValueError] Error checking subject {path_subject.get('subject', 'Unknown Subject')}: {e}")
                isPassPathRequirements = False
                break
            except Exception as e:
                print(f"[Unexpected Error] while checking subject {path_subject}: {e}")
                isPassPathRequirements = False
                break

        if isPassPathRequirements:
            # User has passed the requirements of this group
            print(f"  ✔ Passed one group of program-specific SPM requirements (Path {path_index + 1}).")
            return True

    return False