from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    CustomUser,
    Tag,
    DegreeField,
    Question,
    UserData,
    UserPreference,
    University,
    EntryRequirement,
    Programme,
    TagDegreeField,
    FavouriteProgramme)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Tag)
class ProgramTagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")  # Display ID and name in the admin list view
    search_fields = ("name",)  # Add search functionality


@admin.register(DegreeField)
class DegreeFieldAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_number", "question_text_1", "tag", "question_type")
    list_filter = ("question_type", "tag")
    search_fields = ("question_text_1", "tag__name")


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name")
    search_fields = ("user__email", "full_name")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "tag", "preference_score")
    list_filter = ("tag",)
    search_fields = ("user__email", "tag__name")


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "website")
    search_fields = ("name", "location")


@admin.register(EntryRequirement)
class EntryRequirementAdmin(admin.ModelAdmin):
    list_display = ("id", "explaination")


admin.site.register(Programme)
admin.site.register(TagDegreeField)
admin.site.register(FavouriteProgramme)
