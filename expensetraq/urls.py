"""expensetraq URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout
from expensetraq.core import views

urlpatterns = [
    # Django admin urls
    url(r'^admin/', admin.site.urls),

    # ExpenseTraQ urls
    url(r'^index/$', login_required(views.Index.as_view()), name='index'),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, {'next_page': '/index/'}, name='logout'),
    url(r'^expense-types/$',
        login_required(views.ExpenseTypeList.as_view()),
        name='expense-type-list'),
    url(r'^expense-type/add/$',
        login_required(views.ExpenseTypeCreate.as_view()),
        name='expense-type-add'),
    url(r'expense-type/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseTypeUpdate.as_view()),
        name='expense-type-update'),
    url(r'expense-type/(?P<pk>[0-9]+)/delete/$',
        login_required(views.ExpenseTypeDelete.as_view()),
        name='expense-type-delete'),
    url(r'^salesmen/$',
        login_required(views.SalesmanList.as_view()),
        name='salesman-list'),
    url(r'^salesman/add/$',
        login_required(views.SalesmanCreate.as_view()),
        name='salesman-add'),
    url(r'salesman/(?P<pk>[0-9]+)/$',
        login_required(views.SalesmanUpdate.as_view()),
        name='salesman-update'),
    url(r'^expense-limits/$',
        login_required(views.ExpenseLimitList.as_view()),
        name='expense-limit-list'),
    url(r'^expense-limit/add/$',
        login_required(views.ExpenseLimitCreate.as_view()),
        name='expense-limit-add'),
    url(r'expense-limit/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseLimitUpdate.as_view()),
        name='expense-limit-update'),
    url(r'expense-limit/(?P<pk>[0-9]+)/delete/$',
        login_required(views.ExpenseLimitDelete.as_view()),
        name='expense-limit-delete'),
    url(r'^expenses/$',
        login_required(views.ExpenseList.as_view()),
        name='expense-list'),
    url(r'^expense/add/$',
        login_required(views.ExpenseCreate.as_view()),
        name='expense-add'),
    url(r'expense/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseUpdate.as_view()),
        name='expense-update'),
    url(r'^.*', login_required(views.Index.as_view())),
]
