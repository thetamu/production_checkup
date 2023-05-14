import datetime

from allauth.account.forms import LoginForm
from django import forms
from django.forms import SelectDateWidget

from .models import Jobs, Jun, Mid, User, Sen


def get_username():
    if 0 < User.objects.last().id + 1 <= 9:
        d = '00'
    elif User.objects.last().id + 1 <= 99:
        d = '0'
    else:
        d = ''
    return d + str(User.objects.last().id + 1)


class CustomUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = get_username()
        self.fields['username'].help_text = ' '
        self.fields['username'].disabled = True
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label='Пароль (повторно)',
        widget=forms.PasswordInput
    )

    user_status = forms.ChoiceField(
        label='Статус работника',
        choices=(
            ('Jun', 'Работник'),
            ('Mid', 'Мастер'),
            ('Sen', 'Руководитель'),
            ('Manager', 'Менеджер')
        )
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super(forms.ModelForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username',
                  'first_name',
                  'last_name',
                  ]
        labels = {'first_name': 'Имя',
                  'last_name': 'Фамилия',
                  }


class CustomUserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ' '
        self.fields['username'].disabled = True
        self.fields['username'].label = 'Логин'
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput
    )

    password2 = forms.CharField(
        label='Пароль (повторно)',
        widget=forms.PasswordInput
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super(forms.ModelForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username',
                  'first_name',
                  'last_name',
                  ]
        labels = {'first_name': 'Имя',
                  'last_name': 'Фамилия',
                  }


class CustomJobsForm(forms.ModelForm):
    class Meta:
        model = Jobs
        fields = [
            'job_type',
            'job_reward']
        labels = {
            'job_type': 'Тип работы',
            'job_reward': 'Коэффициент оплаты (0-100%)'}
        error_messages = {'job_type': {'unique': 'Такой тип выполняемых работ существует!'}}


class CustomLoginForm(LoginForm):
    error_messages = {
        "username_password_mismatch": (
            "Имя пользователя или пароль не верны"
        ),
    }

    def login(self, *args, **kwargs):
        return super().login(*args, **kwargs)


class SelectMidForm(forms.Form):
    mid = forms.ModelChoiceField(
        empty_label='Необходим мастер',
        label='Мастер:',
        queryset=Mid.objects.all(),
        required=True
    )


class SelectSenForm(forms.Form):
    sen = forms.ModelChoiceField(
        empty_label='Необходим руководитель',
        label='Руководитель:',
        queryset=Sen.objects.all(),
        required=True
    )


class DetailDoneForm(forms.Form):
    numbers = forms.IntegerField(
        min_value=1,
        label='',
    )


class DetailUpdateForm(forms.Form):
    numbers = forms.IntegerField(
        min_value=0,
        label='',
    )


def month_list():
    month_list = [
        (1, 'Январь'), (2, 'Февраль'), (3, 'Март'),
        (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'),
        (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'),
        (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')
    ]
    complete_list = []
    for row in month_list:
        if row[0] <= datetime.date.today().month:
            complete_list.append(row)
    return tuple(complete_list)


def year_list():
    complete_list = []
    for row in range(datetime.date.today().year, datetime.date.today().year-5, -1):
        complete_list.append((row, row))
    return tuple(complete_list)


class DoneDetailArchiveForm(forms.Form):
    year_now = datetime.date.today().year
    month_accept = forms.ChoiceField(
        initial=datetime.date.today().month,
        choices=month_list(),
        label='Дата выдачи:',
        required=True)

    year_accept = forms.ChoiceField(
        initial=datetime.date.today().year,
        choices=year_list(),
        label='Дата выдачи:',
        required=True)
