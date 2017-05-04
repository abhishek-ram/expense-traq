# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, ListView, CreateView, \
    UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from expensetraq.core.utils import user_in_groups, DeleteMessageMixin
from expensetraq.core.models import Expense, ExpenseType


# @method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class Index(TemplateView):
    template_name = 'core/index.html'


@method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class ExpenseTypeList(ListView):
    model = ExpenseType


class ManageExpenses(ListView):
    model = Expense


class ExpenseTypeCreate(SuccessMessageMixin, CreateView):
    model = ExpenseType
    fields = ['name', 'gl_code', 'receipt_required']
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been created successfully'


class ExpenseTypeUpdate(SuccessMessageMixin, UpdateView):
    model = ExpenseType
    fields = ['name', 'gl_code', 'receipt_required']
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been edited successfully'


class ExpenseTypeDelete(DeleteMessageMixin, DeleteView):
    model = ExpenseType
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been deleted successfully'

