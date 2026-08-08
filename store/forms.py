from django import forms
from .models import Order
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationPolicy

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5'
        })
    )
    override = forms.BooleanField(
        required=False, 
        initial=False, 
        widget=forms.HiddenInput
    )

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            'address': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            'city': forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
        }



# User registration form
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            "first_name": forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            "last_name": forms.TextInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
            "email": forms.EmailInput(attrs={'class': 'w-full p-2.5 border border-gray-300 rounded-lg'}),
        }

    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password_confirm"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password_confirm"]