# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
from localflavor.us import models as us_models
from ast import literal_eval


class ExpenseType(TimeStampedModel, models.Model):
    name = models.CharField(max_length=30)
    receipt_required = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExpenseTypeCode(models.Model):
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE, related_name='gl_codes')
    region = us_models.USStateField()
    gl_code = models.CharField(max_length=30, verbose_name='GL Code')


def receipt_directory_path(instance, filename):
    return 'expense_receipts/{0}/{1}'.format(instance.salesman.id, filename)


class Salesman(TimeStampedModel, models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='salesman',
        error_messages={'unique': 'Salesman already on-boarded.'})
    regions = models.TextField()
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='team', null=True)

    def __str__(self):
        return str(self.user)

    @property
    def region_list(self):
        return literal_eval(self.regions)


class ExpenseLimit(TimeStampedModel, models.Model):
    salesman = models.ForeignKey(
        Salesman, on_delete=models.CASCADE, related_name='expense_limits')
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=14, decimal_places=2)


class RecurringExpense(TimeStampedModel, models.Model):
    salesman = models.ForeignKey(
        Salesman, on_delete=models.CASCADE, related_name='recur_expenses')
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE)
    day_of_month = models.IntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)


class Expense(TimeStampedModel, models.Model):
    PAID_BY_CHOICES = (
        ('E', 'Employee Paid'),
        ('C', 'Company Paid'),
    )
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('D', 'Denied'),
    )

    salesman = models.ForeignKey(
        Salesman, on_delete=models.CASCADE, related_name='expenses')
    transaction_date = models.DateField()
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default='P')
    paid_by = models.CharField(
        max_length=2, choices=PAID_BY_CHOICES, default='E')
    notes = models.TextField(null=True, blank=True)
    receipt = models.ImageField(
        upload_to=receipt_directory_path, null=True, blank=True)

    @property
    def total_amount(self):
        return sum([l.amount for l in self.lines.all()])

    @property
    def expense_types(self):
        return '|'.join([l.expense_type.name for l in self.lines.all()])


class ExpenseLine(TimeStampedModel, models.Model):
    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name='lines')
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    region = us_models.USStateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
