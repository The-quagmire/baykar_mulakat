from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Team, Personnel, Part, Aircraft

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['team']

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'part_type', 'aircraft_type']

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super(PartForm, self).__init__(*args, **kwargs)

        # Takımın üretebileceği parça türünü belirleme
        if self.team:
            team_type_to_part_type = {
                'WING': 'WING',
                'BODY': 'BODY',
                'TAIL': 'TAIL',
                'AVIONICS': 'AVIONICS',
            }

            if self.team.team_type in team_type_to_part_type:
                # Sadece belirli bir parça üretilebilir, değiştirilemez
                self.fields['part_type'].initial = team_type_to_part_type[self.team.team_type]
                self.fields['part_type'].widget = forms.HiddenInput()
                self.fields['part_type'].disabled = True

class AircraftAssemblyForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ['name', 'aircraft_type']

    def __init__(self, *args, **kwargs):
        super(AircraftAssemblyForm, self).__init__(*args, **kwargs)
        self.fields['aircraft_type'].widget.attrs['onchange'] = 'updateAvailableParts()'