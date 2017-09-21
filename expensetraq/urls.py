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
from django.conf import settings
from django.conf.urls.static import static

media_url = []
if settings.DEBUG:
    media_url = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = media_url + [
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
    url(r'^expense-type/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseTypeUpdate.as_view()),
        name='expense-type-update'),
    url(r'^expense-type/(?P<pk>[0-9]+)/delete/$',
        login_required(views.ExpenseTypeDelete.as_view()),
        name='expense-type-delete'),
    url(r'^salesmen/$',
        login_required(views.SalesmanList.as_view()),
        name='salesman-list'),
    url(r'^salesman/add/$',
        login_required(views.SalesmanCreate.as_view()),
        name='salesman-add'),
    url(r'^salesman/(?P<pk>[0-9]+)/$',
        login_required(views.SalesmanUpdate.as_view()),
        name='salesman-update'),
    url(r'^salesman/(?P<salesman_id>[0-9]+)/expense-types/$',
        login_required(views.SalesmanExpenseTypeList.as_view()),
        name='salesman-expense-types'),
    url(r'^expense-limits/$',
        login_required(views.ExpenseLimitList.as_view()),
        name='expense-limit-list'),
    url(r'^expense-limit/add/$',
        login_required(views.ExpenseLimitCreate.as_view()),
        name='expense-limit-add'),
    url(r'^expense-limit/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseLimitUpdate.as_view()),
        name='expense-limit-update'),
    url(r'^expense-limit/(?P<pk>[0-9]+)/delete/$',
        login_required(views.ExpenseLimitDelete.as_view()),
        name='expense-limit-delete'),
    url(r'^expense/list/$',
        login_required(views.ExpenseListExport.as_view()),
        name='expense-list-export'),
    url(r'^expense/add/$',
        login_required(views.ExpenseCreate.as_view()),
        name='expense-add'),
    url(r'^expense/approval/$',
        login_required(views.ExpenseApproval.as_view()),
        name='expense-approval'),
    url(r'^expense/(?P<pk>[0-9]+)/$',
        login_required(views.ExpenseDetail.as_view()),
        name='expense-detail'),
    url(r'^expense/(?P<pk>[0-9]+)/edit/$',
        login_required(views.ExpenseUpdate.as_view()),
        name='expense-update'),
    url(r'^recur-expenses/$',
        login_required(views.RecurringExpenseList.as_view()),
        name='recur-expense-list'),
    url(r'^recur-expense/add/$',
        login_required(views.RecurringExpenseCreate.as_view()),
        name='recur-expense-add'),
    url(r'^recur-expense/(?P<pk>[0-9]+)/edit/$',
        login_required(views.RecurringExpenseUpdate.as_view()),
        name='recur-expense-update'),
    url(r'^recur-expense/(?P<pk>[0-9]+)/delete/$',
        login_required(views.RecurringExpenseDelete.as_view()),
        name='recur-expense-delete'),
    url(r'^notifications/$',
        login_required(views.NotificationList.as_view()),
        name='notification-list'),
    url(r'^expense/daily-average/$',
        login_required(views.ExpenseDailyAverage.as_view()),
        name='expense-daily-average'),
    url(r'^expense/daily-submit/$',
        login_required(views.DailyExpenseSubmit.as_view()),
        name='expense-daily-submit'),
    url(r'^company-cards/$',
        login_required(views.CompanyCardList.as_view()),
        name='company-card-list'),
    url(r'^company-card/add/$',
        login_required(views.CompanyCardCreate.as_view()),
        name='company-card-add'),
    url(r'^company-card/(?P<pk>[0-9]+)/edit/$',
        login_required(views.CompanyCardUpdate.as_view()),
        name='company-card-update'),
    url(r'^company-card/(?P<pk>[0-9]+)/delete/$',
        login_required(views.CompanyCardDelete.as_view()),
        name='company-card-delete'),
    url(r'^.*', login_required(views.Index.as_view())),
]
