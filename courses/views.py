from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import * 
from .forms import *
from json import dumps
from random import shuffle
from django.core.mail import send_mail
from django.conf import settings



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


def HomePage(request):       
    if request.method == 'POST':   
        if "visitor" in request.POST:            
            y = request.POST.get('year') 
            year = Year.objects.get(name=y)
            return redirect('open', year.k)     
            
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
            return redirect('open', Year.objects.get(name=y).k)


@login_required(login_url='login')
def Logout(request):
    logout(request)
    return redirect('home')


Mod = {'y':Year, 's':Subject, 'u':Unit, 'l':Lesson, 'o':Outcome, 'q':Question, 'd':QDubl}
MEval = {'y':YearEval, 's':SubjectEval, 'u':UnitEval, 'l':LessonEval, 'o':OutcomeEval, 'q':QEval}
csymbol = {'h':'y', 'y':'s', 's':'u', 'u':'l', 'l':'o', 'o':'q', 'q':'d'}
psymbol = {'h':'h', 'y':'h', 's':'y', 'u':'s', 'l':'u', 'o':'l', 'q':'o', 'd':'q'}
ara = {'h':'الصفحة الرئيسية', 'y':'صف', 's':'مادة', 'u':'وحدة', 'l':'درس', 'o':'هدف', 'q':'سؤال', 'd':'سؤال'}
contents = {'h':'الصفوف الدراسية', 'y':'المواد الدراسية', 's':'وحدات المادة', 'u':'دروس الوحدة', 'l':'الأهداف التعليمية'}


def Object(request, k):    
    b = k[0]      
    if b == 'h': 
        return redirect('home')
    else:   
        c,p = csymbol[b], psymbol[b]     
        user = 0
        if request.user.is_authenticated : 
            user = request.user    
            Eval = MEval[b]   
        object = Mod[b].objects.get(k=k)
        context = {'teacher': is_teacher(request),'auth':user, 'object':object, 'k':k, 'b':b, 
                   'name':object.name, 'ara':ara[b], 'para':ara[p], 'cara':ara[c]}     
        if user: 
            user_eval = Eval.objects.get(k=object, user=user).percent  
            context['percent'] = user_eval     
        if b == 'y': 
            nD = {'5':'خامس', '6':'سادس', '7':'سابع', '8':'ثامن', 
                  '9':'تاسع', '10':'عاشر', '11':'حادي عشر', '12':'ثاني عشر'}
            context['name'] = nD[object.name]
            outstandings = []  
            ordered = YearEval.objects.filter(k=object).order_by('-percent')      
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
            context['outstandings'] = outstandings                  
            if user:               
                context['user_rank'] = ordered_percents.index(user_eval)+1
        else : 
            context['p']= object.p.k
            context['parent'] = object.p.name
            if b == 's' and user: 
                weaknesses = [] 
                for outcome in Outcome.objects.filter(s=object):
                    opercent = OutcomeEval.objects.get(k=outcome, user=user).percent 
                    if opercent < 70: 
                        weaknesses += [[opercent, outcome.k, outcome.name]] 
                weaknesses = sorted(weaknesses)
                weaknesses = [{'percent':w[0], 'wk':w[1], 'name':w[2]} for w in weaknesses]
                context['weaknesses'] = weaknesses        
        if b == 'o':   
            # context['content'] = dumps([n for n in object.content.split('..')]) 
            questions = []
            for question in Question.objects.filter(p=object) :   
                qD = {'q':question, 'name':[n for n in question.name.split('..')]}
                if question.hint: 
                    qD['hint'] = [n for n in question.hint.split('..')]  
                questions += [qD]   
                for d in QDubl.objects.filter(p=question): 
                    questions += [{'q':d, 'name':[n for n in d.name.split('..')]}] 
            context['questions'] = questions
            return render (request,'courses/outcome.html', context)    
        else:
            context['contents'] = contents[b] 
            children = []  
            for child in Mod[c].objects.filter(p=object): 
                cpercent = 0 
                if user: 
                    cpercent = MEval[c].objects.get(k=child, user=user).percent                    
                children += [{'c':child, 'percent':cpercent}]                       
            context['children'] = children
            return render (request,'courses/object.html', context)

#_________________________________________________________________________________________

def pract_order(outc_qs): 
    questions = []            
    for f in [1,0]: 
        for l in ['1','2','3']: 
            for r in ['exam','book','other']:
                questions += [L for L in outc_qs if L[0].source==r and L[0].level==l and L[1].flag==f and L[1].score==-1] 
    for f in [1,0]: 
        for s in [0,1]:
            for l in ['1','2','3']: 
                for r in ['exam','book','other']:
                    questions += [L for L in outc_qs if L[0].source==r and  L[0].level==l and L[1].flag==f and L[1].score==s]
    return questions 


def assessment_order(outc_qs):  
    l1, l2 = [],[] 
    for L in outc_qs:
        q = L[0] 
        if q.level == '1': 
            l1 += [L]
        elif q.level == '2': 
            l2 += [L]                 
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
    questions = split_for_test(l1)+split_for_test(l2)
    return questions


def user_questions(request, outc_qs, purpose): 
    auth = request.user.is_authenticated
    if auth:    
        user = request.user  
        outc_qs = [[q, QEval.objects.get(k=q, user=user)] for q in outc_qs]        
        if purpose == 'pract':     
            outc_qs = pract_order(outc_qs)            
        else :
            outc_qs = assessment_order(outc_qs)
    else: 
        outc_qs = [outc_qs[0]]
    return outc_qs


def gatherQuestions(request, k, purpose): 
    b = k[0]
    object = Mod[b].objects.get(k=k)    
    questions = [] 
    if b == 'o': 
        outcomes = [object] 
    else:         
        if b == 'l':
            outcomes = [o for o in Outcome.objects.filter(p=object)] 
        else: 
            if b == 'u' : 
                outcomes = [o for o in Outcome.objects.filter(u=object)] 
            elif b == 's' : 
                outcomes = [o for o in Outcome.objects.filter(s=object)] 
    nqsD = {'o':10000, 'l':10, 'u':5, 's':2}
    if purpose == 'test': 
        nqsD = {'o':10000, 'l':5, 'u':2, 's':1}
    nq = nqsD[b]
    for outc in outcomes: 
        outc_qs = [q for q in Question.objects.filter(p=outc)]
        outc_qs = user_questions(request, outc_qs, purpose) 
        # shuffle(outc_qs) 
        questions += outc_qs[:nq]             
    return questions


def MakeQuestions(request, k, purpose): 
    auth = request.user.is_authenticated
    questions = gatherQuestions(request, k, purpose)    
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
        else: 
            d['answer'] = a.op1            
            d['options'] = ['1','0']
            d['correct'] = '0' 
        JQuestions += [d] 
    request.session['questions'] = JQuestions 
    if purpose == 'test':
        return dumps(JQuestions), fullMark
    else: 
        return dumps(JQuestions)


def updateScores(request, test): 
    user = request.user
    submitted = request.POST.get('submitted')
    submitted = submitted.split(',')
    if submitted != ['']: 
        sL = len(submitted)    
        questions = request.session['questions']
        if len(questions) == sL: 
            for j in range(sL): 
                question = Question.objects.get(k=questions[j]['k'])   
                newEval = QEval.objects.get(k=question, user=user)
                newEval.flag = int(submitted[j])
                newEval.save()
            return 0, 0, 0
        else: 
            real_score = 0
            for j in range(0, sL, 2): 
                i = int(j/2)
                question = Question.objects.get(k=questions[i]['k'])   
                newEval = QEval.objects.get(k=question, user=user)
                flag = int(submitted[j+1])
                newEval.flag = flag
                if test: 
                    questions[i]['flag'] =  flag
                if submitted[j]: 
                    questions[i]['choice'] = submitted[j]  
                    if questions[i]['choice'] == questions[i]['correct'] :
                        newEval.score = 1
                        if test and question.op2:
                            real_score += 1
                    else: 
                        newEval.score = -1
                newEval.save()        
            if test:
                return real_score, questions, 1 
    return 0, 0, 0


def Practice(request, k):    
    if request.POST: 
        if request.user.is_authenticated:  
            updateScores(request, 0)             
        return redirect('open', k)    
    else: 
        b=k[0]
        object = Mod[b].objects.get(k=k) 
        questions  = MakeQuestions(request, k, 'pract')   
        if not questions : 
            HttpResponse('لم يتم إعداد أسئلة بعد لهذا المحتوى')
        context = {'name':object.name, 'k':k, 'ara':ara[b], 
                   'questions':questions, 'purpose':'pract', 'auth':request.user.is_authenticated}    
    return render (request,'courses/practice.html', context)


def updatePercent(user,k):     
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
            if len(midpercents) : 
                midpercent = sum(midpercents)/len(midpercents)
            percent = 0.4*midpercent+0.6*percent
        if freq  == 1 :
            percent = min(percent, 70) 
        elif freq == 2 : 
            percent = min(percent, 90)
        elif freq > 3 :
            percent = min(100, percent + min(freq,3)) 
        Eval.percent = int(round(percent))
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
    user = request.user
    b = k[0]
    object = Mod[b].objects.get(k=k)  
    objectEval = MEval[b].objects.get(k=object, user=user)
    if request.POST:  
        real_score, questions, result = updateScores(request, 'test')    
        if result:      
            objectEval.score += int(real_score)  
            objectEval.freq += 1
            objectEval.save()
            updatePercent(user,k)
            context = {'k':k, 'name':object.name, 'ara':ara[b], 'questions':dumps(questions), 'purpose':'result'}
            return render (request,'courses/practice.html', context)
        else:
            return redirect('open', k)   
    else:                                 
        questions, fullMark = MakeQuestions(request, k, 'test')              
        objectEval.total += fullMark        
        objectEval.save()        
        updatePercent(user,k)         
        context = {'name':object.name, 'k':k, 'ara':ara[b],  'questions':questions, 'purpose':'test'}      
        return render (request,'courses/practice.html', context)


def Result(request): 
    return render (request,'courses/practice.html')

