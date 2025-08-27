from django.urls import path
from . import views

urlpatterns = [
    path('teacher/<str:room_name>/', views.teacher_view, name='teacher_view'),
    path('student/<str:room_name>/', views.student_view, name='student_view'),

    path('zlist/<str:k>/', views.Zlist, name='zlist'),

    path("zcreate/<str:p>/", views.Zcreate, name='zcreate'), 
    path("zupdate/<str:k>/", views.Zupdate, name='zupdate'), 
    path("zdelete/<str:k>/", views.Zdelete, name='zdelete'), 
]
