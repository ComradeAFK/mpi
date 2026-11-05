from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Comment, GameComment, Review



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('title', 'rating', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Отличная игра для вечеринок', 'class': 'form-control form-control-lg'}),
            'rating': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'text': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Расскажите о своих впечатлениях...', 'class': 'form-control'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 50:
            raise forms.ValidationError('Обзор должен содержать хотя бы 50 символов.')
        return text

class GameCommentForm(forms.ModelForm):
    class Meta:
        model = GameComment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': _('Ваш вопрос или комментарий к игре...')}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError(_('Текст не может быть пустым.'))
        if len(text) > 1000:
            raise forms.ValidationError(_('Текст не должен превышать 1000 символов.'))
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('subject', 'text')
        labels = {
            'subject': _('Тема'),
            'text': _('Сообщение'),
        }
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': _('Тема комментария')}),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Текст комментария')}),
        }

    def clean_subject(self):
        subject = self.cleaned_data.get('subject', '').strip()
        if not subject:
            raise forms.ValidationError(_('Тема не может быть пустой.'))
        if len(subject) > 150:
            raise forms.ValidationError(_('Тема не должна превышать 150 символов.'))
        return subject

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError(_('Текст комментария не может быть пустым.'))
        if len(text) > 1000:
            raise forms.ValidationError(_('Текст не должен превышать 1000 символов.'))
        return text


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label=_('Email'))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Пользователь с таким именем уже существует.'))
        return username
