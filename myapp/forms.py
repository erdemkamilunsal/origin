# myapp/forms.py
from django import forms

class YouTubeURLForm(forms.Form):
    youtube_url = forms.URLField(label="Channel ID:")
