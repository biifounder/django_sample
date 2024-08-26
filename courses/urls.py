from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views
from . import admin_views

urlpatterns = [
    path("", views.HomePage, name='home'),

    path('logout/',views.Logout,name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='courses/password_reset.html'),
        name='password_reset'),  
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='courses/password_reset_done.html'), 
            name='password_reset_done'), 
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='courses/password_reset_confirm.html'), 
            name='password_reset_confirm'), 
    path('password-reset-complete/', auth_views.PasswordChangeDoneView.as_view(
            template_name='courses/password_reset_complete.html'), 
            name='password_reset_complete'), 

    path("open/<str:k>/", views.Object, name='open'),
    path("practice/<str:k>/", views.Practice, name='practice'),
    path("assessment/<str:k>/", views.Assessment, name='assessment'),
    path("result/<str:k>/", views.Result, name='result'),        
    
    path("create/<str:p>/", views.Create, name='create'),
    path("update/<str:k>/", views.Update, name='update'),
    path("delete/<str:k>/", views.Delete, name='delete'),
    path("dublicate/<str:k>/", views.Dublicate, name='dublicate'),
    path("adduser/<str:k>", views.AddUser, name='adduser'),
    
]