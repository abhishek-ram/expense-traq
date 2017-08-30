# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.utils import timezone
from localflavor.us import models as us_models
from ast import literal_eval
from django.contrib.auth.models import AbstractUser
import humanize


class User(AbstractUser):

    @property
    def user_groups(self):
        return {g.name for g in self.groups.all()}

    @property
    def is_admin(self):
        if 'Expense-Admin' in self.user_groups:
            return True
        else:
            return False

    @property
    def is_manager(self):
        if 'Expense-Manager' in self.user_groups:
            return True
        else:
            return False

    @property
    def is_salesman(self):
        if 'Expense-User' in self.user_groups:
            return True
        else:
            return False

    class Meta:
        db_table = 'auth_user'


class ExpenseType(TimeStampedModel, models.Model):
    name = models.CharField(max_length=100)
    receipt_required = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExpenseTypeCode(models.Model):
    expense_type = models.ForeignKey(
        ExpenseType, on_delete=models.CASCADE, related_name='gl_codes')
    region = us_models.USStateField()
    gl_code = models.CharField(max_length=30, verbose_name='GL Code')


def receipt_directory_path(instance, filename):
    return 'expense_receipts/{0}/{1}'.format(
        instance.transaction_date.strftime('%Y%m%d'), filename)


class CompanyCard(TimeStampedModel, models.Model):
    name = models.CharField(max_length=100)
    gp_vendor_code = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Salesman(TimeStampedModel, models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='salesman',
        error_messages={'unique': 'Salesman already on-boarded.'})
    regions = models.TextField()
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='team', null=True)
    company_cards = models.ManyToManyField(CompanyCard, blank=True)
    gp_vendor_code = models.CharField(max_length=100)
    daily_expense = models.DecimalField(
        max_digits=14, decimal_places=2, default=0)

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
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    day_of_month = models.IntegerField(
        choices=zip(range(1, 31), range(1, 31)))


class Expense(TimeStampedModel, models.Model):
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
    paid_by = models.CharField(max_length=100)
    notes = models.TextField(null=True, blank=True)
    receipt = models.ImageField(
        upload_to=receipt_directory_path, null=True, blank=True)
    pushed_to_gp = models.BooleanField(default=False)

    class Meta:
        ordering = ('-salesman', '-transaction_date', '-created')

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


class Notification(TimeStampedModel, models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    text = models.TextField()
    is_read = models.BooleanField(default=False)

    @property
    def created_slang(self):
        diff_time = timezone.now() - self.created
        if diff_time.days == 0:
            return humanize.naturaltime(timezone.make_naive(self.created))
        else:
            return humanize.naturaldate(timezone.make_naive(self.created))

    def mark_read(self):
        self.is_read = True
        self.save()
        return ''
