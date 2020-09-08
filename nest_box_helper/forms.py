from django import forms
from django.forms import ModelForm, Textarea, DateInput
from django.contrib.auth.forms import UserCreationForm
from nest_box_helper.models import Account, Sheet, Park, Attempt, UserParks, Box
from django.contrib.auth import authenticate


class SheetForm(forms.ModelForm):
    class Meta:
        model = Sheet
        fields = (
            "date",
            "species",
            "eggs",
            "nest_status",
            "live_young",
            "dead_young",
            "adult_activity",
            "young_status",
            "management_activity",
            "cowbird_evidence",
            "comments"
        )

        widgets = {
                'comments': Textarea(attrs={'cols': 25, 'rows': 1}),
                'date': DateInput(attrs={'class':'datepicker'}),
                }


class AddAttemptForm(forms.ModelForm):
    class Meta:
        model = Attempt
        fields = ('attempt_number',)


class AddBoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ('box_number',)


class AddParkForm(forms.ModelForm):
    class Meta:
        model = UserParks
        fields = ('park_name',)


class UpdateSheetForm(forms.ModelForm):
    class Meta:
        model = Sheet
        fields = (
            "date",
            "species",
            "eggs",
            "nest_status",
            "live_young",
            "dead_young",
            "adult_activity",
            "young_status",
            "management_activity",
            "cowbird_evidence",
            "comments"
        )

        widgets = {
                'comments': Textarea(attrs={'cols': 25, 'rows': 1}),
                'date': DateInput(attrs={'class':'datepicker', 'format' : "mm/dd/yy"}),
                }

    def save(self, commit=True):
        sheet_form = self.instance
        sheet_form.date = self.cleaned_data['date']
        sheet_form.species = self.cleaned_data['species']
        sheet_form.eggs = self.cleaned_data['eggs']
        sheet_form.nest_status = self.cleaned_data['nest_status']
        sheet_form.live_young = self.cleaned_data['live_young']
        sheet_form.dead_young = self.cleaned_data['dead_young']
        sheet_form.adult_activity = self.cleaned_data['adult_activity']
        sheet_form.young_status = self.cleaned_data['young_status']
        sheet_form.management_activity = self.cleaned_data['management_activity']
        sheet_form.cowbird_evidence = self.cleaned_data['cowbird_evidence']
        sheet_form.comments = self.cleaned_data['comments']

        if commit:
            sheet_form.save()
        return sheet_form


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text="Required")

    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")


class AccountAuthenticationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid Login")


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('email', 'username')

    def clean_email(self):
        if self.is_valid():
            email=self.cleaned_data['email']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s" is already in use.' % account)

    def clean_username(self):
        if self.is_valid():
            username=self.cleaned_data['username']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
            except Account.DoesNotExist:
                return username
            raise forms.ValidationError('Username "%s" is already in use.' % username)
