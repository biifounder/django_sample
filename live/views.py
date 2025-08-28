from django.shortcuts import render , redirect
from django.contrib.admin.views.decorators import staff_member_required
from courses.views import is_teacher
from courses.models import Lesson
from .models import ZQuestion
from json import dumps

@staff_member_required
def teacher_view(request, room_name):
    lesson = Lesson.objects.get(k=room_name)
    questions = ZQuestion.objects.filter(p=lesson)
    questionsJSON = []
    for question in questions:
        options = [question.op1, question.op2]
        if question.op3:
            options.append(question.op3)
        if question.op4:
            options.append(question.op4)
        questionsJSON.append({
            'question_text': [n for n in question.head.split('..')],
            'options': options,
            "correct_answer": question.op1,
            'image_url': question.file_url,
            'time': question.time,
            'time_limit': question.time_limit,
            
        }) 
    context = {
        'room_name': room_name,
        'teacher': is_teacher(request),
        'questions': questions,
        'lesson': lesson,
        'questions': dumps(questionsJSON),
    }
    return render(request, 'live/teacher.html', context)


def student_view(request, room_name):
    lesson = Lesson.objects.get(k=room_name)
    return render(request, 'live/student.html', {
        'room_name': room_name, 
        'lesson': lesson,
    })

@staff_member_required
def info_fileds(request, object): 
    for field in ['head', 'options', 'file', 'time','time_limit']: 
        if request.POST.get(field): 
            if request.POST.get(field) == '.':
                setattr(object, field, None)  
            else: 
                setattr(object, field, request.POST.get(field))  

    if object.file:  
        object.file_url = '/media/'+object.p.p.k+'/'+object.file+'.png'
    else: 
        object.file_url = None
   
    ops = ['op1','op2','op3','op4']
    for op in ops: 
        setattr(object, op, None)
    options = request.POST.get('options') 
    options = options.rstrip(' ').rstrip('..').split('..')       
    for j in range(min(len(options),4)): 
        op = options[j].strip('\r').strip('\n')
        setattr(object, ops[j], op)
    object.save()




@staff_member_required
def Zcreate(request, p):
    if request.method == 'POST':
        lesson = Lesson.objects.get(k=p)
        args = {'head': request.POST.get('head') , 'p': lesson}
        lesson, _ = ZQuestion.objects.get_or_create(**args)
        lesson.k = 'z'+str(lesson.id)
        info_fileds(request, lesson)
        return redirect('zlist', lesson.p.k)
    else: 
        context = {'teacher':is_teacher(request), 'c':'z', 'head':'إضافة'}    
        return render (request,'courses/create_update.html', context)
    

@staff_member_required
def Zupdate(request, k):
    object = ZQuestion.objects.get(k=k)
    if request.method == 'POST':
        info_fileds(request, object)
        return redirect('zlist', object.p.k)
    else: 
        context = {'teacher':is_teacher(request), 'object': object, 'c':'z', 'head':'تعديل'}
        return render (request,'courses/create_update.html', context)


@staff_member_required
def Zdelete(request, k): 
    if request.method == 'POST':  
        object = ZQuestion.objects.get(k=k)
        object.delete()
        return redirect('zlist', object.p.k)
    else: 
        return render(request, 'courses/delete.html', {'head':'حذف'})


@staff_member_required
def Zlist(request, k):    
    lesson = Lesson.objects.get(k=k)
    questions = []
    for question in ZQuestion.objects.filter(p=lesson) :   
        q = {'k':question.k, 'head':[n for n in question.head.split('..')], 'time':question.time , 'time_limit': question.time_limit}
        if '__' in question.op1 : 
            q['op1'] = [n for n in question.op1.split('__')]  
        else: 
            q['op1'] = question.op1
            q['op2'] = question.op2
            if question.op3: 
                q['op3'] = question.op3
            if question.op4:
                q['op4'] = question.op4
        if question.file_url:                       
            q['file'] = question.file_url            
        questions += [q]   
    context = {'teacher': is_teacher(request), 'questions':questions, 'k':k, 's':lesson.p.p.k , 'head':lesson.head}
    return render (request,'live/zlist.html', context)