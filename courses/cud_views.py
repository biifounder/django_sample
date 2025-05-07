
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.admin.views.decorators import staff_member_required
from .models import * 
from .views import is_teacher
from django.conf import settings
import os, shutil


def getLesson(object):
    lessonD = {'d':object.p.p, 'q':object.p, 'l':object}
    return lessonD[object.k[0]]

def uploadFile(request, object, html_name):  
    lesson = getLesson(object) 
    location = lesson.location   # lesson folder in media
    file_path = '/'+location+request.FILES[html_name].name   # path to file in the folder
    if lesson.file == file_path:                  
        object.file = lesson.file        
        return       
    for q in Question.objects.filter(p=lesson): 
        if html_name == 'file': 
            if q.file == file_path:                 
                object.file = q.file
                return 
            if q.ansimg == file_path: 
                object.file = q.ansimg
                return
            for d in QDubl.objects.filter(p=q):
                if d.file == file_path:     
                    object.file = d.file
                    return 
                if d.ansimg == file_path:     
                    object.file = d.ansimg
                    return
        elif html_name == 'ansimg': 
            if q.file == file_path:                 
                object.ansimg = q.file
                return 
            if q.ansimg == file_path: 
                object.ansimg = q.ansimg
                return
            for d in QDubl.objects.filter(p=q):
                if d.file == file_path:     
                    object.ansimg = d.file
                    return 
                if d.ansimg == file_path:     
                    object.ansimg = d.ansimg
                    return
    file_name = request.FILES[html_name]
    fs = FileSystemStorage(location=location)                
    file = fs.save(file_name.name, file_name)  
    if html_name == 'file':     
        object.file = fs.url(file).replace('media/', location) 
    if html_name == 'ansimg': 
        object.ansimg = fs.url(file).replace('media/', location) 
        print('object.ansimg = ', object.ansimg)

def cleanFiles(lesson):    
    for f in os.listdir(settings.PROJECT_ROOT+lesson.location):
        if f != '.DS_Store':  
            will_remove = 1
            if lesson.file and lesson.file.name.split('/')[-1] == f : 
                will_remove = 0  
            else: 
                for q in Question.objects.filter(p=lesson): 
                    if (q.file and q.file.name.split('/')[-1] == f) or (q.ansimg and q.ansimg.name.split('/')[-1] == f): 
                        will_remove = 0
                        break 
                    for d in QDubl.objects.filter(p=q): 
                        if (d.file and d.file.name.split('/')[-1] == f) or (d.ansimg and  d.ansimg.name.split('/')[-1] == f): 
                            will_remove = 0
                            break 
            if will_remove : 
                file_path = settings.PROJECT_ROOT+lesson.location+f
                os.remove(file_path)



def unpack(object, options):
    object.options = options
    options = options.rstrip(' ').rstrip('..').split('..')   
    ops = ['op1','op2','op3','op4']
    for j in range(len(options)): 
        op = options[j].strip('\r').strip('\n')
        setattr(object, ops[j], op)


# _________________________________________ 
# craeate

def Create(request, object, Eval, fst, yname):
    object.k = fst+str(object.id) 
    object.save()
    if fst != 'd' : 
        Eval.objects.create(k=object, user=User.objects.get(email='biifounder@gmail.com')) 
        for user in User.objects.filter(year=yname):                
            Eval.objects.create(k=object, user=user) 
    if '\\(' in object.name : 
        object.name = object.name.replace('*','\\times')
    if request.POST.get('hint'): 
        hint = request.POST.get('hint') 
        if '\\(' in hint : 
            hint = hint.replace('*','\\times')
        object.hint = hint 
    if request.POST.get('options'): 
        unpack(object, request.POST.get('options'))
    if 'file' in request.FILES: 
        uploadFile(request, object, 'file')
    if 'ansimg' in request.FILES: 
        uploadFile(request, object, 'ansimg')
    for field in ['source', 'kind', 'video', 'level']   : 
        setattr(object, field, request.POST.get(field))
    object.save()


@staff_member_required
def Ycreate(request , p): 
    if request.method == 'POST':  
        name = request.POST.get('name') 
        object, _ = Year.objects.get_or_create(name=name)  
        Create(request, object, YearEval, 'y', object.name)
        return redirect('home')
    else: 
        context = {'teacher':is_teacher(request), 'c':'y', 'head':'إضافة صف'}     
    return render (request,'courses/create_update.html', context)

@staff_member_required
def Screate(request , p): 
    if request.method == 'POST':  
        name = request.POST.get('name') 
        parent = Year.objects.get(k=p) 
        object, _ = Subject.objects.get_or_create(name=name, p=parent)  
        Create(request, object, SubjectEval, 's', parent.name)
        return redirect('year', p)
    else: 
        context = {'teacher':is_teacher(request), 'c':'s', 'head':'إضافة مادة'}     
    return render (request,'courses/create_update.html', context)

@staff_member_required
def Ucreate(request , p): 
    if request.method == 'POST':  
        name = request.POST.get('name') 
        parent = Subject.objects.get(k=p) 
        y = parent.p
        object, _ = Unit.objects.get_or_create(name=name, p=parent, y=y)  
        Create(request, object, UnitEval, 's', y.name)
        return redirect('subject', p)
    else: 
        context = {'teacher':is_teacher(request), 'c':'u', 'head':'إضافة وحدة'}     
    return render (request,'courses/create_update.html', context)


@staff_member_required
def Lcreate(request , p): 
    if request.method == 'POST':  
        name = request.POST.get('name') 
        parent = Unit.objects.get(k=p) 
        y = parent.y
        object, _ = Lesson.objects.get_or_create(name=name, p=parent, s=parent.p, y=y)  
        location = 'media/l'+str(object.id)+'/' 
        object.location = location        
        object.save()
        if not os.path.exists(location):
            os.makedirs(location)
        Create(request, object, LessonEval, 'l', y.name)        
        return redirect('subject', parent.p.k)
    else: 
        context = {'teacher':is_teacher(request), 'c':'l','head':'إضافة درس'}     
    return render (request,'courses/create_update.html', context)

@staff_member_required
def Qcreate(request , p): 
    if request.method == 'POST':  
        name = request.POST.get('name') 
        parent = Lesson.objects.get(k=p) 
        y = parent.y     
        object, _ = Question.objects.get_or_create(name=name, p=parent, u=parent.p, s=parent.p.p, y=y)  
        Create(request, object, QEval, 'q', y.name)
        return redirect('qlist', p)
    else: 
        context = {'teacher':is_teacher(request), 'c':'q', 'head':'إضافة سؤال'}     
    return render (request,'courses/create_update.html', context)

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
        object = QDubl.objects.create(name=name, p=parent)
        Create(request, object, QEval, 'd', parent.y.name)  
        cleanFiles(object.p.p)      
        return redirect('qlist', parent.p.k)
    else:         
        file_name = question.file.name
        if file_name: 
            file_name = file_name.split('/')[-1]   
        ansimg_name = question.ansimg.name
        if ansimg_name: 
            ansimg_name = ansimg_name.split('/')[-1]
        context = {'teacher':is_teacher(request), 'c':'d', 'object': question, 'file_name': file_name, 'ansimg_name': ansimg_name, 
                   'head':'نسخ سؤال'}
    return render(request, 'courses/create_update.html', context)


# _________________________________________ 
# Update

def Update(request, object): 
    if request.POST.get('name') : 
        object.name = request.POST.get('name')  
        if '\\(' in object.name : 
            object.name = object.name.replace('*','\\times')
    if request.POST.get('options'): 
        unpack(object, request.POST.get('options')) 
    if request.POST.get('hint'): 
        hint = request.POST.get('hint')                
        if hint == 'None' or hint == '.': 
            object.hint = None
        else: 
            if '\\(' in hint : 
                hint = hint.replace('*','\\times')
            object.hint = hint
    if 'file' in request.FILES or request.POST.get('removefile') : 
        object.file = None
    if 'file' in request.FILES:    
        uploadFile(request, object, 'file')      
    if 'ansimg' in request.FILES or request.POST.get('removeansimg') : 
        object.ansimg = None
    if 'ansimg' in request.FILES:    
        uploadFile(request, object, 'ansimg')   
    for field in ['source', 'kind', 'video', 'level'] : 
        if request.POST.get(field): 
            setattr(object, field, request.POST.get(field))
    object.save()
        

@staff_member_required
def Yupdate(request, k): 
    object = Year.objects.get(k=k) 
    if request.method == 'POST':   
        Update(request, object)
        return redirect('home')    
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':'y', 'head':'تعديل صف'}
        return render(request, 'courses/create_update.html', context)
    
@staff_member_required  
def Supdate(request, k): 
    object = Subject.objects.get(k=k) 
    if request.method == 'POST':   
        Update(request, object)
        return redirect('subject', k)    
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':'s', 'head':'تعديل مادة'}
        return render(request, 'courses/create_update.html', context)

@staff_member_required
def Uupdate(request, k): 
    object = Unit.objects.get(k=k) 
    if request.method == 'POST':   
        Update(request, object)
        return redirect('subject', object.p.k)    
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':'u', 'head':'تعديل وحدة'}
        return render(request, 'courses/create_update.html', context)

@staff_member_required
def Lupdate(request, k): 
    object = Lesson.objects.get(k=k) 
    if request.method == 'POST':   
        Update(request, object)
        cleanFiles(object)
        return redirect('subject', object.p.p.k)    
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':'l', 'head':'تعديل درس'}
        return render(request, 'courses/create_update.html', context)

@staff_member_required
def Qupdate(request, k):        
    if k[0] == 'd' :
        object = QDubl.objects.get(k=k)   
        p = object.p.p
        head = 'تعديل نسخة سؤال' 
        c = 'd'
    else: 
        object = Question.objects.get(k=k)
        p = object.p
        head = 'تعديل سؤال'
        c = 'q'
    if request.method == 'POST':   
        Update(request, object)
        cleanFiles(p)
        return redirect('qlist', p.k)   
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':c, 'head':head}
        return render(request, 'courses/create_update.html', context)
  


# _________________________________________ 
# delete

def Delete(object, lessons):
    for lesson in lessons: 
        shutil.rmtree('media/'+lesson.k)    
    object.delete()
    

def Ydelete(request, k): 
    if request.method == 'POST':  
        object = Year.objects.get(k=k) 
        Delete(object, Lesson.objects.filter(y=object))
        return redirect('home')
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف صف'})


def Sdelete(request, k): 
    if request.method == 'POST':  
        object = Subject.objects.get(k=k) 
        y = object.p
        Delete(object, Lesson.objects.filter(s=object))
        return redirect('year', y.k)
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف مادة'})


def Udelete(request, k): 
    if request.method == 'POST':  
        object = Unit.objects.get(k=k) 
        s = object.p
        print(Lesson.objects.filter(p=object), '____________')
        Delete(object, Lesson.objects.filter(p=object))
        
        return redirect('subject', s.k)
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف وحدة'})


def Ldelete(request, k): 
    if request.method == 'POST':  
        object = Lesson.objects.get(k=k) 
        s = object.p.p
        Delete(object, [object])
        return redirect('subject', s.k)
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف درس'})


def Qdelete(request, k): 
    if request.method == 'POST':          
        if k[0] == 'q' : 
            object = Question.objects.get(k=k)
            l = object.p 
        else: 
            object = QDubl.objects.get(k=k)
            l = object.p.p
        object.delete()
        cleanFiles(l)
        return redirect('qlist', l.k)
    else: 
        if k[0] == 'q' : 
            head = 'حذف سؤال'
        else: 
            head = 'حذف نسخة سؤال'
        return render(request, 'courses/delete.html', {'head':head})

# _________________________________________ 


def Qlist(request, k):    
    lesson = Lesson.objects.get(k=k)
    questions = []
    for question in Question.objects.filter(p=lesson) :   
        qD = {'q':question, 'name':[n for n in question.name.split('..')]}
        if question.hint : 
            qD['hint'] = [n for n in question.hint.split('..')]  
        questions += [qD]   
        for d in QDubl.objects.filter(p=question): 
            tmp = {'q':d, 'name':[n for n in d.name.split('..')]}
            if d.hint and d.hint != None and d.hint != '00' and d.hint != 'None': 
                tmp['hint'] = [n for n in d.hint.split('..')]  
            questions += [tmp] 
    context = {'teacher': is_teacher(request), 'questions':questions, 'head':lesson.name, 'k':k, 'p':lesson.k, 's':lesson.p.p.k}
    return render (request,'courses/qlist.html', context)



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
