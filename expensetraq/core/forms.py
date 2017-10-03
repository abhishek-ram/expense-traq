from django import forms
from expensetraq.core.models import Salesman, User, ExpenseLine, Expense,\
    SalesmanExpenseType, Region
from django.core.files.uploadedfile import InMemoryUploadedFile
from wand.image import Image
from io import BytesIO
import os


class SalesmanForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalesmanForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(
            groups__name__in=['Expense-User'])
        self.fields['manager'].queryset = User.objects.filter(
            groups__name__in=['Expense-Manager'])

    class Meta:
        model = Salesman
        fields = '__all__'


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['transaction_date', 'paid_by', 'notes', 'receipt', 'salesman']

    receipt = forms.FileField(required=False)

    def clean_receipt(self):
        uploaded_file = self.cleaned_data['receipt']
        if uploaded_file:
            formatted_file = BytesIO()
            formatted_file.name = uploaded_file.name
            name, ext = os.path.splitext(uploaded_file.name)

            if ext in ['.pdf', '.PDF']:
                with Image(file=uploaded_file, resolution=200) as pdf:
                    uploaded_file.name = '%s.png' % name
                    pages = len(pdf.sequence)
                    image = Image(
                        width=pdf.width,
                        height=pdf.height * pages
                    )
                    for i in range(pages):
                        image.composite(
                            pdf.sequence[i],
                            top=pdf.height * i,
                            left=0
                        )
                    uploaded_file.name = '%s.jpg' % name
                    image.format = 'png'
                    # image.resize(1024, 768)
                    image.save(formatted_file)
            else:
                with Image(file=uploaded_file) as img:
                    img.resize(1024, 768)
                    img.save(formatted_file)

            uploaded_file.file = formatted_file

            return InMemoryUploadedFile(
                file=formatted_file,
                field_name='receipt',
                name=uploaded_file.name,
                content_type=uploaded_file.content_type,
                size=formatted_file.tell(),
                charset=uploaded_file.charset
            )
        else:
            return uploaded_file


class ExpenseLineForm(forms.ModelForm):
    region = forms.ChoiceField()

    def clean(self):
        cleaned_data = super(ExpenseLineForm, self).clean()
        expense_limit = self.salesman.expense_limits.filter(
            expense_type=cleaned_data.get('expense_type')).first()
        if expense_limit \
                and cleaned_data.get('amount', 0) > expense_limit.limit:
            self.add_error('amount', 'Amount exceeds the Expense limit')
        if cleaned_data.get('expense_type') \
                and not self.user_is_admin \
                and cleaned_data['expense_type'].expense_type.receipt_required \
                and not cleaned_data['expense'].receipt:
            self.add_error('expense_type',
                           'Receipt is required for this expense type')

    def __init__(self, salesman, user_is_admin, *args, **kwargs):
        super(ExpenseLineForm, self).__init__(*args, **kwargs)
        self.salesman = salesman
        self.user_is_admin = user_is_admin
        self.fields['expense_type'].queryset = SalesmanExpenseType.objects.\
            filter(salesman=salesman).\
            exclude(expense_type__name__in=['Daily Expense'])
        regions = {}
        for et in self.fields['expense_type'].queryset:
            regions[et.region.id] = et.region.name

        self.fields['region'].choices = [('', '----------')] + \
                                        list(regions.items())
        if self.instance.id:
            self.fields['region'].initial = self.instance.expense_type.region_id

    class Meta:
        model = ExpenseLine
        fields = ['region', 'expense_type', 'amount']


class ExpenseApprovalForm(forms.Form):
    expense_list = forms.ModelMultipleChoiceField(
        queryset=Expense.objects.all())
    approved = forms.NullBooleanField()


class DailyExpenseForm(forms.Form):
    WORKED_CHOICES = (
        ('Full', 'Full Day'),
        ('Half', 'Half Day'),
        ('Quart', 'Quarter Day'),
    )
    transaction_date = forms.DateField()
    expense_type = forms.ModelChoiceField(
        queryset=SalesmanExpenseType.objects.all(),
        empty_label=None,
        required=True
    )
    worked = forms.ChoiceField(choices=WORKED_CHOICES)

    def __init__(self, salesman, *args, **kwargs):
        super(DailyExpenseForm, self).__init__(*args, **kwargs)
        self.salesman = salesman
        self.fields['expense_type'].queryset = SalesmanExpenseType.objects. \
            filter(salesman=salesman, expense_type__name__in=['Daily Expense'])
