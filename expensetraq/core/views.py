# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expensetraq.core.utils import user_in_groups


@login_required()
@user_in_groups(['ExpenseAdmin'])
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
