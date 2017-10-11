from django.core.management.base import BaseCommand
from django.urls import reverse_lazy
from django.db import transaction
from django.conf import settings
from django.utils.http import urlencode
from expensetraq.core.models import User
from expensetraq.core.utils import generate_expense_report
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

        # Send the report to each manager registered on the System
        logger.info('Begin weekly email job, looping through the managers')
        for user in User.objects.all():
            if user.is_manager and user.email:
                logger.info(
                    "Generating reports for all salesman under manager %s" % user)
                expense_reports = []
                for salesman in user.team.all():
                    logger.info("Generating report for salesman %s" % salesman)
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

                    report_pdf = generate_expense_report(
                        salesman, date_range, expense_list, 'pdf')
                    report_fn = 'ExpenseReport_%s_%s.xlsx' % (salesman, date_range)
                    report_url = '{}{}?{}'.format(
                        'http://127.0.0.1:8000' if settings.DEBUG else 'https://expenses.cevmultimedia.com',
                        reverse_lazy('expense-list-export'),
                        urlencode({
                            'action': 'list',
                            'salesman[]': salesman.id,
                            'daterange': date_range
                        })
                    )
                    expense_reports.append(
                        (str(salesman), report_url, report_fn))

                print(expense_reports)
