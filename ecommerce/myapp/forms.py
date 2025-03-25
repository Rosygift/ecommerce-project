from typing import Any
from django import forms
from.models import CustomUser 
from.models import ShippingAddress
from.models import Wishlist


class RegistrationForm(forms.ModelForm):
    password =forms.CharField(widget=forms.PasswordInput)
    confirm_password =forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model =CustomUser
        fields =['email','first_name','password']

    def clean(self):
       cleaned_data=super().clean()
       password = cleaned_data.get('password')
       confirm_password = cleaned_data.get('confirm_password')
       if password != confirm_password:
           raise forms.ValidationError('password does not match')
       
class SearchForm(forms.Form):
    query = forms.CharField(label='search',max_length=100)

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress  # Use 'model' instead of 'models'
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']  



class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['products']  # This matches the field in the Wishlist model
        widgets = {
            'products': forms.CheckboxSelectMultiple,
        }
