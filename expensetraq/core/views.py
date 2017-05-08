# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, ListView, CreateView, \
    UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from expensetraq.core.utils import user_in_groups, DeleteMessageMixin
from expensetraq.core.models import Expense, ExpenseType


class Index(TemplateView):
    template_name = 'core/index.html'


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseTypeList(ListView):
    model = ExpenseType


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseTypeCreate(SuccessMessageMixin, CreateView):
    model = ExpenseType
    fields = '__all__'
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been created successfully'


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseTypeUpdate(SuccessMessageMixin, UpdateView):
    model = ExpenseType
    fields = '__all__'
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been edited successfully'


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseTypeDelete(DeleteMessageMixin, DeleteView):
    model = ExpenseType
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been deleted successfully'


class ExpenseList(ListView):
    model = Expense


@method_decorator(user_in_groups(['ExpenseSalesman']), name='dispatch')
class ExpenseCreate(SuccessMessageMixin, CreateView):
    model = Expense
    fields = [
        'expense_type', 'amount', 'transaction_date', 'paid_by', 'notes',
        'receipt'
    ]
    success_url = reverse_lazy('expense-list')
    success_message = 'Expense $%(amount)s of type "%(expense_type)s"' \
                      'has been created successfully'

    def form_valid(self, form):
        form.instance.salesman = self.request.user
        return super(ExpenseCreate, self).form_valid(form)


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseUpdate(SuccessMessageMixin, UpdateView):
    model = Expense
    fields = [
        'expense_type', 'amount', 'transaction_date', 'paid_by', 'notes']
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been edited successfully'
