from django import forms
from django.forms import ModelForm
from .models import Book, Comment, Rating


class BookForm(ModelForm):
    # OPTIONAL comment and rating fields
    comment_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Add a Comment (optional)"
    )

    rating_value = forms.ChoiceField(
        required=False,
        choices=[('', '--- Select ---'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        label="Rate this Book (optional)"
    )

    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',
        ]
