# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView, ListView, CreateView, \
    UpdateView, DeleteView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db import transaction
from expensetraq.core.utils import user_in_groups, DeleteMessageMixin
from expensetraq.core.models import Expense, ExpenseType, ExpenseTypeCode, \
    Salesman, ExpenseLimit, ExpenseLine
from expensetraq.core.forms import SalesmanForm, ExpenseLineForm, \
    ExpenseReportForm
from django.forms import inlineformset_factory


class Index(TemplateView):
    template_name = 'core/index.html'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseTypeList(ListView):
    model = ExpenseType


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseTypeCreate(CreateView):
    model = ExpenseType
    fields = '__all__'
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been created successfully'
    ETCFormSet = inlineformset_factory(
        ExpenseType, ExpenseTypeCode, extra=2, can_delete=False,
        fields=['region', 'gl_code'])

    def get_context_data(self, **kwargs):
        context = super(ExpenseTypeCreate, self).get_context_data(**kwargs)
        if not context.get('inline_formset'):
            context['inline_formset'] = self.ETCFormSet()
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save()
                formset = self.ETCFormSet(
                    self.request.POST, instance=self.object)
                assert formset.is_valid()
                formset.save()
                messages.success(self.request,
                                 self.get_success_message(form.cleaned_data))
                return HttpResponseRedirect(self.get_success_url())
        except AssertionError:
            messages.error(
                self.request, 'Failed to save Expense type, Errors are '
                              '{}'.format(formset.errors[0].as_ul())
            )
            return self.render_to_response(
                self.get_context_data(form=form, inline_formset=formset))

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseTypeUpdate(UpdateView):
    model = ExpenseType
    fields = '__all__'
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been edited successfully'
    ETCFormSet = inlineformset_factory(
        ExpenseType, ExpenseTypeCode, extra=2, fields=['region', 'gl_code'])

    def get_context_data(self, **kwargs):
        context = super(ExpenseTypeUpdate, self).get_context_data(**kwargs)
        if not context.get('inline_formset'):
            context['inline_formset'] = self.ETCFormSet(
                instance=context['form'].instance)
        return context

    def form_valid(self, form):
        self.object = form.save()
        formset = self.ETCFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            messages.success(
                self.request, self.get_success_message(form.cleaned_data))
            return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(
                self.request, 'Failed to save Expense type, Errors are '
                              '{}'.format(formset.errors[0].as_ul())
            )
            return self.render_to_response(
                self.get_context_data(form=form, inline_formset=formset))

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseTypeDelete(DeleteMessageMixin, DeleteView):
    model = ExpenseType
    success_url = reverse_lazy('expense-type-list')
    success_message = 'Expense Type "%(name)s" has been deleted successfully'


@method_decorator(user_in_groups(['Expense-User']), name='dispatch')
class ExpenseList(ListView):
    model = Expense

    def get_queryset(self):
        return Expense.objects.filter(salesman=self.request.user.salesman)


@method_decorator(user_in_groups(['Expense-User']), name='dispatch')
class ExpenseCreate(CreateView):
    model = Expense
    fields = ['transaction_date', 'paid_by', 'notes', 'receipt']
    success_url = reverse_lazy('expense-list')
    success_message = 'Expense with total ${0.total_amount} has ' \
                      'been recorded successfully'
    ExpenseFormSet = inlineformset_factory(
        Expense, ExpenseLine, extra=4, min_num=1, can_delete=False,
        validate_min=True, form=ExpenseLineForm)

    def get_context_data(self, **kwargs):
        context = super(ExpenseCreate, self).get_context_data(**kwargs)
        if not context.get('inline_formset'):
            context['inline_formset'] = self.ExpenseFormSet(
                form_kwargs={'salesman': self.request.user.salesman})
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.instance.salesman = self.request.user.salesman
                self.object = form.save()
                formset = self.ExpenseFormSet(
                    self.request.POST, instance=self.object,
                    form_kwargs={'request': self.request})
                assert formset.is_valid()
                formset.save()
                messages.success(self.request,
                                 self.get_success_message(self.object))
                return HttpResponseRedirect(self.get_success_url())
        except AssertionError:
            form.instance.id = None
            messages.error(
                self.request,
                'Failed to record expense, correct errors and resubmit')
            return self.render_to_response(
                self.get_context_data(form=form, inline_formset=formset))

    def get_success_message(self, obj):
        return self.success_message.format(obj)


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseReport(ListView):
    model = Expense
    form_class = ExpenseReportForm
    template_name = 'core/expense_report.html'

    def get_queryset(self):
        form = self.get_form()
        self.salesman = None
        if form.is_valid():
            self.salesman = form.cleaned_data['salesman']
            return Expense.objects.filter(
                salesman=form.cleaned_data['salesman'])
        else:
            return Expense.objects.none()

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
            kwargs['salesman'] = self.salesman
        return super(ExpenseReport, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            # 'initial': self.get_initial(),
            # 'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        else:
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseUpdate(UpdateView):
    model = Expense
    fields = ['transaction_date', 'paid_by', 'notes']
    success_url = reverse_lazy('expense-report')
    success_message = 'Expense "{0.pk}" has been edited successfully'

    ExpenseFormSet = inlineformset_factory(
        Expense, ExpenseLine,max_num=5, can_delete=False, form=ExpenseLineForm)

    def get_context_data(self, **kwargs):
        context = super(ExpenseUpdate, self).get_context_data(**kwargs)
        if not context.get('inline_formset'):
            context['inline_formset'] = self.ExpenseFormSet(
                form_kwargs={'salesman': context['form'].instance.salesman},
                instance=context['form'].instance)
        return context

    def form_valid(self, form):
        try:
            self.object = form.save()
            formset = self.ExpenseFormSet(
                self.request.POST, instance=self.object,
                form_kwargs={'salesman': self.object.salesman})
            assert formset.is_valid()
            formset.save()
            messages.success(self.request,
                             self.get_success_message(self.object))
            return HttpResponseRedirect('%s?salesman=%s' % (
                self.get_success_url(), self.object.salesman.id))
        except AssertionError:
            messages.error(
                self.request,
                'Failed to record expense, correct errors and resubmit')
            return self.render_to_response(
                self.get_context_data(form=form, inline_formset=formset))

    def get_success_message(self, obj):
        return self.success_message.format(obj)


class ExpenseDetail(DetailView):
    model = Expense


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class SalesmanList(ListView):
    model = Salesman


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class SalesmanCreate(SuccessMessageMixin, CreateView):
    model = Salesman
    form_class = SalesmanForm
    success_url = reverse_lazy('salesman-list')
    success_message = 'Salesman "%(user)s" has been added successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class SalesmanUpdate(SuccessMessageMixin, UpdateView):
    model = Salesman
    form_class = SalesmanForm
    success_url = reverse_lazy('salesman-list')
    success_message = 'Salesman "%(user)s" has been edited successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseLimitList(ListView):
    model = ExpenseLimit


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseLimitCreate(SuccessMessageMixin, CreateView):
    model = ExpenseLimit
    fields = '__all__'
    success_url = reverse_lazy('expense-limit-list')
    success_message = 'Expense limit for <var>%(salesman)s</var> has been ' \
                      'added successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseLimitUpdate(SuccessMessageMixin, UpdateView):
    model = ExpenseLimit
    fields = '__all__'
    success_url = reverse_lazy('expense-limit-list')
    success_message = 'Expense limit for <var>%(salesman)s</var> has been ' \
                      'edited successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseLimitDelete(DeleteMessageMixin, DeleteView):
    model = ExpenseLimit
    success_url = reverse_lazy('expense-limit-list')
    success_message = 'Expense Type <var>%(id)s</var> has been deleted ' \
                      'successfully'
