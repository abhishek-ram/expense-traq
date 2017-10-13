from django.core.management.base import BaseCommand
from django.urls import reverse_lazy
from django.db import transaction
from django.conf import settings
from django.utils.http import urlencode
from django.core.mail import EmailMessage
from expensetraq.core.models import User
from expensetraq.core.utils import generate_expense_report
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from django.utils import timezone
from datetime import timedelta
import logging
logger = logging.getLogger('expensetraq')


class Command(BaseCommand):
    help = 'Email Weekly Expense Reports to Managers'

    @transaction.atomic
    def handle(self, *args, **options):
        to_date = timezone.localtime(timezone.now()).date() - timedelta(days=1)
        from_date = to_date - timedelta(days=6)
        date_range = '{} - {}'.format(
            from_date.strftime('%Y-%m-%d'),
            to_date.strftime('%Y-%m-%d'),
        )

        # Send the report to each manager registered on the System
        logger.info('Begin weekly email job, looping through the managers')
        for user in User.objects.all():
            if user.is_manager and user.email and user.team.exists():
                logger.info(
                    "Generating reports of team for manager %s" % user)
                reports_zip_stream = BytesIO()
                reports_zip = ZipFile(
                    reports_zip_stream, mode='w', compression=ZIP_DEFLATED)
                for salesman in user.team.all():
                    logger.info("Generating report for salesman %s" % salesman)
                    weekly_expenses = salesman.expenses.\
                        filter(status__in=['P', 'A']).\
                        filter(transaction_date__gte=from_date).\
                        filter(transaction_date__lte=to_date)

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
                    reports_zip.writestr(
                        'ExpenseReport_%s_%s.pdf' % (salesman, date_range),
                        generate_expense_report(
                            salesman, date_range, expense_list, 'pdf')
                    )

                reports_zip.close()
                report_url = '{}{}?{}'.format(
                    'http://127.0.0.1:8000' if settings.DEBUG else 'https://expenses.cevmultimedia.com',
                    reverse_lazy('expense-list-export'),
                    urlencode({
                        'action': 'list',
                        'salesman[]': [s.id for s in user.team.all()],
                        'status[]': ['P', 'A'],
                        'daterange': date_range
                    }, True)
                )

                # Send the report email to the manager
                logger.info(
                    "Emailing all reports of team to manager %s" % user)
                email_body = 'Hi %s, \n\n' % user
                email_body += 'Attached is the weekly reports of pending and ' \
                              'approved expenses of everyone you ' \
                              'manage for %s\n\n' % date_range
                email_body += 'You can view the report online at %s \n\n' % report_url

                report_email = EmailMessage(
                    subject='Weekly Expenses Report',
                    body=email_body,
                    to=[user.email],
                )
                report_email.attach(
                    'ExpenseReports_%s.zip' % date_range,
                    reports_zip_stream.getvalue(),
                    'application/x-zip-compressed'
                )
                report_email.send(fail_silently=False)
