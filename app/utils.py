import textwrap
import json
import os

# Dictionary for subject options
spm_subject_options = {
    "1": "Matematik",
    "2": "Sains",
    "3": "Bahasa Inggeris",
    "4": "Bahasa Melayu",
    "5": "Sejarah",
    "6": "Pendidikan Islam",
    "7": "Matematik Tambahan",
    "8": "Fizik",
    "9": "Kimia",
    "10": "Biologi",
    "11": "Prinsip Perakaunan",
    "12": "Sains Tambahan",
    "13": "Sains Komputer",
    "14": "Pendidikan Seni Visual",
    "15": "Ekonomi",
    "16": "Geografi",
}

stpm_subject_options = {
    "1": "Matematik M",
    "2": "Matematik T",
    "3": "Teknologi Komunikasi dan Informasi",
    "4": "Fizik",
    "5": "Kimia",
    "6": "Biologi"
}


matriculation_subject_options = {
    "1": "Matematik",
    "2": "Kimia",
    "3": "Fizik",
    "4": "Biologi",
    "5": "Sains Komputer",
    "6": "Asas Kejuruteraan",
    "7": "Perakaunan",
    "8": "Ekonomi",
    "9": "Pengurusan Perniagaan",
    "10": "Financial Accounting",
    "11": "Management Accounting",
    "12": "Business Accounting",
    "13": "Bahasa Inggeris",
    "14": "Pengajian Am Matrikulasi",
    "15": "Pendidikan Islam",
    "16": "Pendidikan Moral"
}


# Dictionary for grade options
grade_options = {
    "A+": 15,
    "A": 14,
    "A-": 13,
    "B+": 12,
    "B": 11,
    "B-": 10,
    "C+": 9,
    "C": 8,
    "C-": 7,
    "D+": 6,
    "D": 5,
    "D-": 4,
    "E": 3,
    "F": 2,
    "G": 1
}


letter_to_value = {
    "A+": "4.00",
    "A": "3.75",
    "A-": "3.50",
    "B+": "3.25",
    "B": "3.00",
    "C+": "2.75",
    "C": "2.50",
    "D": "2.25",
    "E": "2.00",
    "G": "1.75",  # Assuming this was your intended value
}

quiz_answer_lookup = {
    # Q1
    "1_theoretical": "🧠 I enjoy abstract, theoretical concepts",
    "1_balanced_theory_practical": "⚖️ I like a balance of theory and practice",
    "1_practical": "🛠 I prefer hands-on, practical work",

    # Q2
    "2_hate_math": "🙅 I dislike working with numbers",
    "2_manageable": "🙂 I can manage – if it's necessary",
    "2_enjoy_math": "❤️ I enjoy solving mathematical problems",

    # Q3
    "3_structured": "🧱 I prefer structured, logical work",
    "3_balanced_creative_structured": "🤝 I’m comfortable with both structure and creativity",
    "3_creative": "🎨 I thrive in creative environments",

    # Q4
    "4_software_building": "💻 Building software and applications",
    "4_both_software_infra": "🔁 I’m interested in both areas",
    "4_infrastructure_design": "🌐 Designing systems, networks, or infrastructure",

    # Q5
    "5_machines_and_systems": "🛠 Machines, technical systems, and tools",
    "5_people_and_problems": "👥 People, organizations, and solving real-world problems",

    # Q6
    "6_research_focused": "🔬 Research and exploring new knowledge",
    "6_balanced_research_industry": "⚖️ A mix of research and real-world application",
    "6_industry_application": "🏢 Solving practical problems in industry",

    # Q7 (multi-select)
    "7_mathematical_modeling": "🧮 Mathematical Modeling",
    "7_scientific_computing": "🧪 Scientific Computing",
    "7_machine_learning": "🧠 Machine Learning",
    "7_big_data_analytics": "📊 Big Data & Analytics",
    "7_game_mobile_dev": "🎮 Game & Mobile App Dev",
    "7_uiux_graphics": "🎨 UI/UX & Computer Graphics",
    "7_software_design_testing": "🧰 Software Design & Testing",
    "7_project_quality_mgmt": "📈 Project & Quality Management",
    "7_cybersecurity_networks": "🌐 Cybersecurity & Networks",
    "7_iot_embedded_systems": "📡 IoT & Embedded Systems",
}

program_details = [
    # This is a program details that will only be used for LLMs
    {
        "id": 6,
        "name": "UNIMAS - Bachelor in Computer Science (Computational Science) with Honours",
        "description": "Computational Science is the field of study concerned with constructing mathematical models and its numerical solution techniques, as well as using computers to analyse and solve scientific, social, and engineering problems.",
        "curriculum": "The Bachelor in Computer Science (Computational Science) focuses on mathematical modeling, scientific computing, and problem-solving using computational methods. Core areas include:\n- Programming & Software Development: Java, OOP, Web Development, Databases, Algorithms\n- Mathematics & Statistics: Discrete Math, Differential Equations, Probability, Modeling & Simulation\n- Systems & Infrastructure: Operating Systems, Computer Architecture, Networking, Parallel Computing\n- AI & Advanced Topics: Artificial Intelligence, Computational Science Lab, Computer Security\n- Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training\n- Capstone: Final Year Projects with research and development focus"
    },
    {
        "id": 7,
        "name": "UNIMAS - Bachelor in Computer Science (Data Engineering)",
        "description": "This program trains students to design and implement computer-based systems that support business objectives and automate processes. Focusing on system development, data management, and decision-making, students gain skills in project management, organizational theory, and technology application, preparing them to manage complex systems and create innovative solutions in various industries.",
        "curriculum": "The Bachelor in Computer Science (Data Engineering) focuses on systems development, data management, and information technologies. Core areas include:\n- Programming & Software Development: Java, OOP, Web Development, Databases, Algorithms\n- Mathematics & Statistics: Discrete Math, Probability, Statistics, Data Analytics\n- Systems & Infrastructure: Operating Systems, Computer Architecture, Distributed Systems, Networking\n- AI & Machine Learning: Artificial Intelligence, Machine Learning, Data Mining, Natural Language Processing\n- Information Systems & Process Development: Information Systems in Organisations, System Development Tools\n- Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training\n- Capstone: Final Year Projects with practical and research focus"
    },
    {
        "id": 8,
        "name": "Bachelor in Computer Science (Multimedia Computing) with Honours",
        "description": "The program focuses on software systems for synchronizing multimedia types (video, audio, image). It covers multimedia system implementation, computer graphics, and UI/UX design, providing students with broad knowledge of multimedia technologies. Students will develop practical skills in programming, game and mobile app development, as well as artificial intelligence.",
        "curriculum": "The program emphasizes multimedia systems, programming, and user experience. Core areas include:\n- Programming & Software Development: Java, OOP, Web Development, Mobile App Development, Game Design\n- Mathematics & Statistics: Discrete Math, Probability, Statistics\n- Computer Systems & Infrastructure: Operating Systems, Computer Architecture, Distributed Systems\n- Multimedia & Graphics: Computer Graphics, UI/UX Design, Data Visualization\n- AI & Advanced Topics: Artificial Intelligence, Data Analytics\n- Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training\n- Capstone: Final Year Projects with practical and research focus"
    },
    {
        "id": 9,
        "name": "Bachelor of Software Engineering with Honours",
        "description": "The program focuses on applying scientific and engineering principles to design, develop, and maintain software systems. Students will learn software engineering fundamentals, methodologies, tools, and quality assessment techniques. Graduates will be prepared with technical and soft skills, capable of developing high-quality, maintainable software, and pursuing careers in software development and management.",
        "curriculum": "The program emphasizes software engineering, development, and project management. Core areas include:\n- Programming & Software Development: Java, OOP, Web Development, Software Lab\n- Mathematics & Theoretical Foundations: Discrete Math, Automata Theory, Algorithms\n- Systems & Infrastructure: Operating Systems, Computer Architecture, Networking\n- Software Engineering Practices: System Analysis, Object-Oriented Engineering, Software Testing, Metrics, Configuration\n- Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training\n- Capstone: Final Year Projects with practical and research focus"
    },
    {
        "id": 10,
        "name": "Bachelor in Computer Science (Network Computing) with Honours",
        "description": "The program focuses on core areas of network computing, including high-speed networks, wireless systems, IoT, and blockchain. Students will gain skills in network infrastructure design, cybersecurity, and performance simulation. The program prepares graduates with both technical and soft skills for industry challenges. It takes 4 years to complete with 130 credit hours.",
        "curriculum": "The program covers network computing, security, and system development. Core areas include:\n- Programming & Software Development: Java, OOP, Web Development, System Programming\n- Mathematics & Theoretical Foundations: Discrete Math, Algorithms, Probability\n- Systems & Infrastructure: Operating Systems, Computer Architecture, Networking, Wireless Systems, IoT, Embedded Systems\n- Security & Performance: Cybersecurity, Network Simulation, Security Engineering\n- Professional Skills: Project Management, Technopreneurship, Ethics, Industrial Training\n- Capstone: Final Year Projects with practical and research focus"
    }
]


# Function to return the subject options dictionary
def get_subject_options(qualification):
    if qualification == "spm":
        return spm_subject_options

    if qualification == "matriculation":
        return matriculation_subject_options
    
    if qualification == "stpm":
        return stpm_subject_options


    return spm_subject_options

# Function to return the grade options dictionary
def get_grade_options():
    return grade_options

def format_post_data(post_data):
    """Format POST data into a readable response."""

    response_text = "<h2>Submitted Data</h2>"

    for key in post_data:
        values = post_data.getlist(key)  # Handle both single and multi-value fields

        if len(values) == 1:
            response_text += (
                f"<p><strong>{key.replace('_', ' ').title()}:</strong> {values[0]}</p>"
            )
        else:
            response_text += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {', '.join(values)}</p>"

    return response_text

# Function to return a formatted string for quiz answers
def format_quiz_answers(answers):
    global quiz_answer_lookup
    
    grouped_answers = {
        str(i): [] for i in range(1, 8)
    }

    for key in answers:
        q_num = key.split("_")[0]
        if q_num in grouped_answers:
            label = quiz_answer_lookup[key]
            grouped_answers[q_num].append(label)

    user_prefs = textwrap.dedent(f'''
        1. Do you prefer deep theoretical thinking or practical, hands-on work? (Select 1)
        {grouped_answers.get("1")[0]}

        2. How do you feel about working with mathematics? (Select 1)
        {grouped_answers.get("2")[0]}

        3. Would you describe yourself as a creative person? (Select 1)
        {grouped_answers.get("3")[0]}

        4. What kind of tech work excites you more? (Select 1)
        {grouped_answers.get("4")[0]}

        5. Who or what would you prefer to work with? (Select 1)
        {grouped_answers.get("5")[0]}

        6. Are you more drawn to research or industry application? (Select 1)
        {grouped_answers.get("6")[0]}

        7. Pick 5 topics here that interest you:
        {', '.join(grouped_answers.get("7"))}
    ''')

    return user_prefs

# Function to get program details from program_data.json
def get_program_details(program_id):
    program_data = next((p for p in program_details if p["id"] == program_id), None)

    str = textwrap.dedent(f"""
        Program Name:
        {program_data["name"]}

        Description:
        {program_data["description"]}

        Curriculum:
        {program_data["curriculum"]}
    """)

    return str

def convert_letter_to_value(letter):
    """Convert letter grade to numeric value."""
    return grade_options.get(letter, None)