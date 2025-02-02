from django.shortcuts import render, redirect
from .models import * 
from .forms import *
from .views import updatePercents




#######################   Dangerous Zone  ###########################
# to create user Evals for the newly added instances in the local

def deleteAll():
    for Mod in [QDubl, QEval, Question, LessonEval, Lesson, 
                UnitEval, Unit, SubjectEval, Subject, YearEval, Year, User] : 
        Mod.objects.all().delete()

def add_clean(object, Eval, user):    
    if not Eval.objects.filter(k=object, user=user): 
        Eval.objects.create(k=object, user=user)  
    uevals = Eval.objects.filter(k=object, user=user) 
    # if len(uevals) > 1 : 
    #     print(object , uevals, user.email , '_________________________') 
    for ueval in uevals[1:]: 
        ueval.delete()

def add_and_clean_Evals(): 
    for year in Year.objects.all(): 
        me = User.objects.get(year='0')
        users = [ u for u in User.objects.filter(year=year.name)] + [me]
        # print(len(users))
        for user in users :   
            add_clean(year, YearEval, user)           
            for subject in  Subject.objects.filter(p=year):    
                add_clean(subject, SubjectEval, user)
            for unit in Unit.objects.filter(y=year): 
                add_clean(unit, UnitEval, user)
            for lesson in Lesson.objects.filter(y=year): 
                add_clean(lesson, LessonEval, user)
            for question in Question.objects.filter(y=year): 
                add_clean(question, QEval, user)
    print('All Evals are clean ___________________________')

def update_weights_and_percents(): 
    for subject in Subject.objects.all(): 
        units, unit_nqs, utot = Unit.objects.filter(p=subject), [], 0
        for unit in units: 
            lessons = Lesson.objects.filter(p=unit) 
            less_nqs = [len(Question.objects.filter(p=lesson)) for lesson in lessons]
            tot = sum(less_nqs)
            if tot : 
                for i in range(len(lessons)): 
                    lesson = lessons[i]
                    lesson.w = round(less_nqs[i]/tot,3)  
                    lesson.save() 
            unit_nqs += [tot] 
            utot += tot
        if utot:
            for i in range(len(units)): 
                unit = units[i]
                unit.w = round(unit_nqs[i]/utot,3)  
                unit.save()   

    for year in Year.objects.all(): 
        me = User.objects.get(year='0')
        users = [ u for u in User.objects.filter(year=year.name)] + [me]
        for user in users : 
            lessons = [lesson.k for lesson in Lesson.objects.filter(y=year)] 
            # for lesson in lessons: 
            #     eval = LessonEval.objects.get(user=user, k=lesson)
            #     if eval.score > 0: 
            #         eval.score = eval.score - 1
            #         eval.save()           
            updatePercents(lessons , user)   
    print('All Weights and Percents are Updated ______________')





#=======================================================================================================


# deleteAll()
# add_and_clean_Evals()
# update_weights_and_percents()