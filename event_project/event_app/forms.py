from django import forms
from .models import CustomUser, Event, Registration

class AddBoyForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["boy_id", "username",]
        widgets = {
            "boy_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Boy ID"}),
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter Name"}),
            
        }


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "date", "location", "description",
                  "total_seats", "payment_per_boy","image"]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "total_seats": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_per_boy": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }



class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []  # no fields — we will assign boy/event/seat server-side
        # Keep empty so template just posts; you can add a confirm checkbox if desired

    @property
    def payment(self):
        return self.payment_set.first()
    



class BoyProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "phone", "upi_id", "profile_pic"]

        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.NumberInput(attrs={"class": "form-control"}),
            "upi_id": forms.TextInput(attrs={"class": "form-control"}),
            "profile_pic": forms.FileInput(attrs={"class": "form-control"}),
        }

