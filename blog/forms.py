from django import forms
from .models import Post, Tag


class AdminForm(forms.Form):
    login_field = forms.CharField(label='Login', max_length=100)
    password = forms.CharField(label='Password',
                               max_length=100,
                               widget=forms.PasswordInput
                               )


class CreateForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    post_text = forms.CharField(
        widget=forms.Textarea
    )
    queryset = Tag.objects.all()
#     tags = forms.ModelMultipleChoiceField(
#         queryset=Tag.objects.all(),
#         widget=forms.CheckboxSelectMultiple()
#     )


class TagForm(forms.Form):
    title = forms.CharField(label='Tag', max_length=30)
    url = forms.CharField(label='Tag url', max_length=30)


class SearchForm(forms.Form):
    search = forms.CharField(label='Tag', max_length=30,
                             widget=forms.TextInput(attrs={
                                 'class': 'search_text',
                             }))


class CommentForm(forms.Form):
    author = forms.CharField(label='Author', max_length=100)
    email = forms.EmailField(
        label='Email',
        max_length=50,
    )
    comment_text = forms.CharField(
        widget=forms.Textarea
    )
