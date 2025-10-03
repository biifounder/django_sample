from django.urls import path
from . import views

urlpatterns = [
    path('teacher/<str:room_name>/', views.teacher_view, name='teacher_view'),
    path('student/<str:room_name>/', views.student_view, name='student_view'),

    path('zlist/<str:k>/', views.Zlist, name='zlist'),

    path("zcreate/<str:p>/", views.Zcreate, name='zcreate'), 
    path("zupdate/<str:k>/", views.Zupdate, name='zupdate'), 
    path("zdelete/<str:k>/", views.Zdelete, name='zdelete'), 
    path('upload-question-image/', views.upload_question_image, name='upload_question_image'),


    # zoom
    # path("teacher/<str:meeting_id>/", views.teacher_view, name="teacher"),
    # path("student/<str:meeting_id>/", views.student_view, name="student"),
    # path("api/zoom-signature/", views.zoom_signature_api, name="zoom_signature_api"),

    # jitsi
    # path("teacher/", views.teacher_view, name="teacher"),
    # path("student/", views.student_view, name="student"),


]
