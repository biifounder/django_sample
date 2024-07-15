from django.db import models
from django.contrib.auth.models import AbstractUser
from embed_video.fields import EmbedVideoField


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    year = models.CharField(max_length=200, null=True)
    gov = models.CharField(max_length=200, null=True)
    prov = models.CharField(max_length=200, null=True)
    school = models.CharField(max_length=200, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


#_______________________________________________________________________________
class Year(models.Model):   
    name = models.CharField(max_length=400)    
    k = models.CharField(max_length=400, default='1')        

class YearEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Year, on_delete=models.CASCADE) 
    percent = models.PositiveSmallIntegerField(default=0) 

   
#_______________________________________________________________________________
class Subject(models.Model):
    name = models.CharField(max_length=400)    
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Year, on_delete=models.CASCADE) 
    
class SubjectEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Subject, on_delete=models.CASCADE) 
    score = models.PositiveSmallIntegerField(default=0) 
    total = models.PositiveSmallIntegerField(default=0) 
    percent = models.PositiveSmallIntegerField(default=0) 
    freq = models.PositiveSmallIntegerField(default=0)  

#_______________________________________________________________________________
class Unit(models.Model):
    name = models.CharField(max_length=400)   
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Subject, on_delete=models.CASCADE) 
    y = models.ForeignKey(Year, on_delete=models.CASCADE) 
    
class UnitEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Unit, on_delete=models.CASCADE) 
    score = models.PositiveSmallIntegerField(default=0) 
    total = models.PositiveSmallIntegerField(default=0) 
    percent = models.PositiveSmallIntegerField(default=0) 
    freq = models.PositiveSmallIntegerField(default=0)  
    


#_______________________________________________________________________________
class Lesson(models.Model):
    name = models.CharField(max_length=400)    
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Unit, on_delete=models.CASCADE) 
    y = models.ForeignKey(Year, on_delete=models.CASCADE) 

class LessonEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Lesson, on_delete=models.CASCADE) 
    score = models.PositiveSmallIntegerField(default=0) 
    total = models.PositiveSmallIntegerField(default=0) 
    percent = models.PositiveSmallIntegerField(default=0) 
    freq = models.PositiveSmallIntegerField(default=0)  

#_______________________________________________________________________________
class Outcome(models.Model):
    name = models.CharField(max_length=400)
    content = models.CharField(max_length=10000, default='_')
    file = models.FileField(null=True)
    location = models.CharField(max_length=400,null=True)  
    video = EmbedVideoField(null=True)
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Lesson, on_delete=models.CASCADE) 
    u = models.ForeignKey(Unit, on_delete=models.CASCADE, default='') 
    s = models.ForeignKey(Subject, on_delete=models.CASCADE, default='') 
    y = models.ForeignKey(Year, on_delete=models.CASCADE, default='')  

class OutcomeEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Outcome, on_delete=models.CASCADE) 
    score = models.PositiveSmallIntegerField(default=0) 
    total = models.PositiveSmallIntegerField(default=0) 
    percent = models.PositiveSmallIntegerField(default=0) 
    freq = models.PositiveSmallIntegerField(default=0)  

#_______________________________________________________________________________

class Question(models.Model):
    name = models.TextField(null=True)
    op1 = models.CharField(max_length=10000,null=True)
    op2 = models.CharField(max_length=10000,null=True)
    op3 = models.CharField(max_length=10000,null=True)
    op4 = models.CharField(max_length=10000,null=True)
    options = models.TextField(null=True) 
    hint = models.TextField(null=True)   
    level = models.CharField(max_length=400,null=True) 
    file = models.FileField(null=True)
    ansimg = models.FileField(null=True)
    video = EmbedVideoField(null=True)
    source = models.CharField(max_length=400,default='other') 
    kind =  models.CharField(max_length=400,default='understand')  
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Outcome, on_delete=models.CASCADE) 
    y = models.ForeignKey(Year, on_delete=models.CASCADE, default='') 
    
    
class QEval(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    k = models.ForeignKey(Question, on_delete=models.CASCADE) 
    score = models.SmallIntegerField(default=0) 
    flag =  models.PositiveSmallIntegerField(default=0) 


class QDubl(models.Model):
    name = models.TextField(null=True)
    op1 = models.CharField(max_length=10000,null=True)
    op2 = models.CharField(max_length=10000,null=True)
    op3 = models.CharField(max_length=10000,null=True)
    op4 = models.CharField(max_length=10000,null=True)
    options = models.TextField(null=True) 
    file = models.FileField(null=True)
    ansimg = models.FileField(null=True)
    k = models.CharField(max_length=400, default='1')
    p = models.ForeignKey(Question, on_delete=models.CASCADE) 
    