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
from django.forms import inlineformset_factory
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from expensetraq.core.utils import user_in_groups, DeleteMessageMixin
from expensetraq.core.models import Expense, ExpenseType, ExpenseTypeCode, \
    Salesman, ExpenseLimit, ExpenseLine, RecurringExpense, Notification
from expensetraq.core.forms import SalesmanForm, ExpenseLineForm, \
    ExpenseApprovalForm
import maya


class Index(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        user_groups = {g.name for g in self.request.user.groups.all()}
        limit_date = maya.when(timezone.now().isoformat()).subtract(
            months=3).datetime()
        if 'Expense-User' in user_groups:
            expenses = self.request.user.salesman.expenses.filter(
                transaction_date__gte=limit_date)
            context.update({
                'pending_amt': sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='P')]),
                'approved_amt': sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='A')]),
                'denied_amt': sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='D')]),
            })
        elif 'Expense-Manager' in user_groups:
            team = self.request.user.team.all()
            context.update({
                'team_count': len(team),
                'pending_amt': 0,
                'approved_amt': 0,
                'denied_amt': 0,
            })
            for salesman in team:
                expenses = salesman.expenses.filter(
                    transaction_date__gte=limit_date)
                context['pending_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='P')])
                context['approved_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='A')])
                context['denied_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='D')])
        elif 'Expense-Admin' in user_groups:
            salesmen = Salesman.objects.all()
            context.update({
                'team_count': len(salesmen),
                'pending_amt': 0,
                'approved_amt': 0,
                'denied_amt': 0,
            })
            for salesman in salesmen:
                expenses = salesman.expenses.filter(
                    transaction_date__gte=limit_date)
                context['pending_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='P')])
                context['approved_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='A')])
                context['denied_amt'] += sum([
                    e.lines.all().aggregate(Sum('amount'))['amount__sum']
                    for e in expenses.filter(status='D')])
        return context


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
                    form_kwargs={'salesman': self.request.user.salesman})
                assert formset.is_valid()
                formset.save()
                messages.success(
                    self.request, self.get_success_message(self.object))

                # Create notifications for the admin and manager
                not_message = '{} has added a new expense dated {} for ${}'.format(
                    self.request.user, self.object.transaction_date,
                    self.object.total_amount)
                Notification.objects.create(
                    user=self.request.user.salesman.manager,
                    title='New Expense Created',
                    text=not_message)
                Notification.objects.create(
                    user=User.objects.filter(groups__name__in=['Expense-Admin']).first(),
                    title='New Expense Created',
                    text=not_message)
                return HttpResponseRedirect(self.get_success_url())
        except AssertionError:
            form.instance.id = None
            messages.error(
                self.request, 'Failed to record expense, correct errors and resubmit')
            return self.render_to_response(
                self.get_context_data(form=form, inline_formset=formset))

    def get_success_message(self, obj):
        return self.success_message.format(obj)


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class ExpenseApproval(ListView):
    model = Expense
    form_class = ExpenseApprovalForm
    template_name = 'core/expense_approval.html'

    def get_queryset(self):
        salesman = self.request.GET.get('salesman')
        if salesman:
            return Expense.objects.filter(salesman=salesman, status='P')
        else:
            return Expense.objects.none()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            ap_display = 'Approved' if form.cleaned_data['approved'] else 'Denied'
            if form.cleaned_data['approved']:
                form.cleaned_data['expense_list'].update(status='A')
            else:
                form.cleaned_data['expense_list'].update(status='D')
            messages.success(
                request, 'Selected expenses have been %s' % ap_display)

            # Create notifications for the salesman and manager
            for expense in form.cleaned_data['expense_list']:
                Notification.objects.create(
                    user=expense.salesman.user,
                    title='Expense Updated',
                    text='Admin has {} your expense dated {} for ${}'.format(
                        ap_display, expense.transaction_date, expense.total_amount))
                Notification.objects.create(
                    user=expense.salesman.manager,
                    title='Expense Updated',
                    text='Admin has {} {}\'s expense dated {} for ${}'.format(
                        ap_display, expense.salesman.user,
                        expense.transaction_date, expense.total_amount))

        else:
            messages.error(
                request, 'Unable to update expenses, please contact Admin')
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'Expense-Manager' in \
                {g.name for g in self.request.user.groups.all()}:
            kwargs['salesman_list'] = self.request.user.team.objects.all()
        else:
            kwargs['salesman_list'] = Salesman.objects.all()
        kwargs['sel_salesman'] = int(self.request.GET.get('salesman', 0))
        return super(ExpenseApproval, self).get_context_data(**kwargs)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            # 'initial': self.get_initial(),
            # 'prefix': self.get_prefix(),
            # 'user': self.request.user,
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
    success_url = reverse_lazy('expense-approval')
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


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class RecurringExpenseList(ListView):
    model = RecurringExpense


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class RecurringExpenseCreate(SuccessMessageMixin, CreateView):
    model = RecurringExpense
    fields = '__all__'
    success_url = reverse_lazy('recur-expense-list')
    success_message = 'Recurring Expense for <var>%(salesman)s</var> has ' \
                      'been added successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class RecurringExpenseUpdate(SuccessMessageMixin, UpdateView):
    model = RecurringExpense
    fields = '__all__'
    success_url = reverse_lazy('recur-expense-list')
    success_message = 'Recurring Expense for <var>%(salesman)s</var> has ' \
                      'been edited successfully'


@method_decorator(user_in_groups(['Expense-Admin']), name='dispatch')
class RecurringExpenseDelete(DeleteMessageMixin, DeleteView):
    model = RecurringExpense
    success_url = reverse_lazy('recur-expense-list')
    success_message = 'Recurring Expense <var>%(id)s</var> has been deleted ' \
                      'successfully'


class NotificationList(ListView):
    model = Notification

    def get_queryset(self):
        return self.request.user.notifications.all()
