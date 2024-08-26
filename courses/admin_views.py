from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import * 
from .forms import *
from json import dumps
from random import shuffle
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
import os, shutil
from django.conf import settings
from .views import updatePercent, is_teacher
from django.contrib.admin.views.decorators import staff_member_required



#######################   Dangerous Zone  ###########################
# to create user Evals for the newly added instances in the local

def deleteAll():
    for Mod in [QDubl, QEval, Question, OutcomeEval, Outcome, LessonEval, Lesson, 
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
            for outcome in Outcome.objects.filter(y=year): 
                add_clean(outcome, OutcomeEval, user)
            for question in Question.objects.filter(y=year): 
                add_clean(question, QEval, user)
    print('All Evals are clean ___________________________')





def AddUser(request,year):  
    user=request.user  
    YearEval.objects.create(k=year, user=user)    
    for subject in  Subject.objects.filter(p=year):      
        SubjectEval.objects.create(k=subject, user=user)
    for unit in Unit.objects.filter(y=year): 
        UnitEval.objects.create(k=unit, user=user)
    for lesson in Lesson.objects.filter(y=year): 
        LessonEval.objects.create(k=lesson, user=user)
    for outcome in Outcome.objects.filter(y=year): 
        OutcomeEval.objects.create(k=outcome, user=user)
    for question in Question.objects.filter(y=year): 
        QEval.objects.create(k=question, user=user)
    return redirect('open', year.k)

def updateUsers(Eval, k, p, y):  
    for user in User.objects.filter(y=y): 
        Eval.objects.create(k=k, user=user,p=p)

def addAdmin(request): 
    for year in Year.objects.all():
        if not YearEval.objects.filter(k=year): 
            AddUser(request, year)







fields = {
    'o': ['video'],
    'q': ['source', 'kind', 'video', 'level'], 
}


def getOutcome(object):
    outcomeD = {'d':object.p.p, 'q':object.p, 'o':object}
    return outcomeD[object.k[0] ]

def uploadFile(request, object, html_name):  
    outcome = getOutcome(object) 
    location = outcome.location 
    exfile = '/'+location+request.FILES[html_name].name
    if outcome.file == exfile:                  
        object.file = outcome.file        
        return            
    for q in Question.objects.filter(p=outcome):           
        if html_name == 'file': 
            if q.file == exfile:                 
                object.file = q.file
                return 
            if q.ansimg == exfile: 
                object.file = q.ansimg
                return
            for d in QDubl.objects.filter(p=q):
                if d.file == exfile:     
                    object.file = d.file
                    return 
                if d.ansimg == exfile:     
                    object.file = d.ansimg
                    return
        elif html_name == 'ansimg': 
            if q.file == exfile:                 
                object.ansimg = q.file
                return 
            if q.ansimg == exfile: 
                object.ansimg = q.ansimg
                return
            for d in QDubl.objects.filter(p=q):
                if d.file == exfile:     
                    object.ansimg = d.file
                    return 
                if d.ansimg == exfile:     
                    object.ansimg = d.ansimg
                    return
    is_uploaded = request.FILES[html_name]
    fs = FileSystemStorage(location=location)                
    file = fs.save(is_uploaded.name, is_uploaded)  
    if html_name == 'file':     
        object.file = fs.url(file).replace('media/', location) 
    if html_name == 'ansimg': 
        object.ansimg = fs.url(file).replace('media/', location) 

import re
def eqeval(num):
    num_split = num.strip('=').split('=')    
    if len(num_split) == 1 : 
        num = num_split[0]
        un = 0         
    else:
        num = num_split[0]
        un = num_split[1]
    num = num.replace('^','**')
    num = float(eval(num))
    if abs(num) < 0.001 or abs(num) > 1000: 
        num = "{:.1e}".format(num)
    elif len(str(num)) > 3:
        num = float("{:.2g}".format(num))       
    num = str(num)
    if 'e' in num :
        num = num.replace('e+0','e+').replace('e-0','e-')
        num = num.replace('e+',' \u00D7 10^').replace('e',' \u00D7 10^')
        if '^' in num: 
            power = num.split('^')[1]            
            num = num.replace(power,'{'+power+'}')    
    if un : 
        num += un
    num = '\\( ' + num + ' \\)'
    return num


def unpack(object, options):
    object.options = options
    options = options.split('..')
    ops = ['op1','op2','op3','op4']
    for j in range(len(options)): 
        op = options[j].strip('\r').strip('\n')
        if op.startswith('='):
            setattr(object, ops[j], eqeval(op))   
        else: 
             setattr(object, ops[j], op)

Mod = {'y':Year, 's':Subject, 'u':Unit, 'l':Lesson, 'o':Outcome, 'q':Question, 'd':QDubl}
MEval = {'y':YearEval, 's':SubjectEval, 'u':UnitEval, 'l':LessonEval, 'o':OutcomeEval, 'q':QEval}
csymbol = {'h':'y', 'y':'s', 's':'u', 'u':'l', 'l':'o', 'o':'q', 'q':'d'}
psymbol = {'h':'h', 'y':'h', 's':'y', 'u':'s', 'l':'u', 'o':'l', 'q':'o', 'd':'q'}
ara = {'h':'الصفحة الرئيسية', 'y':'صف', 's':'مادة', 'u':'وحدة', 'l':'درس', 'o':'هدف', 'q':'سؤال', 'd':'سؤال'}
contents = {'h':'الصفوف الدراسية', 'y':'المواد الدراسية', 's':'وحدات المادة', 'u':'دروس الوحدة', 'l':'الأهداف التعليمية'}

@staff_member_required
def Create(request, p):  
    c = csymbol[p[0]]
    if request.method == 'POST':  
        name = request.POST.get('name')        
        if c == 'y': 
            object, _ = Year.objects.get_or_create(name=name)  
            yname = name
        else:
            parent = Mod[p[0]].objects.get(k=p)   
            if c in ['q','l']: 
                object, _ = Mod[c].objects.get_or_create(name=name, p=parent, y=parent.y)  
                yname = parent.y.name  
                if c == 'q':
                    if '\\(' in name : 
                        object.name = object.name.replace('*','\\times')
                    if request.POST.get('hint'): 
                        hint = request.POST.get('hint') 
                        if '\\(' in hint : 
                            hint = hint.replace('*','\\times')
                        object.hint = hint 
                    if request.POST.get('options'): 
                        unpack(object, request.POST.get('options')) 
            elif c == 'o': 
                object, _ = Outcome.objects.get_or_create(name=name, p=parent, y=parent.y, u=parent.p, s=parent.p.p)  
                yname = parent.y.name   
                # object.content = request.POST.get('content') 
            elif c == 'u': 
                object, _ = Unit.objects.get_or_create(name=name, p=parent, y=parent.p)  
                yname = parent.p.name  
            elif c == 's': 
                object, _ = Subject.objects.get_or_create(name=name, p=parent)  
                yname = parent.name     
        object.k = c+str(object.id)       
        if c in  ['q','o']:   
            if c == 'o': 
                object.location = 'media/'+object.k+'/' 
            if 'file' in request.FILES: 
                uploadFile(request, object, 'file')
            if c == 'q' and 'ansimg' in request.FILES: 
                uploadFile(request, object, 'ansimg')
            childfields = fields[c]
            for field in childfields: 
                setattr(object, field, request.POST.get(field))
        object.save()
        MEval[c].objects.create(k=object, user=User.objects.get(email='biifounder@gmail.com')) 
        for user in User.objects.filter(year=yname):                
            MEval[c].objects.create(k=object, user=user)  
        return redirect('open', p)
    else: 
        context = {'teacher':is_teacher(request), 'c':c, 'ara':ara[c]}     
    return render (request,'courses/create_update.html', context)

def cleanFiles(object): 
    outcome = getOutcome(object) 
    for f in os.listdir(settings.PROJECT_ROOT+outcome.location):
        if f != '.DS_Store':  
            will_remove = 1
            if outcome.file and outcome.file.name.split('/')[-1] == f : 
                will_remove = 0  
            else: 
                for q in Question.objects.filter(p=outcome): 
                    if (q.file and q.file.name.split('/')[-1] == f) or (q.ansimg and q.ansimg.name.split('/')[-1] == f): 
                        will_remove = 0
                        break 
                    for d in QDubl.objects.filter(p=q): 
                        if (d.file and d.file.name.split('/')[-1] == f) or (d.ansimg and  d.ansimg.name.split('/')[-1] == f): 
                            will_remove = 0
                            break 
            if will_remove : 
                file_path = settings.PROJECT_ROOT+outcome.location+f
                os.remove(file_path)

@staff_member_required
def Dublicate(request, k):
    b = k[0]
    if b == 'd': 
        question = QDubl.objects.get(k=k) 
        parent = question.p
    else: 
        question = Question.objects.get(k=k) 
        parent = question
    if request.method == 'POST':    
        if request.POST.get('name') : 
            name = request.POST.get('name')  
            if '\\(' in name : 
                name = name.replace('*','\\times')      
        object = QDubl.objects.create(name=name, p=parent)
        object.k = 'd'+str(object.id)
        if request.POST.get('options'): 
            unpack(object, request.POST.get('options')) 
        if 'file' in request.FILES or request.POST.get('removefile') : 
            object.file = None
            cleanFiles(parent.p)    
        if 'file' in  request.FILES: 
            uploadFile(request, object, 'file')        
        elif question.file: 
            object.file = question.file   
        if 'ansimg' in request.FILES or request.POST.get('removeansimg') : 
            object.ansimg = None
            cleanFiles(parent.p)        
        if 'ansimg' in request.FILES: 
            uploadFile(request, object, 'ansimg')
        elif question.ansimg: 
            object.ansimg = question.ansimg
        object.save()
        return redirect('open', parent.p.k)
    else:         
        file_name = question.file.name
        if file_name: 
            file_name = file_name.split('/')[-1]   
        ansimg_name = question.ansimg.name
        if ansimg_name: 
            ansimg_name = ansimg_name.split('/')[-1]
        context = {'teacher':is_teacher(request), 'c':'d', 'object': question, 'file_name': file_name, 'ansimg_name': ansimg_name}
    return render(request, 'courses/create_update.html', context)

@staff_member_required
def Update(request, k):    
    b = k[0]
    object = Mod[b].objects.get(k=k) 
    if request.method == 'POST':        
        p = k
        if b == 'd': 
            p = object.p.p.k        
        elif b == 'q': 
            p = object.p.k         
        if request.POST.get('name') : 
            object.name = request.POST.get('name')   
        if b == 'q':
            if request.POST.get('hint'): 
                hint = request.POST.get('hint')                
                if hint == 'None' or hint == '.': 
                    object.hint = None
                else: 
                    if '\\(' in hint : 
                        hint = hint.replace('*','\\times')
                    object.hint = hint
        if b in ['d','q']:
            if request.POST.get('options'): 
                unpack(object, request.POST.get('options')) 
            if '\\(' in object.name : 
                object.name = object.name.replace('*','\\times')
        # elif b == 'o' and request.POST.get('content'): 
        #     object.content = request.POST.get('content') 
        if b in ['d','q','o']:
            if 'file' in request.FILES or request.POST.get('removefile') : 
                object.file = None
                cleanFiles(object)
            if 'file' in request.FILES:    
                uploadFile(request, object, 'file')      
            if b in ['d','q']: 
                if 'ansimg' in request.FILES or request.POST.get('removeansimg') : 
                    object.ansimg = None
                    cleanFiles(object)
                if 'ansimg' in request.FILES:    
                    uploadFile(request, object, 'ansimg')      
        if b in ['q','o']:
            obfields = fields[b] 
            for field in obfields: 
                if request.POST.get(field) :  
                    inp = request.POST.get(field) 
                    if inp ==  '.' :
                        setattr(object, field, None) 
                    else :
                        setattr(object, field, inp)     
        object.save()
        return redirect('open', p)
    else:        
        context = {'teacher':is_teacher(request), 'c':b, 'object': object, 'ara':ara[b]}
        if b in ['d','q', 'o'] and object.file:
            file_name = object.file.name
            context['file_name'] = file_name.split('/')[-1] 
        if b in ['d','q'] and object.ansimg:
            ansimg_name = object.ansimg.name
            context['ansimg_name'] = ansimg_name.split('/')[-1] 
    return render(request, 'courses/create_update.html', context)

@staff_member_required
def Delete(request, k):      
    if request.method == 'POST':  
        b = k[0]
        object = Mod[b].objects.get(k=k)     
        if b == 'o': 
            shutil.rmtree('media/'+k)
        elif b in ['l','u','s','y']: 
            if b in ['l','u']: 
                y = object.y
            elif b == 's': 
                y = object.p                
            elif b == 'y': 
                y = object
            for outcome in Outcome.objects.filter(y=y): 
                shutil.rmtree('media/'+outcome.k)
        p = object.p.k        
        if b == 'd': 
            p = object.p.p.k           
        object.delete()
        cleanFiles(object)
        return redirect('open', p)
    return render(request, 'courses/delete.html')

 

#=======================================================================================================
def update_weights_and_percents(): 
    for lesson in Lesson.objects.all():
        tot_qs = sum([len(Question.objects.filter(p=outcome)) for outcome in Outcome.objects.filter(p=lesson)])
        for outcome in Outcome.objects.filter(p=lesson): 
            outcome.w = 0 
            if tot_qs : 
                outcome.w = round(len([q for q in Question.objects.filter(p=outcome)])/tot_qs,3)
                outcome.save()

    for unit in Unit.objects.all():
        tot_qs = sum([len(Question.objects.filter(p=outcome)) for outcome in Outcome.objects.filter(u=unit)])
        for lesson in Lesson.objects.filter(p=unit): 
            les_qs = sum([len(Question.objects.filter(p=outcome)) for outcome in Outcome.objects.filter(p=lesson)])
            lesson.w = 0 
            if tot_qs : 
                lesson.w = round(les_qs/tot_qs,3)
                lesson.save()

    for subject in Subject.objects.all():
        tot_qs = sum([len(Question.objects.filter(p=outcome)) for outcome in Outcome.objects.filter(s=subject)])
        for unit in Unit.objects.filter(p=subject): 
            les_qs = sum([len(Question.objects.filter(p=outcome)) for outcome in Outcome.objects.filter(u=unit)])
            unit.w = 0 
            if tot_qs : 
                unit.w = round(les_qs/tot_qs,3)
                unit.save()

    for year in Year.objects.all(): 
        me = User.objects.get(year='0')
        users = [ u for u in User.objects.filter(year=year.name)] + [me]
        for user in users :  
            for outcome in Outcome.objects.filter(y=year): 
                updatePercent(user,outcome.k)
    print('All Weights and Percents are Updated ______________')





''' these lines ar to follow percent calculations '''
# user = User.objects.get(email='koshgamer509@gmial.com')
# for u in SubjectEval.objects.filter(user = user) : 
#     print('subjec = ',  u.percent , u.freq)
# print('units ---------')
# for u in UnitEval.objects.filter(user = user) :  
#     print(u.percent , u.freq)
# print('lessons ---------')
# for u in LessonEval.objects.filter(user = user) :  
#     print(u.percent , u.freq)
# print('outcomes ---------')
# for u in OutcomeEval.objects.filter(user = user) :  
#     print(u.percent , u.freq)



#deleteAll()
# add_and_clean_Evals()
# update_weights_and_percents()