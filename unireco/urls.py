"""
URL configuration for unireco project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from app.views import (
    home,
    about,
    user_login,
    user_logout,
    user_signup,
    search_programs,
    view_program,
    interest_form,
    spm_form,
    diploma_form,
    recommendation,
    favourite,
    api_recommendation,
    get_started,
    api_check_eligibility,
    admin_add_program,
    admin_add_entry_requirement,
    qualification_selection,
    matriculation_form,
    stpm_form,
    api_add_to_favourites,
    api_delete_from_favourites
)

urlpatterns = [
    path("adminsql/", admin.site.urls),
    path("admin/add_program/", admin_add_program, name="admin_add_program"),
    path("admin/add_entry_requirement/", admin_add_entry_requirement, name="admin_add_entry_requirement"),
    path("", home),
    path("about/", about),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("signup/", user_signup, name="signup"),
    path("search/", search_programs, name="search_programs"),
    path("program/<int:programme_id>/", view_program, name="view_program"),
    path("interest/", interest_form, name="interest_form"),
    path("recommendation/", recommendation, name="recommendation_view"),
    path('api/recommendation/', api_recommendation, name='recommendation_api'),
    path("favourite/", favourite, name="favourite"),
    path("get-started/", get_started, name="get_started"),
    path("api/check_eligibility/<int:program_id>/", api_check_eligibility, name="check_eligibility_api"),
    path("qualification/", qualification_selection, name="qualification_selection"),
    path("qualification/diploma/", diploma_form, name="diploma_form"),
    path("qualification/matriculation/", matriculation_form, name="matriculation_form"),
    path("qualification/spm/", spm_form, name="spm_form"),
    path("qualification/stpm/", stpm_form, name="stpm_form"),
    path("api/favourite/add/<int:program_id>/", api_add_to_favourites, name="add_to_favourite_api"),
    path("api/favourite/delete/<int:program_id>/", api_delete_from_favourites, name="delete_from_favourite_api"),
]
