from django.urls import path
from . import views
from .views import *
from django.contrib.auth import views as auth_views
from . import cud_views, admin_views
from . import admin_calc


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

    path("practice/<str:k>/", views.Practice, name='practice'),
    path("assessment/<str:k>/", views.Assessment, name='assessment'),
    path("result/<str:k>/", views.Result, name='result'), 
    path("adduser/<str:k>", views.AddUser, name='adduser'),
    

    path("solve/", admin_calc.Solve, name='solve'),  


    path("year/<str:k>/", views.YearPage, name='year'), 
    path("subject/<str:k>/", views.SubjectPage, name='subject'), 
    path("qlist/<str:k>/", cud_views.Qlist, name='qlist'),

    path("ycreate/<str:p>/", cud_views.Ycreate, name='ycreate'), 
    path("screate/<str:p>/", cud_views.Screate, name='screate'), 
    path("ucreate/<str:p>/", cud_views.Ucreate, name='ucreate'), 
    path("lcreate/<str:p>/", cud_views.Lcreate, name='lcreate'), 
    path("qcreate/<str:p>/", cud_views.Qcreate, name='qcreate'), 
    path("dublicate/<str:k>/", cud_views.Dublicate, name='dublicate'),

    path("yupdate/<str:k>/", cud_views.Yupdate, name='yupdate'), 
    path("supdate/<str:k>/", cud_views.Supdate, name='supdate'), 
    path("uupdate/<str:k>/", cud_views.Uupdate, name='uupdate'), 
    path("lupdate/<str:k>/", cud_views.Lupdate, name='lupdate'), 
    path("qupdate/<str:k>/", cud_views.Qupdate, name='qupdate'), 

    path("ydelete/<str:k>/", cud_views.Ydelete, name='ydelete'), 
    path("sdelete/<str:k>/", cud_views.Sdelete, name='sdelete'), 
    path("udelete/<str:k>/", cud_views.Udelete, name='udelete'), 
    path("ldelete/<str:k>/", cud_views.Ldelete, name='ldelete'), 
    path("qdelete/<str:k>/", cud_views.Qdelete, name='qdelete'), 

    
]