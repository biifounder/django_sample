from django.urls import path
from . import views
from .views import *
from . import cud_views
from . import admin_views


urlpatterns = [
    path("", views.HomePage, name='home'),

    path('logout/',views.Logout,name='logout'),
    path("adduser/<str:k>", views.AddUser, name='adduser'),  

    path("year/<str:k>/", views.YearPage, name='year'), 
    path("subject/<str:k>/", views.SubjectPage, name='subject'),     
    path("interactive/<str:k>/", views.Interactive, name='interactive'),

    path("practice/<str:k>/", views.Practice, name='practice'),
    path("assessment/<str:k>/", views.Assessment, name='assessment'),     

    path("create/<str:p>/", cud_views.Create, name='create'), 
    path("dublicate/<str:k>/", cud_views.Dublicate, name='dublicate'),
    path("update/<str:k>/", cud_views.Update, name='update'), 
    path("delete/<str:k>/", cud_views.Delete, name='delete'), 
    path("qlist/<str:k>/", cud_views.Qlist, name='qlist'),

    path("solve/", cud_views.Solve, name='solve'),  

]