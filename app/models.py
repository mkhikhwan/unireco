from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class DegreeField(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    class QuestionType(models.TextChoices):
        SCALE_1_5 = 'SCALE_1_5', _('Scale 1 to 5')
        YES_NO = 'YES_NO', _('Yes/No Question')

    question_text_1 = models.TextField(help_text=_("Main question text or label."))
    question_text_2 = models.TextField(blank=True, null=True, help_text=_("Secondary statement, if any (e.g., for scale questions)."))
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, help_text=_("The Tag this question relates to."))
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        help_text=_("Type of question, determines rendering and answer format.")
    )
    question_number = models.PositiveIntegerField(unique=True, help_text=_("Order/number of the question."))

    def __str__(self):
        return f"Q{self.question_number}: {self.question_text_1[:50]}... ({self.tag.name})"

class UserData(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    spm_qualification = models.JSONField(blank=True, null=True)
    stpm_qualification = models.JSONField(blank=True, null=True)
    matriculation_qualification = models.JSONField(blank=True, null=True)
    diploma_qualification = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"UserData for {self.user.email}"


class UserPreference(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    preference_score = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.email} - {self.tag.name} ({self.preference_score})"


class University(models.Model):
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    logo = models.URLField(max_length=500, default="https://placehold.co/500x500")

    def __str__(self):
        return self.name


class EntryRequirement(models.Model):
    stpm = models.JSONField(default=dict, blank=True, null=True)
    matriculation = models.JSONField(default=dict, blank=True, null=True)
    diploma = models.JSONField(default=dict, blank=True, null=True)
    explaination = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Entry Requirement {self.id}"


class Programme(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    entry_requirement = models.ForeignKey(EntryRequirement, on_delete=models.CASCADE, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True)
    image = models.URLField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    mode = models.CharField(max_length=100, blank=True, null=True)
    career_opportunities = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    degree_field = models.ForeignKey(DegreeField, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class TagDegreeField(models.Model):
    degree_field = models.ForeignKey(DegreeField, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    relevancy_score = models.IntegerField(default=0)  # Default to 5

    def __str__(self):
        return f"{self.degree_field.name} - {self.tag.name} - Score: {self.relevancy_score}"

class FavouriteProgramme(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} - {self.programme.name}"
