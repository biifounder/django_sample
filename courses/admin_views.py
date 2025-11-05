from django.shortcuts import render, redirect
from .models import * 
from .forms import *
from .views import updatePercents
from live.models import * 




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
    for ueval in uevals[1:]: 
        ueval.delete()

def add_and_clean_Evals(): 
    for year in Year.objects.all(): 
        me = User.objects.get(year='0')
        users = [ u for u in User.objects.filter(year=year.head)] + [me]
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
    for year in Year.objects.all(): 
        me = User.objects.get(year='0')
        users = [ u for u in User.objects.filter(year=year.head)] + [me]
        for user in users : 
            lessons = [lesson.k for lesson in Lesson.objects.filter(y=year)] 
            # for k in lessons: 
            #     lesson = Lesson.objects.get(k=k)
            #     eval = LessonEval.objects.get(user=user, k=lesson)
            #     if eval.score > 0: 
            #         eval.score = eval.score - 1
            #         eval.save()           
            updatePercents(lessons , user)   
    print('All Weights and Percents are Updated ______________')






def loadscores(): # from datafile which contains QEval/ after loading the new users 
    import json
    with open('eval.json', 'r') as file:
        data = json.load(file)
        print(data[-1])
    for d in data : 
        if d['model'] == 'courses.qeval': 
            for v in QEval.objects.all() :                
                if str(v.k.id) == str(d['fields']['k']) and str(v.user) == str(User.objects.get(id=d['fields']['user']).email):
                    if d['fields']['score'] != v.pscore: 
                        v.pscore = d['fields']['score']
                        if d['fields']['score'] > 0 : 
                            v.tscore = d['fields']['score']
                        v.save() 
                    if d['fields']['flag'] != v.flag: 
                        v.pscore = d['fields']['score']
                        v.save() 
            print('________________________________________')
#=======================================================================================================





# add_and_clean_Evals()
# update_weights_and_percents()
# 
# loadscores()


