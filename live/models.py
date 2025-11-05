from django.db import models
from courses.models import Lesson 

class ZQuestion(models.Model):
    head = models.TextField(null=True)
    op1 = models.CharField(max_length=10000,null=True)
    op2 = models.CharField(max_length=10000,null=True)
    op3 = models.CharField(max_length=10000,null=True)
    op4 = models.CharField(max_length=10000,null=True)
    options = models.TextField(null=True) 
    file = models.CharField(max_length=400,null=True)
    file_url = models.CharField(max_length=400, null=True)
    time = models.CharField(max_length=400, default='0')
    time_limit = models.CharField(max_length=400, default='30')
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Lesson, on_delete=models.CASCADE) 
    class Meta:
        ordering = ['id']
