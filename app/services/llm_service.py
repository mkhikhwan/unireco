import ollama
import textwrap

class BaseLLM:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        response = ollama.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])

        return response['message']['content']
    
    def explain_recommendation(self, questionnaire_and_answers: str, program_details: str) -> str:
        prompt = f"""
            You are an educational advisor helping students understand why a university program suits their interests and preferences.
            You will be provided with the full questionnaire (including questions and the user's answers), as well as the details of the recommended program.
            Your task is to write a short, high-level explanation, in 50 words or less, of why this program might be suitable recommendation for the user.
            No need to explain the program details in depth, just focus on the user's preferences and how they align with the program.

            Be friendly, concise, and clear. Do not exaggerate or make assumptions outside the given input.

            Questionnaire and Answers:
            {questionnaire_and_answers}

            Program Details:
            {program_details}

            Explanation:
        """

        return self.generate(prompt)

    
# def main():
#     llm = OllamaLLM("mistral")  # or any local model you pulled

#     user_prefs =textwrap.dedent('''
#         1. Do you prefer deep theoretical thinking or practical, hands-on work? (Select 1)
#         🧠 I enjoy abstract, theoretical concepts

#         2. How do you feel about working with mathematics? (Select 1)
#         ❤️ I enjoy solving mathematical problems

#         3. Would you describe yourself as a creative person? (Select 1)
#         🧱 I prefer structured, logical work

#         4. What kind of tech work excites you more? (Select 1)
#         🔁 I’m interested in both areas

#         5. Who or what would you prefer to work with? (Select 1)
#         🛠 Machines, technical systems, and tools

#         6. Are you more drawn to research or industry application? (Select 1)
#         🔬 Research and exploring new knowledge

#         7. Pick 5 topics here that interest you:
#         🧮 Mathematical Modeling
#         🧪 Scientific Computing
#         🧠 Machine Learning
#         📊 Big Data & Analytics
#         🌐 Cybersecurity & Networks
#     ''')

#     program_details = textwrap.dedent('''
#         1. UNIMAS - Bachelor in Computer Science (Computational Science) with Honours
        
#         PROGRAM DESCRIPTION:
#         Computational Science is the field of study concerned with constructing mathematical models and its numerical solution techniques, as well as using computers to analyse and solve scientific, social, and engineering problems.

#         PROGRAMME CURRICULUM COURSES (Compressed):
#         The Bachelor in Computer Science (Computational Science) focuses on mathematical modeling, scientific computing, and problem-solving using computational methods. Core areas include:
#         - Programming & Software Development: Java, OOP, Web Development, Databases, Algorithms
#         - Mathematics & Statistics: Discrete Math, Differential Equations, Probability, Modeling & Simulation
#         - Systems & Infrastructure: Operating Systems, Computer Architecture, Networking, Parallel Computing
#         - AI & Advanced Topics: Artificial Intelligence, Computational Science Lab, Computer Security
#         - Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training
#     ''')

#     explanation = llm.explain_recommendation(user_prefs, program_details)
#     print("Explanation:\n", explanation)

# if __name__ == "__main__":
#     main()
