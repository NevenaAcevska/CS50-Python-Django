# forms.py
from django import forms
from .models import Listing


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category','end_time']
