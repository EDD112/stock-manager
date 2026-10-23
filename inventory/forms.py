from django import forms
from .models import Product, Category, CategoryType, ProductBatch


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'quantity', 'expiry_date']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name', 'required': 'required'}),
            'category':    forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'quantity':    forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Enter quantity', 'required': 'required'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.initial['quantity'] = ''
            self.fields['quantity'].initial = None

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Product name is required.')
        return name

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('Please select a category.')
        return category

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity == '':
            raise forms.ValidationError('Quantity is required.')
        if quantity <= 0:
            raise forms.ValidationError('Quantity must be at least 1.')
        return quantity

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if not expiry_date:
            raise forms.ValidationError('Expiry date is required.')
        return expiry_date


class AddBatchForm(forms.Form):
    """Form for adding a new stock batch (FIFO-aware, creates separate batch entry)."""
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'e.g. 50'})
    )
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    notes = forms.CharField(
        required=False, max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'})
    )


class RemoveStockForm(forms.Form):
    """Form for removing stock using FIFO deduction across batches."""
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Quantity to remove'})
    )
    notes = forms.CharField(
        required=False, max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'})
    )


class StockMovementForm(forms.Form):
    ACTION_CHOICES = (('ADD', 'Add Stock'), ('REMOVE', 'Remove Stock'))
    action   = forms.ChoiceField(choices=ACTION_CHOICES,
                                 widget=forms.Select(attrs={'class': 'form-control'}))
    quantity = forms.IntegerField(min_value=1,
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}))
    notes    = forms.CharField(required=False, max_length=255,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Optional notes'}))


class BatchEditForm(forms.Form):
    """Form for editing a specific batch's quantity and expiry date."""
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Enter quantity',
            'required': 'required',
        })
    )
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required',
        })
    )

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0:
            raise forms.ValidationError('Quantity must be at least 1.')
        return quantity

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        if not expiry_date:
            raise forms.ValidationError('Expiry date is required.')
        return expiry_date


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'description']
        widgets = {
            'name':          forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder': 'e.g. Soft Drinks',
                                                    'required': 'required'}),
            'category_type': forms.Select(attrs={'class': 'form-control', 'id': 'id_category_type',
                                                 'required': 'required'}),
            'description':   forms.TextInput(attrs={'class': 'form-control',
                                                    'placeholder': 'Optional description'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Category name is required.')
        return name

    def clean_category_type(self):
        category_type = self.cleaned_data.get('category_type')
        if not category_type:
            raise forms.ValidationError('Please select a category type.')
        return category_type


class CategoryTypeForm(forms.ModelForm):
    class Meta:
        model = CategoryType
        fields = ['name', 'color', 'icon']
        widgets = {
            'name':  forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'e.g. Seafood, Organic, Hot Food...'}),
            'color': forms.Select(attrs={'class': 'form-control', 'id': 'id_color'}),
            'icon':  forms.Select(attrs={'class': 'form-control', 'id': 'id_icon'}),
        }
