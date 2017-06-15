from django import forms
from expensetraq.core.models import Salesman, User, ExpenseLine, ExpenseLimit
from localflavor.us.models import STATE_CHOICES


class SalesmanForm(forms.ModelForm):
    regions = forms.MultipleChoiceField(choices=STATE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(SalesmanForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(
            groups__name__in=['Expense-User'])
        self.fields['manager'].queryset = User.objects.filter(
            groups__name__in=['Expense-Manager'])

    class Meta:
        model = Salesman
        fields = '__all__'


class ExpenseLineForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ExpenseLineForm, self).clean()
        expense_limit = self.salesman.expense_limits.filter(
            expense_type=cleaned_data.get('expense_type')).first()
        if expense_limit \
                and cleaned_data.get('amount', 0) > expense_limit.limit:
            self.add_error('amount', 'Amount exceeds the Expense limit')
        if cleaned_data.get('expense_type') \
                and cleaned_data['expense_type'].receipt_required \
                and not cleaned_data['expense'].receipt:
            self.add_error('expense_type',
                           'Receipt is required for this expense type')

    def __init__(self, salesman, *args, **kwargs):
        super(ExpenseLineForm, self).__init__(*args, **kwargs)
        self.salesman = salesman
        region_dict = dict(STATE_CHOICES)
        region_choices = [
            (r, region_dict[r]) for r in salesman.region_list]
        self.fields['region'].choices = [('', '---------')] + region_choices

    class Meta:
        model = ExpenseLine
        fields = ['expense_type', 'region', 'amount']


class ExpenseReportForm(forms.Form):
    salesman = forms.ModelChoiceField(
        queryset=Salesman.objects.all(), empty_label='')
