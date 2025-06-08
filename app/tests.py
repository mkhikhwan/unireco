from django.test import TestCase
from app.services.recommender import Recommender
from app.models import CustomUser, DegreeField, Tag, UserData, UserPreference, TagDegreeField, Programme, EntryRequirement, University
from app.services.recommender import Recommender

class RecommenderTestCase(TestCase):
    def setUp(self):
        # Create User
        user = CustomUser.objects.create_user(email='test@example.com', password='password')
        self.user = user

        university = University.objects.create(name="ABC University")

        entry_requirement = EntryRequirement.objects.create(
            diploma={
                "AND": [
                    {
                        "abovecgpa": {
                            "value": 2.5,
                            "qualification": "diploma"
                        }
                    },
                    {
                        "nec_in": {
                            "nec_codes": ["05", "06", "07"],
                            "qualification": "diploma"
                        }
                    },
                    {
                        "AND": [
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "C",
                                    "subjects": ["4"],
                                    "qualification": "SPM"
                                }
                            },
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "E",
                                    "subjects": ["5"],
                                    "qualification": "SPM"
                                }
                            },
                            {
                                "OR": [
                                    {
                                        "atleast": {
                                            "count": 1,
                                            "grade": "B",
                                            "subjects": ["7"],
                                            "qualification": "SPM"
                                        }
                                    },
                                    {
                                        "AND": [
                                            {
                                                "atleast": {
                                                    "count": 1,
                                                    "grade": "C",
                                                    "subjects": ["1"],
                                                    "qualification": "SPM"
                                                }
                                            },
                                            {
                                                "atleast": {
                                                    "count": 1,
                                                    "grade": "C",
                                                    "subjects": ["8", "2"],
                                                    "qualification": "SPM"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            matriculation = {
                "AND": [
                    {
                        "abovecgpa": {
                            "value": 3.00,
                            "qualification": "matriculation"
                        }
                    },
                    {
                        "AND": [
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "B-",
                                    "subjects": ["1"],
                                    "qualification": "matriculation"
                                }
                            },
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "B-",
                                    "subjects": ["3", "4", "5", "6", "7", "8", "9"],
                                    "qualification": "matriculation"
                                }
                            }
                        ]
                    },
                    {
                        "AND": [
                            {
                                "atleast": {
                                    "count": 2,
                                    "grade": "B",
                                    "subjects": ["1", "7"],
                                    "qualification": "spm"
                                }
                            },
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "B",
                                    "subjects": ["8", "9", "10", "13", "12"],
                                    "qualification": "spm"
                                }
                            }
                        ]
                    }
                ]
            },
            stpm ={
                "AND": [
                    {
                        "abovecgpa": {
                            "value": 3.00,
                            "qualification": "stpm"
                        }
                    },
                    {
                        "atleast": {
                            "count": 1,
                            "grade": "B-",
                            "subjects": ["2"],
                            "qualification": "stpm"
                        }
                    },
                    {
                        "AND": [
                            {
                                "atleast": {
                                    "count": 1,
                                    "grade": "B-",
                                    "subjects": ["4", "3", "5", "6"],
                                    "qualification": "stpm"
                                }
                            },
                            {
                                "AND": [
                                    {
                                        "atleast": {
                                            "count": 1,
                                            "grade": "B",
                                            "subjects": ["7"],
                                            "qualification": "spm"
                                        }
                                    },
                                    {
                                        "atleast": {
                                            "count": 1,
                                            "grade": "B",
                                            "subjects": ["1", "8", "9", "10", "13"],
                                            "qualification": "spm"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        )

        # Create Program
        self.programme = Programme.objects.create(
            name="Bachelor in Computer Science (Data Engineering) with Honours",
            entry_requirement = entry_requirement,
            university = university
        )

    def test_diploma_program_qualify(self):
        # Create user qualifications as per the original setup
        UserData.objects.create(
            user=self.user,
            spm_qualification=[
                {"id": 1, "subject": "Matematik", "grade": "A"},
                {"id": 2, "subject": "Sains", "grade": "A"},
                {"id": 4, "subject": "Bahasa Melayu", "grade": "A"},
                {"id": 5, "subject": "Sejarah", "grade": "A"},
                {"id": 7, "subject": "Matematik Tambahan", "grade": "A"}
            ],
            diploma_qualification={
                "diploma_institute": "Politeknik Kuching",
                "diploma_name": "Diploma in Computer Science",
                "nec_category": "06",
                "cgpa": 4.00
            }
        )

        # Test if the user qualifies for the program
        recommender = Recommender(self.user)
        is_qualified = recommender.isProgramQualified(self.programme)
        
        self.assertTrue(is_qualified, "The program should be qualified based on the user's qualifications.")

    def test_diploma_program_does_not_qualify(self):
        # Modify the user qualifications to fail the test
        UserData.objects.create(
            user=self.user,
            spm_qualification=[
                {"id": 1, "subject": "Matematik", "grade": "A+"},
                {"id": 2, "subject": "Sains", "grade": "G"},
                {"id": 4, "subject": "Bahasa Melayu", "grade": "A+"},
                {"id": 5, "subject": "Sejarah", "grade": "A+"},
                {"id": 7, "subject": "Matematik Tambahan", "grade": "G"}
            ],
            diploma_qualification={
                "diploma_institute": "Politeknik Kuching",
                "diploma_name": "Diploma in Computer Science",
                "nec_category": "06",
                "cgpa": 3.60
            }
        )

        # Test if the user does not qualify for the program due to the failing subject
        recommender = Recommender(self.user)
        is_qualified = recommender.isProgramQualified(self.programme)
        
        self.assertFalse(is_qualified, "The program should not be qualified based on the user's insufficient qualifications.")

    def test_matriculation_program_qualify(self):
        UserData.objects.create(
            user=self.user,
            spm_qualification=[
                {"id": 1, "subject": "Matematik", "grade": "B"},
                {"id": 7, "subject": "Matematik Tambahan", "grade": "B"},
                {"id": 8, "subject": "Fizik", "grade": "B"},
                {"id": 5, "subject": "Sejarah", "grade": "A"},
                {"id": 4, "subject": "Bahasa Melayu", "grade": "A"}
            ],
            matriculation_qualification={
                "cgpa": "3.80",
                "subjects": [
                    {"id": 1, "subject": "Matematik", "grade": "A"},
                    {"id": 2, "subject": "Kimia", "grade": "A"},
                    {"id": 3, "subject": "Fizik", "grade": "A"},
                    {"id": 5, "subject": "Sains Komputer", "grade": "A"}
                ]
            }
        )

        recommender = Recommender(self.user)
        is_qualified = recommender.isProgramQualified(self.programme)

        self.assertTrue(is_qualified, "The program should be qualified based on the user's matriculation qualifications.")

    def test_stpm_program_qualify(self):
            UserData.objects.create(
                user=self.user,
                spm_qualification=[
                    {"id": 1, "subject": "Matematik", "grade": "A"},
                    {"id": 7, "subject": "Matematik Tambahan", "grade": "A"},
                    {"id": 8, "subject": "Fizik", "grade": "A"},
                    {"id": 5, "subject": "Sejarah", "grade": "A"},
                    {"id": 4, "subject": "Bahasa Melayu", "grade": "A"}
                ],
                stpm_qualification={
                    "cgpa": "4.00",
                    "subjects": [
                        {"id": 1, "subject": "Matematik M", "grade": "A+"},
                        {"id": 2, "subject": "Matematik T", "grade": "A+"},
                        {"id": 3, "subject": "Teknologi Komunikasi dan Informasi", "grade": "A+"},
                        {"id": 4, "subject": "Fizik", "grade": "A+"}
                    ]
                }
            )

            recommender = Recommender(self.user)
            is_qualified = recommender.isProgramQualified(self.programme)

            self.assertTrue(is_qualified, "The program should be qualified based on the user's matriculation qualifications.")


    def tearDown(self):
        pass






# class RecommendationAcademicQualificationTest(TestCase):
#     def setUp(self):
#         """
#         Set up the test data for the Recommender class.
#         This method runs before every test.
#         """
#         self.recommender = Recommender()

#         # Set sample programs
#         self.recommender.set_programs([
#             {
#                 "id": 1,
#                 "name": "program_1",
#                 "entry_requirement": {
#                     "spm": {
#                         "general_requirements": [
#                             {"id": 4, "subject": "Bahasa Melayu", "grade": "E"},
#                             {"id": 5, "subject": "Sejarah", "grade": "E"}
#                         ],
#                         "programme_requirements": [
#                             [
#                                 {"id": 7, "subject": "Matematik Tambahan", "grade": "C"}
#                             ],
#                             [
#                                 {"id": 1, "subject": "Matematik", "grade": "C"},
#                                 {"id": 2, "subject": "Sains", "grade": "C"}
#                             ]
#                         ]
#                     },
#                     "diploma": {"cgpa": 2.0, "NEC": ["05", "06"]},
#                     "matriculation": {"cgpa": 2.0}
#                 }
#             },
#             {
#                 "id": 2,
#                 "name": "program_2",
#                 "entry_requirement": {
#                     "spm": {
#                         "general_requirements": [
#                             {"id": 4, "subject": "Bahasa Melayu", "grade": "E"},
#                             {"id": 5, "subject": "Sejarah", "grade": "C"}
#                         ],
#                         "programme_requirements": [
#                             [
#                                 {"id": 7, "subject": "Matematik Tambahan", "grade": "C"}
#                             ],
#                             [
#                                 {"id": 1, "subject": "Matematik", "grade": "C"},
#                                 {"id": 2, "subject": "Sains", "grade": "C"}
#                             ]
#                         ]
#                     },
#                     "diploma": {"cgpa": 3.0, "NEC": ["01", "02"]},
#                     "matriculation": {"cgpa": 2.0}
#                 }
#             }
#         ])
    
#         # Set sample tags
#         self.recommender.set_tags([
#             {"id": 1, "name": "tag_1"},
#             {"id": 2, "name": "tag_2"}
#         ])

#         # Set sample program attributes
#         self.recommender.set_program_attributes([
#             {"id": 1, "program_id": 1, "tag_id": 1, "relevancy_score": 5},
#             {"id": 2, "program_id": 1, "tag_id": 2, "relevancy_score": 3},
#             {"id": 3, "program_id": 2, "tag_id": 1, "relevancy_score": 4},
#             {"id": 4, "program_id": 2, "tag_id": 2, "relevancy_score": 2}
#         ])

#         # Set sample user preferences
#         self.recommender.set_user_preferences([
#             {"tag_id": 1, "preference_score": 3},
#             {"tag_id": 2, "preference_score": 2}
#         ])

#     def test_qualify_for_program_1(self):
#         """
#         Case 1: Qualify for Program 1
#         """
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "C"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "C"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "E"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "C"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": "4.00"
#             },
#             "matriculation_qualification": None
#         })
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertIsNotNone(recommendations, "Recommendations should not be None")

#     def test_spm_not_qualified_no_general_requirements_programme_failed(self):
#         """
#         Case 2a: Diploma Qualify, SPM not qualified (Don't have general requirements) - Programme Requirements failed
#         """
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "G"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "A"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 3.00
#             },
#             "matriculation_qualification": None
#         })
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify")

#     def test_spm_not_qualified_no_general_requirements_no_programme_requirements(self):
#         """
#         Case 2a: Diploma Qualify, SPM not qualified (Don't have general requirements) - Programme Requirements non-existent
#         """
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "A"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 3.00
#             },
#             "matriculation_qualification": None
#         })
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify")

#     def test_spm_not_qualified_no_programme_requirements_programme_failed(self):
#         """
#         Case 2b: Diploma Qualify, SPM not qualified (Don't have Programme requirements) - Programme Requirements failed
#         """
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "G"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "E"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "E"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 3.00
#             },
#             "matriculation_qualification": None
#         })
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify")

#     def test_spm_not_qualified_no_programme_requirements_no_programme_requirements(self):
#         """
#         Case 2b: Diploma Qualify, SPM not qualified (Don't have Programme requirements) - Programme Requirements non-existent
#         """
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "E"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "E"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 3.00
#             },
#             "matriculation_qualification": None
#         })
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify")

#     def test_diploma_qualification_valid_cgpa_and_nec(self):
#         """
#         Case: User qualifies for one program based on either CGPA or NEC.
#         The user should be recommended one program based on their qualifications, either from CGPA or NEC.
#         """
#         # Set user data where one qualification (CGPA or NEC) should be met
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "C"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "B"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 2.5
#             },
#             "matriculation_qualification": None
#         })

#         # Check recommendations, only program_1 should be returned due to the NEC match
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(len(recommendations), 1, "Only one program should be recommended based on valid NEC qualification.")
#         self.assertEqual(recommendations[0]['id'], 1, "Program_1 should be recommended based on valid NEC qualification and CGPA.")
#         self.assertNotEqual(recommendations[0]['id'], 2, "Program_2 should not be recommended based on CGPA qualification or NEC.")

#     def test_diploma_qualification_invalid_cgpa(self):
#         """
#         Case: User qualifies for one program based on either CGPA or NEC when CGPA is valid but NEC is not.
#         The user should be recommended one program based on their CGPA.
#         """
#         # Set user data where CGPA is valid but NEC is invalid
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "C"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "B"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": 1.0  # CGPA invalid
#             },
#             "matriculation_qualification": None
#         })

#         # Check recommendations, only program_2 should be returned due to valid CGPA
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify based on CGPA or NEC.")

#     def test_diploma_qualification_invalid_NEC(self):
#         """
#         Case: User qualifies for one program based on either CGPA or NEC when CGPA is valid but NEC is not.
#         The user should be recommended one program based on their CGPA.
#         """
#         # Set user data where CGPA is valid but NEC is invalid
#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "C"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "B"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "99", # Invalid NEC
#                 "cgpa": 4.0
#             },
#             "matriculation_qualification": None
#         })

#         # Check recommendations, only program_2 should be returned due to valid CGPA
#         recommendations = self.recommender.filter_programs_on_qualifications()
#         self.assertEqual(recommendations, [], "Recommendations should be an empty list when the user does not qualify based on CGPA or NEC.")

#     def tearDown(self):
#         # Clean up any resources or state after tests
#         pass


# class RecommendationEngineLogicTest(TestCase):
#     def setUp(self):
#         """
#         Set up the test data for the Recommender class.
#         This method runs before every test.
#         """
#         self.recommender = Recommender()

#         # Set sample programs
#         self.recommender.set_programs([
#             {
#                 "id": 1,
#                 "name": "program_1",
#                 "entry_requirement": {
#                     "spm": {
#                         "general_requirements": [
#                             {"id": 4, "subject": "Bahasa Melayu", "grade": "E"},
#                             {"id": 5, "subject": "Sejarah", "grade": "E"}
#                         ],
#                         "programme_requirements": [
#                             [
#                                 {"id": 7, "subject": "Matematik Tambahan", "grade": "C"}
#                             ],
#                             [
#                                 {"id": 1, "subject": "Matematik", "grade": "C"},
#                                 {"id": 2, "subject": "Sains", "grade": "C"}
#                             ]
#                         ]
#                     },
#                     "diploma": {"cgpa": 2.0, "NEC": ["05", "06"]},
#                     "matriculation": {"cgpa": 2.0}
#                 }
#             },
#             {
#                 "id": 2,
#                 "name": "program_2",
#                 "entry_requirement": {
#                     "spm": {
#                         "general_requirements": [
#                             {"id": 4, "subject": "Bahasa Melayu", "grade": "E"},
#                             {"id": 5, "subject": "Sejarah", "grade": "C"}
#                         ],
#                         "programme_requirements": [
#                             [
#                                 {"id": 7, "subject": "Matematik Tambahan", "grade": "C"}
#                             ],
#                             [
#                                 {"id": 1, "subject": "Matematik", "grade": "C"},
#                                 {"id": 2, "subject": "Sains", "grade": "C"}
#                             ]
#                         ]
#                     },
#                     "diploma": {"cgpa": 3.0, "NEC": ["05", "06"]},
#                     "matriculation": {"cgpa": 2.0}
#                 }
#             }
#         ])
    
#         # Set sample tags
#         self.recommender.set_tags([
#             {"id": 1, "name": "tag_1"},
#             {"id": 2, "name": "tag_2"}
#         ])

#         # Set sample program attributes
#         self.recommender.set_program_attributes([
#             {"id": 1, "program_id": 1, "tag_id": 1, "relevancy_score": 5},
#             {"id": 2, "program_id": 1, "tag_id": 2, "relevancy_score": 1},
#             {"id": 3, "program_id": 2, "tag_id": 1, "relevancy_score": 1},
#             {"id": 4, "program_id": 2, "tag_id": 2, "relevancy_score": 5}
#         ])

#         self.recommender.set_user_data({
#             "spm_qualification": [
#                 {"subject_id": 1, "subject_name": "Matematik", "grade": "A"},
#                 {"subject_id": 2, "subject_name": "Sains", "grade": "A"},
#                 {"subject_id": 4, "subject_name": "Bahasa Melayu", "grade": "A"},
#                 {"subject_id": 5, "subject_name": "Sejarah", "grade": "A"}
#             ],
#             "diploma_qualification": {
#                 "diploma_institute": "Politeknik Kuching",
#                 "diploma_name": "Diploma in Computer Science",
#                 "nec_category": "05",
#                 "cgpa": "4.00"
#             },
#             "matriculation_qualification": None
#         })

#     def test_recommendation_bias_program_1(self):
#         # Set sample user preferences
#         self.recommender.set_user_preferences([
#             {"tag_id": 1, "preference_score": 5},
#             {"tag_id": 2, "preference_score": 1}
#         ])
        
#         recommendations = self.recommender.process_recommendations()
#         self.assertEqual(recommendations[0][0], 1, "Program_1 should be recommended based on user preferences and qualifications.")

#     def test_recommendation_bias_program_2(self):
#         # Set sample user preferences
#         self.recommender.set_user_preferences([
#             {"tag_id": 1, "preference_score": 1},
#             {"tag_id": 2, "preference_score": 5}
#         ])
        
#         recommendations = self.recommender.process_recommendations()
#         self.assertEqual(recommendations[0][0], 2, "Program_2 should be recommended based on user preferences and qualifications.")

#     def tearDown(self):
#         # Clean up any resources or state after tests
#         pass