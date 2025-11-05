from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from courses.views import is_teacher
from courses.models import Lesson
# Assuming ZQuestion is in a sub-app called '.models'
from .models import ZQuestion 
from json import dumps, loads 
# We need loads for the questions_raw data if it were used, but dumps is correct for questionsJSON


@staff_member_required
def teacher_view(request, room_name):
    lesson = Lesson.objects.get(k=room_name)
    questions = ZQuestion.objects.filter(p=lesson)

    questionsJSON = []
    for question in questions:
        # Assuming question.head is a string that needs splitting for question_text
        question_text_parts = question.head.split('..')
        
        options = [question.op1, question.op2]
        if question.op3:
            options.append(question.op3)
        if question.op4:
            options.append(question.op4)
        
        # Ensure we send the correct time field
        time_limit = getattr(question, 'time_limit', 30) # Default to 30 if not set
        
        questionsJSON.append({
            # The template expects question_text to be a string, not a list of strings
            'question_text': question.head, 
            'options': options,
            "correct_answer": question.op1,
            'image_url': question.file_url,
            'time': getattr(question, 'time', 0), 
            'time_limit': time_limit,
        })
    
    # --- FIX 1: Add initial_scores to context ---
    # This is a placeholder. In a real application, you would query your
    # database/cache here for currently logged-in students and their scores.
    # We pass an empty but valid JSON string to prevent JS errors.
    initial_scores = {}
    
    context = {
        'room_name': room_name,
        'teacher': True,
        'lesson': lesson,
        # 'questions_raw': questions, # Not needed in the template now
        'questions': dumps(questionsJSON),
        'initial_scores': dumps(initial_scores), # FIX: Pass the empty dictionary as JSON string
    }
    
    # Note: I've also slightly adjusted the parsing of 'question_text' and 'time_limit' 
    # to be safer, assuming the front-end expects a string for the question text.
    
    return render(request, 'live/teacher.html', context)





def student_view(request, room_name):
    lesson = Lesson.objects.get(k=room_name)
    context = {
        'room_name': room_name,
        'lesson': lesson,
    }
    return render(request, 'live/student.html', context)






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




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage

@csrf_exempt
def upload_question_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        filename = default_storage.save(f'question_images/{image.name}', image)
        image_url = default_storage.url(filename)
        return JsonResponse({'image_url': image_url})
    return JsonResponse({'error': 'No image provided'}, status=400)
