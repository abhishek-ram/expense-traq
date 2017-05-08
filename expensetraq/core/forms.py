from django import forms
from expensetraq.core.models import Salesman, User
from localflavor.us.models import STATE_CHOICES


class SalesmanForm(forms.ModelForm):
    regions = forms.MultipleChoiceField(choices=STATE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(SalesmanForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(
            groups__name__in=['ExpenseSalesman'])
        self.fields['manager'].queryset = User.objects.filter(
            groups__name__in=['ExpenseManager'])

    class Meta:
        model = Salesman
        fields = '__all__'
