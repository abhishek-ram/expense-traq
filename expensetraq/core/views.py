# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from expensetraq.core.utils import user_in_groups


# @method_decorator(user_in_groups(['ExpenseAdmin']), name='dispatch')
class Index(TemplateView):
    template_name = 'core/index.html'
