from django.core.management.base import BaseCommand
from expensetraq.core.models import RecurringExpense, Expense, ExpenseLine
from django.db import transaction
import logging
import maya
logger = logging.getLogger('expensetraq')


class Command(BaseCommand):
    help = 'Add recurring expenses for salesmen'

    @transaction.atomic
    def handle(self, *args, **options):
        # Loop through all the recurring expenses in the system
        for recur_expense in RecurringExpense.objects.all():
            # If today is the day of the recurring expense then create it
            if recur_expense.day_of_month == maya.now().day:
                expense = Expense.objects.create(
                    salesman=recur_expense.salesman,
                    transaction_date=maya.now().datetime().date(),
                    status='P',
                    paid_by='Employee Paid',
                    notes='Recurring Expense Auto created by system'
                )
                ExpenseLine.objects.create(
                    expense=expense,
                    expense_type=recur_expense.expense_type,
                    amount=recur_expense.amount
                )
                logger.info(
                    'Recurring Expense {} for {} created for '
                    'salesman {}'.format(recur_expense.expense_type,
                                         recur_expense.amount,
                                         recur_expense.salesman))

