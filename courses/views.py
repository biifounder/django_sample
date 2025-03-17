from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import * 
from .forms import *
from json import dumps
from random import shuffle
from django.core.mail import send_mail
from math import log

#======================================================================================================
def auth(request):
    return request.user.is_authenticated


def is_teacher(request): 
    if auth(request) :   
        if request.user.email in  ['biifounder@gmail.com'] : 
            return request.user.username 
    return False


def EmailSender(email_subject, message,receiver_emails):
        send_mail(
        email_subject,
        message,
        'biifounder@gmail.com',
        receiver_emails,
        fail_silently=False,
        )

def AddUser(request,year):  
    user=request.user  
    YearEval.objects.create(k=year, user=user)    
    for subject in  Subject.objects.filter(p=year):      
        SubjectEval.objects.create(k=subject, user=user)
    for unit in Unit.objects.filter(y=year): 
        UnitEval.objects.create(k=unit, user=user)
    for lesson in Lesson.objects.filter(y=year): 
        LessonEval.objects.create(k=lesson, user=user)
    for question in Question.objects.filter(y=year): 
        QEval.objects.create(k=question, user=user)
    return redirect('year', year.k)

def HomePage(request):       
    if request.method == 'POST':   
        if "visitor" in request.POST:            
            y = request.POST.get('year') 
            year = Year.objects.get(name=y)
            return redirect('year', year.k)     
            
        if "register" in request.POST:          
            form = MyUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.name = request.POST.get('name')
                user.email = request.POST.get('email')
                user.year = request.POST.get('year')
                user.gov = request.POST.get('gov')
                user.prov = request.POST.get('prov') 
                user.school = request.POST.get('school')                
                user.save()  
                login(request, user)
                year = Year.objects.get(name=user.year)  
                AddUser(request, year)                
                return redirect('home')  
            else: 
                return HttpResponse("يوجد خطأ في تسجيلك")   
        elif "login" in request.POST:            
            email=request.POST.get('email')
            pass1=request.POST.get('pass')
            user=authenticate(request,email=email,password=pass1)            
            if user is not None:
                login(request,user) 
                return redirect('home')
            else:
                return HttpResponse ("كلمة السر خطأ")
        elif 'enquirey' in request.POST:
            email=request.POST.get('email')
            email_subject = 'from ' + email
            message = request.POST.get('message')
            EmailSender(email_subject, message, ['bahaaismailres@gmail.com'])
            return HttpResponse ("نشكركم على التواصل معنا وسوف يتم الرد على استفساركم في أقرب وقت ممكن إن شاء الله")   
    else:   
        if is_teacher(request) or not request.user.is_authenticated:             
            form = MyUserCreationForm()  
            context = {'teacher':is_teacher(request), 'years':Year.objects.all(), 'form':form}
            context['allusers'] = dumps([u.email for u in User.objects.all()])
            return render (request,'courses/home.html',context)
        else:             
            context = {'teacher':is_teacher(request)}        
            y = User.objects.get(email=request.user).year
            return redirect('year', Year.objects.get(name=y).k)


@login_required(login_url='login')
def Logout(request):
    logout(request)
    return redirect('home')


def YearPage(request, k): 
    user = 0
    if request.user.is_authenticated : 
        user = request.user  
    nD = {'5':'خامس', '6':'سادس', '7':'سابع', '8':'ثامن', 
                '9':'تاسع', '10':'عاشر', '11':'حادي عشر', '12':'ثاني عشر'}
    year = Year.objects.get(k=k)
    ypercent = 0
    if user :   
        ypercent = YearEval.objects.get(user=user, k=year).percent 
    subjects = []
    for subject in Subject.objects.filter(p=year): 
        spercent = 0 
        if user :
            spercent = SubjectEval.objects.get(user=user, k=subject).percent  
        subjects += [{'name':subject.name, 'k':subject.k, 'spercent':spercent}]


    outstandings = []  
    ordered = YearEval.objects.filter(k=year).order_by('-percent')      
    ordered_percents = [ord.percent for ord in ordered]   
    if len(ordered_percents)  > 4:  
        rank5 = ordered_percents[4]
    else: 
        if ordered_percents : 
            rank5 = min(ordered_percents)
        else: 
            rank5 = 0
    rank5 = len([ord for ord in ordered_percents if ord >= rank5])
    for ord in ordered[:rank5]: 
        out = ord.user
        outstandings += [{'rank':ord.percent,'name': out.name, 'school':out.school, 'prov': out.prov, 'gov': out.gov, 'percent':ord.percent}]
    if user:               
        user_rank = ordered_percents.index(ypercent)+1


    context = {'teacher': is_teacher(request), 'year':year, 'yname':nD[year.name] , 'ypercent':ypercent, 'subjects':subjects, 
               'outstandings':outstandings, 'user_rank':user_rank}
    return render (request,'courses/year.html', context)

def SubjectPage(request, k): 
    if request.method == 'POST':         
        selectedlessons = request.POST.get('selectedlessons').split(',')
        purpose = selectedlessons[-1]
        request.session['selectedlessons'] = selectedlessons[:-1]
        if purpose == 'pract' :  
            return redirect('practice', k)
        elif purpose == 'test' :
            return redirect('assessment', k)
        else: 
            return redirect('subject', k)
    else: 
        user = 0
        if request.user.is_authenticated : 
            user = request.user  
        subject = Subject.objects.get(k=k)
        spercent = 0 
        if user :
            spercent = SubjectEval.objects.get(user=user, k=subject).percent  
        units, weaknesses = [], []
        for unit in Unit.objects.filter(p=subject):   
            upercent = 0 
            if user :
                upercent = UnitEval.objects.get(user=user, k=unit).percent       
            lessons = []
            for lesson in Lesson.objects.filter(p=unit): 
                lpercent = 0 
                if user :
                    lpercent = LessonEval.objects.get(user=user, k=lesson).percent
                    if lpercent < 70: 
                        weaknesses += [[lesson.k, lpercent, lesson.name, unit.name]] 
                lessons += [{'title':lesson.name, 'file':lesson.file.name, 'video':lesson.video, 'lpercent':lpercent, 'k':lesson.k}]
            units += [{'title':unit.name, 'upercent': upercent, 'lessons':lessons, 'k':unit.k,}]
        weaknesses = sorted(weaknesses)
        weaknesses = [{'percent':w[1], 'l':w[2], 'u':w[3]} for w in weaknesses]
        context = {'teacher': is_teacher(request), 'auth':request.user.is_authenticated, 'k':subject.k, 'sname':subject.name, 'spercent':spercent, 
                'units':dumps(units), 'weaknesses':weaknesses}
        return render (request,'courses/subject.html', context)

#_________________________________________________________________________________________

def pract_order(lesson_qs): 
    questions = []            
    for f in [1,0]: 
        for l in ['1','2','3']: 
            for r in ['exam','book','other']:
                questions += [L for L in lesson_qs if L[0].source==r and L[0].level==l and L[1].flag==f and L[1].score==-1] 
    for f in [1,0]: 
        for s in [0,1]:
            for l in ['1','2','3']: 
                for r in ['exam','book','other']:
                    questions += [L for L in lesson_qs if L[0].source==r and  L[0].level==l and L[1].flag==f and L[1].score==s]
    return questions 


def assessment_order(lesson_qs):     
    l1, l2, l3 = [],[],[] 
    for L in lesson_qs:
        q = L[0] 
        if q.level == '1': 
            l1 += [L]
        elif q.level == '2': 
            l2 += [L] 
        else : 
            l3 += [L] 
    def split_for_test(l):
        t0, t1 = [],[]
        for L in l: 
            if L[1].score != 1: 
                t0 += [L]
            else: 
                t1 += [L] 
        return t0 + t1
    shuffle(l1)
    shuffle(l2)
    shuffle(l3)
    questions = split_for_test(l2)+split_for_test(l1)+split_for_test(l3)
    return questions


def updatePercents(lessons , user): 
    lessons = [Lesson.objects.get(k=k) for k in lessons]
    units = [] 
    for lesson in lessons : 
        Eval = LessonEval.objects.get(k=lesson, user=user)
        if Eval.total > 0: 
            Eval.percent = int(round(Eval.score/Eval.total*100))
            Eval.save()
            if not lesson.p in units : 
                units += [lesson.p] 
    for unit in units : 
        percent = 0 
        for lesson in Lesson.objects.filter(p=unit): 
            percent += LessonEval.objects.get(k=lesson, user=user).percent*lesson.w 
        Eval = UnitEval.objects.get(k=unit, user=user)
        Eval.percent = int(round(percent,0))
        Eval.save()

    units = Unit.objects.filter(p=lesson.s)
    percent = 0 
    for unit in units : 
        percent += UnitEval.objects.get(k=unit, user=user).percent*unit.w 
    Eval =SubjectEval.objects.get(k=lesson.s, user=user)
    Eval.percent = int(round(percent,0))
    Eval.save()

    subjects = Subject.objects.filter(p=lesson.y)
    percent = 0 
    for subject in subjects: 
        percent += SubjectEval.objects.get(k=subject, user=user).percent
    Eval = YearEval.objects.get(k=lesson.y, user=user)
    Eval.percent = int(round(percent/len(subjects),0))
    Eval.save()
    


    
        

def user_questions(request, lesson_qs, purpose): 
    auth = request.user.is_authenticated
    if auth:    
        user = request.user        
        lesson_qs = [[q, QEval.objects.get(k=q, user=user)] for q in lesson_qs]             
        if purpose == 'pract':     
            lesson_qs = pract_order(lesson_qs)            
        else :
            lesson_qs = assessment_order(lesson_qs)
    else: 
        lesson_qs = lesson_qs[0]
    return lesson_qs


def gatherQuestions(request, lessons, purpose): 
    lessons = [Lesson.objects.get(k=k) for k in lessons]
    nlessons = len(lessons)
    wts = [len(Question.objects.filter(p=lesson)) for lesson in lessons]
    wtot = sum(wts)
    wts = [round(w/wtot,3) for w in wts]
    nqtot = min(5+40*log(nlessons,50), 50)
    questions = [] 
    for i in range(nlessons): 
        lesson = lessons[i]       
        lesson_qs = [q for q in Question.objects.filter(p=lesson)]
        lesson_qs = user_questions(request, lesson_qs, purpose) 
        if purpose == 'test': 
            print ()
            quota = int(wts[i]*nqtot)
            nqs = max(quota,1)
            lesson_qs = lesson_qs[:nqs]
        questions += lesson_qs          
    return questions


def MakeQuestions(request, lessons, purpose): 
    auth = request.user.is_authenticated
    questions = gatherQuestions(request, lessons, purpose)    
    JQuestions = []
    fullMark = 0 
    for que in questions:        
        flag, score = 0,0 
        if auth: 
            [q,eval] = que
            flag, score = eval.flag, eval.score 
            ds = [q]+[i for i in QDubl.objects.filter(p=q)]
            shuffle(ds)
            a = ds[0]   
        else : 
            q, a = que , que      
        d = {'k':q.k, 'file':'', 'ansimg':'', 'video':'', 'hint':'',
                'choice':'', 'delay':0, 'flagged':'', 
                'flag':flag, 'score':score, 'source':q.source, 'kind':q.kind, 
                'q_question':q.name, 'q_img':''} 
        if q.file: 
            d['q_img'] = q.file.name      
        d['question'] = a.name
        if a.file: 
            d['file'] = a.file.name
        if a.ansimg: 
            d['ansimg'] = a.ansimg.name
        if q.hint: 
            d['hint'] = [h for h in q.hint.split('..')]
        if q.video: 
            d['video'] = q.video
        if a.op2:            
            options = [a.op1, a.op2]
            if a.op3: options+=[a.op3]
            if a.op4: options += [a.op4]
            shuffle(options)
            d['correct'] = str(options.index(a.op1)) 
            d['options'] = options   
            fullMark += 1  
            if purpose == 'test':  
                Eval = LessonEval.objects.get(k=q.p, user=request.user) 
                Eval.total += 1
                Eval.save()                       
        else: 
            d['answer'] = a.op1            
            d['options'] = ['1','0']
            d['correct'] = '0' 
        JQuestions += [d] 
    request.session['questions'] = JQuestions 
    return dumps(JQuestions)


def updateQScores(request, test): 
    user = request.user
    submitted = request.POST.get('submitted')
    submitted = submitted.split(',')
    if submitted != ['']: 
        sL = len(submitted)    
        questions = request.session['questions']
        if len(questions) == sL:     # i.e. came from result display page which (may) contain flags only
            for j in range(sL): 
                question = Question.objects.get(k=questions[j]['k'])   
                qEval = QEval.objects.get(k=question, user=user)
                qEval.flag = int(submitted[j])
                qEval.save()
        else:                        # i.e. came from pract and test which contains choices and flags 
            for j in range(0, sL, 2): 
                i = int(j/2)
                question = Question.objects.get(k=questions[i]['k'])   
                qEval = QEval.objects.get(k=question, user=user)
                flag = int(submitted[j+1])
                qEval.flag = flag
                if test: 
                    questions[i]['flag'] =  flag
                if submitted[j]: 
                    questions[i]['choice'] = submitted[j] 
                    if questions[i]['choice'] == questions[i]['correct'] :
                        qEval.score = 1                        
                        if test and question.op2:
                            Eval = LessonEval.objects.get(k=question.p, user=user) 
                            Eval.score += 1
                            Eval.save()
                    else: 
                        qEval.score = -1
                qEval.save()     
            if test:
                return questions, 1 
    return 0,0

def Practice(request, k):    
    if request.POST: 
        if request.user.is_authenticated:  
            updateQScores(request, 0)             
        return redirect('subject', k)    
    else: 
        selectedlessons = request.session['selectedlessons']        
        questions  = MakeQuestions(request, selectedlessons, 'pract')   
        if not questions : 
            HttpResponse('لم يتم إعداد أسئلة بعد لهذا المحتوى')
        context = {'k':k, 'questions':questions, 'purpose':'pract', 'auth':request.user.is_authenticated}    
    return render (request,'courses/practice.html', context)

    def calcPercent(user, k) :   
        b = k[0]   
        Obj, Modeval = Mod[b], MEval[b]
        object = Obj.objects.get(k=k)
        Eval = Modeval.objects.get(k=object, user=user)      
        score, total, freq, percent = Eval.score, Eval.total, Eval.freq, 0   
        if total > 0 and score > 0:      
            percent = 100*score/total+1
        if b in ['s','u','l']: 
            c = csymbol[b]
            midObj, midEval = Mod[c], MEval[c]  
            midpercents = [midEval.objects.get(k=midobj, user=user).percent*midobj.w for midobj in midObj.objects.filter(p=object)]
            midpercent = 0 
            midpercent = sum(midpercents)
            # if len(midpercents) : 
            #     midpercent = sum(midpercents)/len(midpercents)
            
            percent = 0.4*midpercent+0.6*percent
        if freq  == 1 :
            percent = min(percent, 70) 
        elif freq > 2 :
            percent = min(100, percent + 2) 
        Eval.percent = min(int(round(percent)), 100)
        Eval.save()
        return object.p.k 
    while k[0] in ['o','l','u','s'] :   
        k = calcPercent(user, k) 
    if k[0] == 'y': 
        year = Year.objects.get(k=k)
        Eval = YearEval.objects.get(k=year, user=user) 
        subpercents = [SubjectEval.objects.get(k=s, user=user).percent for s in Subject.objects.filter(p=year)]
        subEval = 0 
        if subpercents :
            subEval = sum(subpercents)/len(subpercents)
        Eval.percent = int(round(subEval)) 
        Eval.save()

def Assessment(request, k):      
    if request.POST:  
        questions, result = updateQScores(request, 1)    
        if result:  
            selectedlessons = request.session['selectedlessons']
            updatePercents(selectedlessons , request.user)       
            context = {'k':k, 'questions':dumps(questions), 'purpose':'result'}
            return render (request,'courses/practice.html', context)
        else:
            return redirect('subject', k)   
    else:   
        selectedlessons = request.session['selectedlessons']        
        questions  = MakeQuestions(request, selectedlessons, 'test')       
        updatePercents(selectedlessons , request.user)                        
        context = {'k':k, 'questions':questions, 'purpose':'test', 'auth':request.user.is_authenticated}      
        return render (request,'courses/practice.html', context)


def Result(request): 
    return render (request,'courses/practice.html')

