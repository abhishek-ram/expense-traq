# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel


class ExpenseType(TimeStampedModel, models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    gl_code = models.CharField(max_length=30, verbose_name='GL Code')
    receipt_required = models.BooleanField(default=True)


def receipt_directory_path(instance, filename):
    return 'expense_receipts/{0}/{1}'.format(instance.salesman.id, filename)


class Expense(TimeStampedModel, models.Model):
    PAID_BY_CHOICES = (
        ('E', 'Employee Paid'),
        ('C', 'Company Paid'),
    )
    STATUS_CHOICES = (
        ('C', 'Created'),
        ('A', 'Approved'),
        ('D', 'Denied'),
    )

    salesman = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    transaction_date = models.DateField()
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default='C')
    paid_by = models.CharField(max_length=2, choices=PAID_BY_CHOICES)
    notes = models.TextField(null=True, blank=True)
    receipt = models.ImageField(
        upload_to=receipt_directory_path, null=True, blank=True)


class ExpenseLimit(TimeStampedModel, models.Model):
    salesman = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='expense_limits')
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=14, decimal_places=2)


class RecurringExpense(TimeStampedModel, models.Model):
    salesman = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recur_expenses')
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE)
    day_of_month = models.IntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
