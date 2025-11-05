
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.admin.views.decorators import staff_member_required
from .models import * 
from .views import is_teacher
from django.conf import settings
import os, shutil

# _________________________________________ 
# craeate

Mod = {'y':Year, 's':Subject, 'u':Unit, 'l':Lesson, 'q':Question, 'd':QDubl} 
Eval = {'y':YearEval, 's':SubjectEval, 'u':UnitEval, 'l':LessonEval, 'q':QEval}  
pMod = {'s':Year, 'u':Subject, 'l':Unit, 'q':Lesson, 'd':Question} 
child = {'h':'y', 'y':'s', 's':'u', 'u':'l', 'l':'q', 'q':'d'} 

def tree_fileds(request, p, i): 
    args = {'head': request.POST.get('head')}    
    if i != 'y': 
        parent = pMod[i].objects.get(k=p) 
        args['p'] = parent
        if i == 'q':
            year = parent.y
            args.update({'y': year, 's': parent.s, 'u': parent.p})
        elif i == 'l' : 
            year = parent.y
            args.update({'y': year, 's': parent.p})
        elif i == 'u' : 
            year = parent.p
            args['y'] = year
        elif i == 's' : 
            year = parent 
    else:
        year = 0
    object, _ = Mod[i].objects.get_or_create(**args)
    return object, year

def info_fileds(request, object, i): 
    for field in ['head', 'options', 'hint','file', 'ansimg', 'video', 'source', 'kind', 'level']: 
        if request.POST.get(field): 
            if request.POST.get(field) == '.':
                setattr(object, field, None)  
            else: 
                setattr(object, field, request.POST.get(field))  
    if i == 'u':
        location = 'media/u'+str(object.id)+'/' 
        if not os.path.exists(location):
            os.makedirs(location) 

    if i in ['d','q','u']:
        if object.file:  
            if i == 'd': 
                object.file_url = '/media/'+object.p.u.k+'/'+object.file+'.png'
            elif i == 'q': 
                object.file_url = '/media/'+object.u.k+'/'+object.file+'.png'
            else: 
                object.file_url = '/media/'+object.k+'/'+object.file+'.pdf'
            
            


    if i in ['d','q']:
        if object.ansimg:
            if i == 'q':
                object.ansimg_url = '/media/'+object.u.k+'/'+object.ansimg+'.png'
            elif i == 'd': 
                object.ansimg_url = '/media/'+object.p.u.k+'/'+object.ansimg+'.png'
        else: 
            object.ansimg_url = None
    
    if request.POST.get('options'):
        ops = ['op1','op2','op3','op4']
        for op in ops: 
            setattr(object, op, None)
        options = request.POST.get('options') 
        options = options.rstrip(' ').rstrip('..').split('..')       
        for j in range(min(len(options),4)): 
            op = options[j].strip('\r').strip('\n')
            setattr(object, ops[j], op)
    object.save()
     

def addEval(i, object, year):
    if i == 'y': 
        yhead = object.head
    else : 
        yhead = year.head
    eval = Eval[i]
    eval.objects.create(k=object, user=User.objects.get(email='biifounder@gmail.com')) 
    for user in User.objects.filter(year=yhead):                
        eval.objects.create(k=object, user=user) 

def go_redierct(i, object): 
    if i == 'y': 
        return redirect('home')
    elif i == 's' : 
        return redirect('year', object.p.k)
    elif i == 'u': 
        return redirect('subject', object.p.k)
    elif i == 'l' : 
        return redirect('subject', object.p.p.k)
    elif i == 'q': 
        return redirect('qlist', object.p.k)
    elif i == 'd': 
        return redirect('qlist', object.p.p.k)


@staff_member_required
def Create(request, p):
    i = child[p[0]]    
    if request.method == 'POST':
        object, year = tree_fileds(request, p, i)         
        object.k = i+str(object.id)
        addEval(i, object, year)
        info_fileds(request, object, i)
        return go_redierct(i, object)
    else: 
        context = {'teacher':is_teacher(request), 'c':i, 'head':'إضافة'}    
        return render (request,'courses/create_update.html', context)


@staff_member_required
def Dublicate(request, k):
    i = k[0]
    if i == 'd':        
        question = QDubl.objects.get(k=k) 
        parent = question.p
    else: 
        i = child[i]
        question = Question.objects.get(k=k) 
        parent = question
    if request.method == 'POST':    
        if request.POST.get('head') : 
            head = request.POST.get('head')       
        object = QDubl.objects.create(head=head, p=parent)
        object.k = 'd'+str(object.id)
        info_fileds(request, object, 'd') 
        return redirect('qlist', parent.p.k)
    else:         
        context = {'teacher':is_teacher(request), 'c':'d', 'object': question, 'head':'نسخ سؤال'}
    return render(request, 'courses/create_update.html', context)


# _________________________________________ 
# Update

@staff_member_required
def Update(request, k):
    i =k[0]
    object = Mod[i].objects.get(k=k)
    if request.method == 'POST':
        info_fileds(request, object, i)
        return go_redierct(i, object)
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':i, 'head':'تعديل'}
        return render (request,'courses/create_update.html', context)
  


# _________________________________________ 
# delete 

def Delete(request, k): 
    if request.method == 'POST':  
        i = k[0]
        object = Mod[i].objects.get(k=k)
        if i in ['u','s','y']:
            if i == 'u' : 
                units = [object]
            elif i == 's': 
                units = Unit.objects.filter(p=object)
            elif i == 'y': 
                units = Unit.objects.filter(p=object)
            for unit in units: 
                shutil.rmtree('media/'+unit.k)    
        object.delete()
        return go_redierct(i, object)
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف'})

# _________________________________________ 


# def Qlist(request, k):    
#     lesson = Lesson.objects.get(k=k)
#     questions = []
#     for question in Question.objects.filter(p=lesson) :   
#         qD = {'q':question, 'head':[n for n in question.head.split('..')]}
#         if '__' in question.op1 : 
#             qD['op1'] = [n for n in question.op1.split('__')]  
#         else: 
#             qD['op1'] = [question.op1]
#         if question.hint : 
#             qD['hint'] = [n for n in question.hint.split('..')]  
#         questions += [qD]   
#         for d in QDubl.objects.filter(p=question): 
#             tmp = {'q':d, 'head':[n for n in d.head.split('..')]}
#             if '__' in d.op1 : 
#                 tmp['op1'] = [n for n in d.op1.split('__')] 
#             else: 
#                 tmp['op1'] = [d.op1]
#             if d.hint and d.hint != None and d.hint != '00' and d.hint != 'None': 
#                 tmp['hint'] = [n for n in d.hint.split('..')]  
#             questions += [tmp] 
#     context = {'teacher': is_teacher(request), 'questions':questions, 'head':lesson.head, 'k':k, 'p':lesson.k, 's':lesson.p.p.k}
#     return render (request,'courses/qlist.html', context)



from .models import Year, Subject, Unit, Lesson, Question, QDubl 

def Qlist(request, k):    
    lesson = Lesson.objects.get(k=k)
    current_unit = lesson.p  # الوحدة التي ينتمي إليها الدرس الحالي
    current_subject = current_unit.p # المادة التي تنتمي إليها الوحدة الحالية
    
    # ------------------ منطق الشريط الجانبي المعدّل (الوحدة والدرس فقط) ------------------
    # جلب جميع الوحدات التابعة للمادة الحالية
    units = Unit.objects.filter(p=current_subject)
    sidebar_data = []

    for unit in units:
        unit_data = {
            'unit': unit,
            # جلب جميع الدروس التابعة لهذه الوحدة
            'lessons': Lesson.objects.filter(p=unit) 
        }
        sidebar_data.append(unit_data)
    # -----------------------------------------------------------------------------

    # منطق جلب الأسئلة الأصلي (يبقى كما هو)
    questions = []
    for question in Question.objects.filter(p=lesson) :   
        qD = {'q':question, 'head':[n for n in question.head.split('..')]}
        if '__' in question.op1 : 
            qD['op1'] = [n for n in question.op1.split('__')]  
        else: 
            qD['op1'] = [question.op1]
        if question.hint : 
            qD['hint'] = [n for n in question.hint.split('..')]  
        questions += [qD]   
        for d in QDubl.objects.filter(p=question): 
            tmp = {'q':d, 'head':[n for n in d.head.split('..')]}
            if '__' in d.op1 : 
                tmp['op1'] = [n for n in d.op1.split('__')] 
            else: 
                tmp['op1'] = [d.op1]
            if d.hint and d.hint != None and d.hint != '00' and d.hint != 'None': 
                tmp['hint'] = [n for n in d.hint.split('..')]  
            questions += [tmp] 
    
    context = {
        'teacher': is_teacher(request), 
        'questions': questions, 
        'head': lesson.head, 
        'k': k, 
        'p': lesson.k, 
        's': lesson.p.p.k,
        # تمرير بيانات الشريط الجانبي الجديدة
        'sidebar_data': sidebar_data, 
        'current_lesson_k': k, 
        'current_unit_k': current_unit.k, # لتحديد الوحدة الحالية وتمييزها
    }
    return render (request,'courses/qlist.html', context)

def Solve(request): 
    context = {'teacher':is_teacher(request)}
    return render(request, 'courses/solve.html', context)

