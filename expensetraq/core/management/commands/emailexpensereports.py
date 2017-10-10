from django.core.management.base import BaseCommand
from expensetraq.core.models import Salesman, Expense, ExpenseLine
from expensetraq.core.utils import generate_expense_report
from django.db import transaction
import logging
import maya
logger = logging.getLogger('expensetraq')


class Command(BaseCommand):
    help = 'Email Weekly Expense Reports to Managers'

    @transaction.atomic
    def handle(self, *args, **options):
        to_date = maya.now()
        from_date = to_date.subtract(days=7)
        date_range = '{} - {}'.format(
            from_date.datetime().strftime('%Y-%m-%d'),
            to_date.datetime().strftime('%Y-%m-%d'),
        )
        salesman = Salesman.objects.get(user__username='salesman3')
        weekly_expenses = salesman.expenses.\
            filter(transaction_date__gte=from_date.datetime().date()).\
            filter(transaction_date__lte=to_date.datetime().date())

        expense_list = {}
        for expense in weekly_expenses:
            if not expense_list.get(expense.paid_by):
                expense_list[expense.paid_by] = {
                    'total': {}
                }

            trans_date = expense.transaction_date.strftime('%Y-%m-%d')
            for line in expense.lines.all():
                e_type = str(line.expense_type)

                if not expense_list[expense.paid_by].get(e_type):
                    expense_list[expense.paid_by][e_type] = {}

                if not expense_list[expense.paid_by][e_type].get(trans_date):
                    expense_list[expense.paid_by][e_type][trans_date] = 0

                if not expense_list[expense.paid_by]['total'].get(trans_date):
                    expense_list[expense.paid_by]['total'][trans_date] = 0

                expense_list[
                    expense.paid_by][e_type][trans_date] += line.amount
                expense_list[
                    expense.paid_by]['total'][trans_date] += line.amount

        expense_report = generate_expense_report(
            salesman, date_range, expense_list, 'pdf')
