from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser, Tag

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        print("[DEBUG] Initializing form")
        super().__init__(*args, **kwargs)

        # Add placeholders and Bootstrap classes
        self.fields["email"].widget.attrs.update(
            {"placeholder": "Email", "class": "form-control"}
        )
        self.fields["password1"].widget.attrs.update(
            {"placeholder": "Password", "class": "form-control"}
        )
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Confirm Password", "class": "form-control"}
        )

        # Add error highlighting
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                print(f"[DEBUG] Error in field: {field_name}")
                field.widget.attrs["class"] += " is-invalid"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        print(f"[DEBUG] Cleaning email: {email}")
        if not email:
            raise ValidationError("Email field cannot be empty.")
        if CustomUser.objects.filter(email=email).exists():
            print(f"[DEBUG] Email already exists: {email}")
            raise ValidationError("This email is already in use.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        print(f"[DEBUG] Cleaning password1: {password1}")
        if not password1:
            raise ValidationError("Password field cannot be empty.")
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if password1.isdigit():
            raise ValidationError("Password cannot be entirely numeric.")
        return password1

    def clean_password2(self):
        password2 = self.cleaned_data.get("password2")
        print(f"[DEBUG] Cleaning password2: {password2}")
        if not password2:
            raise ValidationError("Please confirm your password.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        print(f"[DEBUG] Validating passwords match: {password1} == {password2}")
        if password1 and password2 and password1 != password2:
            print("[DEBUG] Passwords do not match")
            self.add_error("password2", "Passwords do not match.")

        return cleaned_data

    def get_bootstrap_errors(self):
        print("[DEBUG] self.errors:", self.errors)

        # Collect all error messages
        error_messages = []

        # Non-field errors (like form-wide errors from clean())
        for error in self.non_field_errors():
            error_messages.append(str(error))

        # Field-specific errors
        for field, errors in self.errors.items():
            for error in errors:
                # You can customize this message format
                error_messages.append(f"{error}")

        if error_messages:
            return (
                '<div class="alert alert-danger" role="alert">'
                + "<br>".join(error_messages)
                + "</div>"
            )

        return ""




class CustomUserLoginForm(AuthenticationForm):

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholder for email field
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Email", "class": "form-control"}
        )

        self.fields["password"].widget.attrs.update(
            {"placeholder": "Password", "class": "form-control"}
        )

        # Customize error messages using Bootstrap alert class
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs["class"] += " is-invalid"

    def get_bootstrap_errors(self):
        """Returns formatted Bootstrap alerts for non-field errors."""
        if self.non_field_errors():
            return (
                '<div class="alert alert-danger">'
                + " ".join(self.non_field_errors())
                + "</div>"
            )
        return ""


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email",)


class PreferenceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PreferenceForm, self).__init__(*args, **kwargs)

        PREFERENCE_CHOICES = [(i, str(i)) for i in range(1, 10)]

        # Get All Tags
        program_tags = Tag.objects.all()

        for tag in program_tags:
            self.fields[f"preference_{tag.id}"] = forms.ChoiceField(
                choices=PREFERENCE_CHOICES,
                widget=forms.RadioSelect(attrs={"class": "btn-check"}),
                label=tag.name,
                required=False,
            )
