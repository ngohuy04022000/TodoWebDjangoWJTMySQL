import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User

from .models import ToDoItem, ToDoList


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Tài khoản', max_length=30)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput())
    password2 = forms.CharField(label='Nhập lại mật khẩu', widget=forms.PasswordInput())

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError("Tên tài khoản có kí tự đặc biệt")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Tài khoản đã tồn tại")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email đã được sử dụng")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1 or password1 != password2:
            raise forms.ValidationError("Mật khẩu nhập lại không khớp")
        user = User(
            username=self.cleaned_data.get('username', ''),
            email=self.cleaned_data.get('email', ''),
        )
        password_validation.validate_password(password2, user)
        return password2

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
        )


class ToDoListForm(forms.ModelForm):
    """List form; the owner is set by the view and checked for duplicate titles."""

    class Meta:
        model = ToDoList
        fields = ["title"]
        labels = {"title": "Tên danh sách"}

    def clean_title(self):
        title = self.cleaned_data["title"]
        duplicates = ToDoList.objects.filter(owner_id=self.instance.owner_id, title__iexact=title)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise forms.ValidationError("Bạn đã có danh sách với tên này")
        return title


class ToDoItemForm(forms.ModelForm):
    class Meta:
        model = ToDoItem
        fields = ["task", "description", "due_date", "status"]
        labels = {
            "task": "Công việc",
            "description": "Mô tả",
            "due_date": "Hạn hoàn thành",
            "status": "Đã hoàn thành",
        }
        widgets = {
            "due_date": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }
