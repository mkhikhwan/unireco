from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import CustomUserLoginForm, PreferenceForm, CustomUserCreationForm
from .utils import format_post_data, get_subject_options, get_grade_options, format_quiz_answers, get_program_details, spm_subject_options, matriculation_subject_options, stpm_subject_options
from django.shortcuts import render, get_object_or_404
from app.services.recommender import Recommender
# from app.services.llm_service import OllamaLLM
from django.http import JsonResponse
import time
from django.contrib.auth.decorators import login_required

from .models import (
    CustomUser,
    Tag,
    UserData,
    UserPreference,
    University,
    EntryRequirement,
    Programme,
    FavouriteProgramme,
    DegreeField,
    TagDegreeField,
    Question
)


# Home Page
def home(request):
    return render(request, "home.html")

# Landing Page
def about(request):
    return render(request, "about.html")

# User Login Page
def user_login(request):
    if request.method == "POST":
        form = CustomUserLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/")  # Redirect to home after login
    else:
        form = CustomUserLoginForm()
    return render(request, "user/login.html", {"form": form})

# User Logout View
def user_logout(request):
    logout(request)
    return redirect("/")

# User Signup View
def user_signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in after signup
            return redirect("/")  # Change "home" to your homepage URL name
    else:
        print("Failed to create user")
        form = CustomUserCreationForm()

    return render(request, "user/signup.html", {"form": form})

# Search / View All Programs
def search_programs(request):
    programmes = Programme.objects.select_related("university").all()

    programs_list = [
        {
            "id": programme.id,
            "name": programme.name,
            "university": programme.university.name,
            "logo": programme.university.logo,
            "description": programme.description
        }
        for programme in programmes
    ]

    return render(request, "program/search_program.html", {"programs": programs_list})

# View Program
def view_program(request, programme_id):
    # This safely retrieves the object or returns a 404 page
    programme = get_object_or_404(
        Programme.objects.select_related('entry_requirement', 'university','degree_field'),
        id=programme_id
    )

    university_detail = {
        "name": programme.university.name,
        "location": programme.university.location,
        "university_page_url": programme.university.website,
    }

    program_detail = {
        "id": programme.id,
        "program_name": programme.name,
        "program_image": programme.image,
        "duration": programme.duration,
        "mode": programme.mode,
        "career_opportunities": programme.career_opportunities,
        "description": programme.description,
        "entry_requirement": programme.entry_requirement.explaination,
        "university": university_detail
    }

    degreeField_id = programme.degree_field.id
    related_programmes = [
        {
            "name": programme.name,
            "description": programme.description,
            "university": programme.university.name,
            "image": programme.university.logo,
            "link": f"/program/{programme.id}"
        }
        for programme in Programme.objects.filter(degree_field__id=degreeField_id)
        if programme.id != programme_id
    ]

    return render(
        request, "program/view_program.html", {"program_detail": program_detail, "related_programmes": related_programmes}
    )

# Interest Quiz
@login_required(login_url='/login')
def interest_form(request):
    riasec_tags = {
        'realistic_1', 'realistic_2',
        'investigative_1', 'investigative_2',
        'artistic_1', 'artistic_2',
        'social_1', 'social_2',
        'enterprising_1', 'enterprising_2',
        'conventional_1', 'conventional_2',
    }

    if request.method == "POST":
        user = request.user
        submitted_data = request.POST
        print("submitted_data", submitted_data)

        # Clear previous preferences for this user
        UserPreference.objects.filter(user=user).delete()

        for tag, value_list in submitted_data.lists():
            if tag == 'csrfmiddlewaretoken':
                continue

            try:
                tag_obj = Tag.objects.get(name=tag)
                value = value_list[0].strip().lower()

                if tag in riasec_tags:
                    try:
                        score = int(value)  # Parse as integer (e.g., 1–5 scale)
                    except ValueError:
                        print(f"Invalid integer value for RIASEC tag {tag}: {value}")
                        continue
                else:
                    score = 1 if value == 'yes' else 0

                # Store preference
                UserPreference.objects.create(user=user, tag=tag_obj, preference_score=score)

            except Tag.DoesNotExist:
                print(f"Tag not found: {tag}")

        print("✅ Preferences successfully inserted for user:", user.email)
        return redirect('/recommendation')

    # GET method – show the form
    questions = Question.objects.order_by('question_number').all()
    context = {'questions': questions}
    return render(request, "question-form/interest.html", context)

# SPM Form
def spm_form(request):
    choices = {
        "subjects": get_subject_options('spm'),
        "grades": get_grade_options(),
    }

    if request.method == "POST":
        # TODO: Handle the form submission and save the data to the database
        subjects = request.POST.getlist('subjects[]')
        grades = request.POST.getlist('grades[]')

        spm_result_data = []
        for subject, grade in zip(subjects, grades):
            spm_result_data.append({
                "id": int(subject),
                "subject": spm_subject_options[subject],
                "grade": grade,
            })

        user = request.user
        user_data, created = UserData.objects.get_or_create(user=user)
        user_data.spm_qualification = spm_result_data
        user_data.save()
        print("SPM Data Saved:", spm_result_data)

        return redirect("/interest")
        

    return render(request, "question-form/spm.html", {"choices": choices})

# Select Qualification Page
def qualification_selection(request):
    if request.method == 'POST':
        user = request.user
        selection = request.POST.get('qualification_selection')

        # Get or create the user's data
        user_data, created = UserData.objects.get_or_create(user=user)

        # Clear any existing qualification fields
        user_data.diploma_qualification = None
        user_data.matriculation_qualification = None
        user_data.stpm_qualification = None
        user_data.save()
        print("Qualification fields cleared for user:", user)

        # Redirect based on selection
        if selection == 'diploma':
            return redirect('/qualification/diploma')
        elif selection == 'matriculation':
            return redirect('/qualification/matriculation')
        elif selection == 'stpm':
            return redirect('/qualification/stpm')
        else:
            # Handle unexpected value
            return redirect('qualification/selection')  # Or show an error

    return render(request, 'question-form/qualification_selection.html')

# Diploma Form Page
def diploma_form(request):
    institutions = [
        "Politeknik Kuching",
        "Universiti Institut Teknologi Mara (UiTM)",
    ]

    diploma_names = [
        "Diploma in Computer Science",
        "Diploma in Information Technology",
    ]

    nec_categories = {
        "05": "05: Natural sciences, mathematics and statistics",
        "06": "06: Information and communication technologies",
        "07": "07: Engineering, manufacturing and construction"
    }

    context = {
        "institutions": institutions,
        "diploma_names": diploma_names,
        "nec_categories": nec_categories,
    }

    if request.method == "POST":
        diploma_data = {
            "diploma_institute": request.POST.get("diploma_institute"),
            "diploma_name": request.POST.get("diploma_name"),
            "nec_category": request.POST.get("nec"),
            "cgpa": request.POST.get("cgpa"),
        }

        user = request.user
        user_data, created = UserData.objects.get_or_create(user=user)
        user_data.diploma_qualification = diploma_data
        user_data.save()
        print("Diploma Data Saved:", diploma_data)
        
        return redirect("/qualification/spm")

        # return HttpResponse(format_post_data(request.POST))

    return render(request, "question-form/diploma.html", context)

# Matriculation Form Page
def matriculation_form(request):
    choices = {
        "subjects": get_subject_options('matriculation'),
        "grades": get_grade_options(),
    }

    if request.method == "POST":
        # TODO: Handle the form submission and save the data to the database
        subjects = request.POST.getlist('subjects[]')
        grades = request.POST.getlist('grades[]')

        matriculation_subject_data = []
        for subject, grade in zip(subjects, grades):
            matriculation_subject_data.append({
                "id": int(subject),
                "subject": matriculation_subject_options[subject],
                "grade": grade,
            })

        matriculation_result_data = {
            "cgpa": request.POST.get('cgpa'),
            "subjects" : matriculation_subject_data
        }

        user = request.user
        user_data, created = UserData.objects.get_or_create(user=user)
        user_data.matriculation_qualification = matriculation_result_data
        user_data.save()
        print("Matriculation Data Saved:", matriculation_result_data)

        return redirect("/qualification/spm")

    return render(request, "question-form/matriculation.html", {"choices": choices})

# STPM Form Page
def stpm_form(request):
    choices = {
        "subjects": get_subject_options('stpm'),
        "grades": get_grade_options(),
    }

    if request.method == "POST":
        subjects = request.POST.getlist('subjects[]')
        grades = request.POST.getlist('grades[]')

        stpm_subject_data = []
        for subject, grade in zip(subjects, grades):
            stpm_subject_data.append({
                "id": int(subject),
                "subject": stpm_subject_options[subject],
                "grade": grade,
            })

        stpm_result_data = {
            "cgpa": request.POST.get('cgpa'),
            "subjects": stpm_subject_data
        }

        user = request.user
        user_data, created = UserData.objects.get_or_create(user=user)
        user_data.stpm_qualification = stpm_result_data
        user_data.save()
        print("STPM Data Saved:", stpm_result_data)

        return redirect("/qualification/spm")

    return render(request, "question-form/stpm.html", {"choices": choices})

def favourite(request):
    user = request.user
    notDoneQuiz = False

    if not UserPreference.objects.filter(user=user).exists():
        notDoneQuiz = True

    favourite_programs = FavouriteProgramme.objects.filter(user=user).select_related('programme', 'programme__university')

    program_favourites = [
        {
            "id" : fav.programme.id,
            "name": fav.programme.name,
            "university": fav.programme.university.name,
            "logo": fav.programme.university.logo,
            "description": fav.programme.description,
            "program_url": f"/programmes/{fav.programme.id}/",
        }
        for fav in favourite_programs
    ]

    riasec = calculate_riasec_value(user)
    riasec_desc = {
        "realistic": "You enjoy hands-on activities and working with tools, machines, or the outdoors.",
        "investigative": "You are curious, analytical, and enjoy solving complex problems or exploring abstract ideas.",
        "artistic": "You value creativity, self-expression, and open-ended problem solving.",
        "social": "You enjoy helping others, teaching, or working in team environments that support collaboration.",
        "enterprising": "You enjoy leading, persuading, and managing for organizational goals or economic success.",
        "conventional": "You prefer structured tasks and managing data or details, often excelling in organized environments."
    }
    top_2 = sorted(riasec.items(), key=lambda item: item[1], reverse=True)[:2]
    top_2_descriptions = {trait: riasec_desc[trait] for trait, _ in top_2}

    interest_list = get_user_interest(user)

    return render(request, "favourite.html", 
                  {"programs": program_favourites, 
                   "riasec": riasec, 
                   "riasec_desc": top_2_descriptions, 
                   "interest_list": interest_list,
                   "isNotDoneQuiz": notDoneQuiz}
                   )

def get_started(request):
    # Check if logged in
    if not request.user.is_authenticated:
        return redirect("/login")
    
    return redirect("/qualification")

@login_required(login_url='/login')
def recommendation(request):
    user = request.user
    if not UserData.objects.filter(user=user).exists():
        return redirect("/get-started")

    if not UserPreference.objects.filter(user=user).exists():
        return redirect("/get-started")

    recommender = Recommender(user)
    scores = recommender.get_all_subfield_scores()

    # return HttpResponse("Recommendation API is not available. Please use the /api/recommendation endpoint.")
    return render(request, "recommendation.html")

def api_check_eligibility(request,program_id):
    user = request.user
    if not user.is_authenticated:
        return redirect("/login")

    program = Programme.objects.get(id=program_id)
    Recommender = Recommender(user)
    is_qualified = Recommender.isProgramQualified(program)

    return JsonResponse({"is_qualified": is_qualified}, safe=False)

# API Views
# API Get Recommendations
def api_recommendation(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("/login")
    
    # Get top 3 most compatible fields
    recommender = Recommender(user)
    scores = recommender.get_all_subfield_scores()

    subfield_recommendations = [
        {
            "name": subfield.name,
            "match_percentage": round(score * 100),
            "description": subfield.description,  # Ensure this field exists in your model
            "programs": [
                {
                    "id": program.id,
                    "name": program.name,
                    "qualified": recommender.isProgramQualified(program),
                    "institute": program.university.name
                }
                for program in Programme.objects.filter(degree_field=subfield)
            ]
        }
        for subfield, score in scores
    ]

    return JsonResponse(subfield_recommendations, safe=False)

# API Add to Favourites
def api_add_to_favourites(request, program_id):
    user = request.user

    try:
        programme = Programme.objects.get(id=program_id)
    except Programme.DoesNotExist:
        return JsonResponse({"error": "Programme not found"}, status=404)

    # Check if already in favourites
    if FavouriteProgramme.objects.filter(user=user, programme=programme).exists():
        return JsonResponse({"message": "Already in favourites"}, status=200)

    # Add to favourites
    FavouriteProgramme.objects.create(user=user, programme=programme)
    return JsonResponse({"message": "Added to favourites successfully"}, status=201)

# API Delete From Favourites
def api_delete_from_favourites(request, program_id):
    user = request.user

    try:
        programme = Programme.objects.get(id=program_id)
    except Programme.DoesNotExist:
        return JsonResponse({"error": "Programme not found"}, status=404)

    try:
        favourite = FavouriteProgramme.objects.get(user=user, programme=programme)
        favourite.delete()
        return JsonResponse({"message": "Removed from favourites successfully"}, status=200)
    except FavouriteProgramme.DoesNotExist:
        return JsonResponse({"message": "Not in favourites"}, status=200)

# Admin Views
def admin_add_program(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        entry_requirement_id = request.POST.get('entry_requirement')
        university_id = request.POST.get('university')
        image = request.POST.get('image')
        duration = request.POST.get('duration')
        mode = request.POST.get('mode')
        career_opportunities = request.POST.get('career_opportunities')
        url = request.POST.get('url')
        degree_field_id = request.POST.get('degree_field')

        # Convert related fields
        entry_requirement = EntryRequirement.objects.get(id=entry_requirement_id) if entry_requirement_id else None
        university = University.objects.get(id=university_id) if university_id else None
        degree_field = DegreeField.objects.get(id=degree_field_id) if degree_field_id else None

        # Handle JSON field (be cautious: no validation here)
        import json
        try:
            career_data = json.loads(career_opportunities) if career_opportunities else None
        except json.JSONDecodeError:
            career_data = None  # Or handle error

        Programme.objects.create(
            name=name,
            description=description,
            entry_requirement=entry_requirement,
            university=university,
            image=image,
            duration=duration,
            mode=mode,
            career_opportunities=career_data,
            url=url,
            degree_field=degree_field
        )

        return HttpResponse("Programme added successfully!")

    # If GET request, load the form
    entry_requirements = EntryRequirement.objects.all()
    universities = University.objects.all()
    degree_fields = DegreeField.objects.all()

    context = {
        'entry_requirements': entry_requirements,
        'universities': universities,
        'degree_fields': degree_fields,
    }

    return render(request, 'admin/add_program.html', context)

def admin_add_entry_requirement(request):
    # TODO: Implement this function to add a new entry requirement
    pass

    # subject_options = get_subject_options()  # { "1": "Math", ... }
    # nec_categories = {
    #     "05": "05: Natural sciences, mathematics and statistics",
    #     "06": "06: Information and communication technologies",
    #     "07": "07: Engineering, manufacturing and construction"
    # }

    # if request.method == "POST":
    #     # Programme linkage
    #     programme_id = request.POST.get("programme_id")
    #     programme = Programme.objects.get(id=programme_id)

    #     # General SPM Requirements
    #     general_subjects = request.POST.getlist('general_subjects[]')
    #     general_grades = request.POST.getlist('general_grades[]')

    #     # Programme SPM Requirements
    #     prog_subjects_grouped = request.POST.getlist('prog_subjects_grouped[]')
    #     prog_grades_grouped = request.POST.getlist('prog_grades_grouped[]')

    #     # Parse general requirements
    #     general_requirements = []
    #     for sub_id, grade in zip(general_subjects, general_grades):
    #         general_requirements.append({
    #             "id": int(sub_id),
    #             "subject": subject_options[sub_id],
    #             "grade": grade
    #         })

    #     # Parse programme requirements
    #     programme_requirements = []
    #     for group in prog_subjects_grouped:
    #         group_data = []
    #         entries = group.split(",")  # e.g., "1|C,2|C"
    #         for entry in entries:
    #             sub_id, grade = entry.split("|")
    #             group_data.append({
    #                 "id": int(sub_id),
    #                 "subject": subject_options[sub_id],
    #                 "grade": grade
    #             })
    #         programme_requirements.append(group_data)

    #     spm_json = {
    #         "general_requirements": general_requirements,
    #         "programme_requirements": programme_requirements
    #     }

    #     # Optional diploma/matric/stpm
    #     diploma_json = None
    #     matric_json = None
    #     stpm_json = None

    #     if request.POST.get("diploma_cgpa"):
    #         diploma_json = {
    #             "cgpa": float(request.POST["diploma_cgpa"]),
    #             "NEC": request.POST.getlist("diploma_nec[]")
    #         }

    #     if request.POST.get("matric_cgpa"):
    #         matric_json = {
    #             "cgpa": float(request.POST["matric_cgpa"])
    #         }

    #     if request.POST.get("stpm_cgpa"):
    #         stpm_json = {
    #             "cgpa": float(request.POST["stpm_cgpa"]),
    #             "subjects": request.POST.getlist("stpm_subjects[]")
    #         }

    #     # Create and link the EntryRequirement
    #     entry_req = EntryRequirement.objects.create(
    #         spm=spm_json,
    #         diploma=diploma_json,
    #         matriculation=matric_json,
    #         stpm=stpm_json
    #     )

    #     programme.entry_requirement = entry_req
    #     programme.save()

    #     return redirect('/entry-requirements')

    # choices = {
    #     "subjects": subject_options,
    #     "grades": get_grade_options(),
    #     "nec_codes": nec_categories,
    #     "programmes": Programme.objects.all()
    # }

    # return render(request, "entry/add_entry_requirement.html", {"choices": choices})

# # Functions that are used inside views
def calculate_riasec_value(user):
    user_pref = UserPreference.objects.filter(user=user)
    
    riasec_ids = {
        'realistic': [70, 71],
        'investigative': [72, 73],
        'artistic': [74, 75],
        'social': [76, 77],
        'enterprising': [78, 79],
        'conventional': [80, 81],
    }

    riasec_scores = {}

    for trait, ids in riasec_ids.items():
        values = []
        for id in ids:
            pref = user_pref.filter(tag_id=id).first()
            if pref:
                values.append(pref.preference_score)  # Assuming your model has a `value` field
        riasec_scores[trait] = sum(values) / len(values) if values else 0


    return riasec_scores

def get_user_interest(user):
    user_pref = UserPreference.objects.filter(user=user)

    interest_tag_ids = range(58, 70)
    preferences = UserPreference.objects.filter(
        user=user,
        tag_id__in=interest_tag_ids
    ).values_list('tag_id', 'preference_score')

    interest_list = [x for x in preferences if x[1] > 0]
    tag_ids = [tag_id for tag_id, score in interest_list]
    interest_string_list = Tag.objects.filter(id__in=tag_ids).values_list('desc', flat=True)
    
    return interest_string_list




# def handle_prompt(arrOfAnswers, program_id):
#     # This function will handle the prompt generation for the LLM
#     # It will take the questionnaire and answers and generate a prompt for the LLM
#     # The prompt will be used to generate a recommendation for the user

#     questionnaire_and_answers = format_quiz_answers(arrOfAnswers)
#     program_details = get_program_details(program_id)

#     llm = OllamaLLM("mistral")
#     explanation = llm.explain_recommendation(questionnaire_and_answers, program_details)

#     return explanation
