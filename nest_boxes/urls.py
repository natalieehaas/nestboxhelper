"""nest_boxes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from nest_box_helper import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_screen_view, name="home"),
    path('register/', views.registration_view, name="register"),
    path('logout/', views.logout_view, name="logout"),
    path('login/', views.login_view, name="login"),
    path('dashboard/', views.dashboard_view, name="dashboard"),
    path('nest_box_helper/update', views.account_update_view, name="account_update"),
    path('park/<park_id>/<box_id>/<attempt_id>/create/sheet/', views.create_sheet_form_view, name="create_sheet"),
    path('add/park/', views.add_park_form_view, name="add_park"),
    path('park/<park_id>/park_summary', views.park_summary_view, name="park_summary"),
    path('park/<park_id>/addbox', views.add_box_form_view, name="add_box"),
    path('park/<park_id>/<box_id>/attempt_summary', views.attempt_summary_view, name="attempt_summary"),
    path('park/<park_id>/<box_id>/addattempt', views.add_attempt_form_view, name="add_attempt"),
    path('park/<park_id>/<box_id>/<attempt_id>/attempt_detail', views.attempt_detail_view, name="attempt_detail"),
    path('park/<park_id>/<box_id>/<attempt_id>/<slug>/update', views.update_sheet_form_view, name="update_sheet"),
    path('park/<park_id>/<box_id>/<attempt_id>/<slug>', views.detail_sheet_view, name="detail_sheet"),
    path('must_authenticate/', views.authentication_view, name="authenticate"),
    path('delete/<park_id>',views.delete_user_park,name='delete_user_park'),
    path('delete/<park_id>/<box_id>',views.delete_box,name='delete_box'),
    path('delete/<park_id>/<box_id>/<attempt_id>',views.delete_attempt,name='delete_attempt'),
    path('delete/<park_id>/<box_id>/<attempt_id>/<slug>',views.delete_sheet,name='delete_sheet'),
    path('summarize_attempt/<attempt_id>',views.summarize_attempt, name='summarize_attempt'),

    # Password Reset Links
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
