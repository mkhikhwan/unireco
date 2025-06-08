import numpy as np

class Recommender:
    def __init__(self, user_id: int):
        self.programs = []  # List of programs available for recommendation
        self.tags = []  # List of all possible tags (attributes)
        self.program_attributes = (
            []
        )  # List of program-tag relationships with relevancy scores
        self.user_preferences = {}  # Dictionary mapping tag_id to user preference score

    def set_programs(self, programs):
        """
        Sets the list of available programs.

        Expected format:
        programs = [
            {
                "id": int,  # Unique program ID
                "name": str,  # Program name
            },
            ...
        ]
        """
        
        self.programs = programs

    def set_tags(self, tags):
        """
        Sets the list of available tags (attributes).

        Expected format:
        tags = [
            {
                "id": int,  # Unique tag ID
                "name": str,  # Tag name (e.g., "Mathematics", "Programming")
            },
            ...
        ]
        """
        self.tags = tags

    def set_program_attributes(self, program_attributes):
        """
        Sets the list of program attributes that define how relevant each tag is to a program.

        Expected format:
        program_attributes = [
            {
                "id": int,  # Unique program-tag relationship ID
                "program_id": int,  # ID of the related program
                "tag_id": int,  # ID of the related tag
                "relevancy_score": int,  # Score indicating how relevant the tag is to the program
            },
            ...
        ]
        """
        self.program_attributes = program_attributes

    def set_user_preferences(self, user_preferences):
        """
        Sets the user's preference scores for different tags.

        Expected format:
        user_preferences = {
            tag_id: preference_score,  # Mapping of tag_id to user's preference score (e.g., {1: 5, 2: 3})
        }
        """
        self.user_preferences = user_preferences

    def calculate_similarity_scores(self):
        program_array = []
        for program in self.programs:
            program_id = program["id"]
            program_tag_scores = []
            for tag in self.tags:
                tag_id = tag["id"]
                relevancy_score = 0
                for program_attribute in self.program_attributes:
                    if (
                        program_attribute["program_id"] == program_id
                        and program_attribute["tag_id"] == tag_id
                    ):
                        relevancy_score = program_attribute["relevancy_score"]
                        break
                program_tag_scores.append(relevancy_score)

            program_array.append(program_tag_scores)

        program_attribute_matrix = np.array(program_array)
        user_preferences = self.process_user_preferences()
        similarity_scores = np.dot(program_attribute_matrix, user_preferences)

        # Compute dot product (numerator)
        dot_product = np.dot(program_attribute_matrix, user_preferences)

        # Compute norms (denominator)
        program_norms = np.linalg.norm(
            program_attribute_matrix, axis=1
        )  # Norm of each program vector
        user_norm = np.linalg.norm(user_preferences)  # Norm of user preference vector

        # Avoid division by zero
        program_norms[program_norms == 0] = 1
        user_norm = max(user_norm, 1e-10)

        # Compute cosine similarity
        similarity_scores = dot_product / (program_norms * user_norm)

        return similarity_scores

    def process_user_preferences(self):
        user_preferences = [
            self.user_preferences.get(tag["id"], 0) for tag in self.tags
        ]

        for score in user_preferences:
            if score > 1 and score < 5:
                score = score

        return user_preferences

    def get_recommendations(self):
        similarity_scores = self.calculate_similarity_scores()

        # Pair each program with its score
        program_scores = [
            {"id": program["id"], "program": program["name"], "score": score}
            for program, score in zip(self.programs, similarity_scores)
        ]

        return program_scores

    def get_recommendations_debug(self):
        similarity_scores = self.calculate_similarity_scores()

        # Pair each program with its score
        program_scores = [
            {"program": program["name"], "score": score}
            for program, score in zip(self.programs, similarity_scores)
        ]

        # Sort by highest score first
        sorted_programs = sorted(program_scores, key=lambda x: x["score"], reverse=True)

        # Print debug information
        print("\n=== Recommended Programs (Most to Least Suitable) ===")
        for rank, program in enumerate(sorted_programs, start=1):
            print(f"{rank}. {program['program']} - Score: {program['score']}")


def main():
    # Define the data as per the given entities
    # Expanded programs
    programs = [
        {"id": 1, "name": "Bachelor of Computer Science (Software Engineering)"},
        {"id": 2, "name": "Bachelor of Computer Science (Computing Science)"},
        {"id": 3, "name": "Bachelor of Computer Science (Artificial Intelligence)"},
        {"id": 4, "name": "Bachelor of Computer Science (Cybersecurity)"},
        {
            "id": 5,
            "name": "Bachelor of Computer Science (Multimedia & Game Development)",
        },
        {"id": 6, "name": "Bachelor of Computer Science (Data Science)"},
        {"id": 7, "name": "Bachelor of Computer Science (Human-Computer Interaction)"},
        {"id": 8, "name": "Bachelor of Computer Science (Bioinformatics)"},
        {"id": 9, "name": "Bachelor of Computer Science (Embedded Systems)"},
        {"id": 10, "name": "Bachelor of Computer Science (Cloud Computing)"},
    ]

    # Expanded tags
    tags = [
        {"id": 1, "name": "Programming"},
        {"id": 2, "name": "Mathematics"},
        {"id": 3, "name": "Creativity"},
        {"id": 4, "name": "Problem-Solving"},
        {"id": 5, "name": "Security"},
        {"id": 6, "name": "AI & Machine Learning"},
        {"id": 7, "name": "Networking"},
        {"id": 8, "name": "Cloud Computing"},
        {"id": 9, "name": "Data Analysis"},
        {"id": 10, "name": "Game Development"},
        {"id": 11, "name": "UI/UX Design"},
        {"id": 12, "name": "Cybersecurity"},
        {"id": 13, "name": "Mobile Development"},
        {"id": 14, "name": "Embedded Systems"},
        {"id": 15, "name": "Bioinformatics"},
    ]

    # Expanded program attributes
    program_attributes = [
        {"id": 1, "program_id": 1, "tag_id": 1, "relevancy_score": 9},
        {"id": 2, "program_id": 1, "tag_id": 4, "relevancy_score": 8},
        {"id": 3, "program_id": 2, "tag_id": 1, "relevancy_score": 10},
        {"id": 4, "program_id": 2, "tag_id": 2, "relevancy_score": 9},
        {"id": 5, "program_id": 3, "tag_id": 1, "relevancy_score": 8},
        {"id": 6, "program_id": 3, "tag_id": 6, "relevancy_score": 10},
        {"id": 7, "program_id": 4, "tag_id": 5, "relevancy_score": 10},
        {"id": 8, "program_id": 4, "tag_id": 7, "relevancy_score": 9},
        {"id": 9, "program_id": 5, "tag_id": 3, "relevancy_score": 10},
        {"id": 10, "program_id": 5, "tag_id": 10, "relevancy_score": 9},
        {"id": 11, "program_id": 6, "tag_id": 9, "relevancy_score": 10},
        {"id": 12, "program_id": 6, "tag_id": 2, "relevancy_score": 7},
        {"id": 13, "program_id": 7, "tag_id": 11, "relevancy_score": 10},
        {"id": 14, "program_id": 7, "tag_id": 3, "relevancy_score": 7},
        {"id": 15, "program_id": 8, "tag_id": 15, "relevancy_score": 10},
        {"id": 16, "program_id": 8, "tag_id": 2, "relevancy_score": 8},
        {"id": 17, "program_id": 9, "tag_id": 14, "relevancy_score": 10},
        {"id": 18, "program_id": 9, "tag_id": 1, "relevancy_score": 7},
        {"id": 19, "program_id": 10, "tag_id": 8, "relevancy_score": 10},
        {"id": 20, "program_id": 10, "tag_id": 7, "relevancy_score": 8},
    ]

    user_preferences = [
        {
            "id": 1,
            "user_id": 1,
            "tag_id": 1,
            "preference_score": 10,
        },  # Programming (Likes)
        {
            "id": 2,
            "user_id": 1,
            "tag_id": 2,
            "preference_score": 1,
        },  # Mathematics (Hate)
        {
            "id": 3,
            "user_id": 1,
            "tag_id": 3,
            "preference_score": 7,
        },  # Creativity (Neutral)
        {
            "id": 4,
            "user_id": 1,
            "tag_id": 4,
            "preference_score": 6,
        },  # Problem Solving (Neutral)
        {
            "id": 5,
            "user_id": 1,
            "tag_id": 5,
            "preference_score": 5,
        },  # Security (Neutral)
        {
            "id": 6,
            "user_id": 1,
            "tag_id": 6,
            "preference_score": 4,
        },  # AI & Machine Learning (Neutral)
        {
            "id": 7,
            "user_id": 1,
            "tag_id": 7,
            "preference_score": 3,
        },  # Networking (Low Interest)
        {
            "id": 8,
            "user_id": 1,
            "tag_id": 8,
            "preference_score": 10,
        },  # Game Development (Likes)
    ]

    # Instantiate the Recommender class
    recommender = Recommender(user_id=1)

    # Set the programs, tags, program attributes, and user preferences
    recommender.set_programs(programs)
    recommender.set_tags(tags)
    recommender.set_program_attributes(program_attributes)
    recommender.set_user_preferences(
        {pref["tag_id"]: pref["preference_score"] for pref in user_preferences}
    )

    # Get the recommendations and print the results
    print(recommender.get_recommendations())


# Run the main function
# if __name__ == "__main__":
#     main()
