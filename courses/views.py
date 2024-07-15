from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import * 
from .forms import *
from json import dumps
from random import shuffle
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
import os, shutil
from django.conf import settings
from math import sqrt, tan, sin, cos, pi





def auth(request):
    return request.user.is_authenticated

def is_teacher(request): 
    if auth(request) :   
        if request.user.email in  ['biifounder@gmail.com','bahaaismailres@gmail.com'] : 
            return request.user.username 
    return False

def deleteAll():
    for Mod in [QDubl, QEval, Question, OutcomeEval, Outcome, LessonEval, Lesson, 
                UnitEval, Unit] : 
        Mod.objects.all().delete()

#======================================================================================================
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

def HomePage(request):  
    # deleteAll()
    # AddUser(request,Year.objects.get(name='10'))     
    if request.method == 'POST':   
        if "visitor" in request.POST:            
            y = request.POST.get('year') 
            year = Year.objects.get(name=y)
            return redirect('open', year.k)     
            
        elif "register" in request.POST:          
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


table = {
    'h':[ 'y' , '',   ''       ,  ''          ,  'الصفحة الرئيسية' ,  'الصفوف الدراسية' ],
    'y':[ 's' , 'h',   Year     ,  YearEval    ,  'صف'               ,  'المواد الدراسية' ],
    's':[ 'u' , 'y',   Subject  ,  SubjectEval ,  'مادة'             ,  'وحدات المادة'    ],
    'u':[ 'l' , 's',  Unit     ,  UnitEval    ,  'وحدة'             ,  'دروس الوحدة'     ],
    'l':[ 'o' , 'u',  Lesson   ,  LessonEval  ,  'درس'              ,  'الأهداف التعليمية في هذا الدرس'    ],
    'o':[ 'q' , 'l',  Outcome  ,  OutcomeEval ,  'مخرج'             ,  ''                 ],
    'q':[ 'd'  , 'o',  Question ,  QEval          ,  'سؤال '            ,  ''                 ],
    'd':[ ''  , 'q',  QDubl ,  ''          ,  'سؤال '            ,  ''                 ],
}


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
            ordered = ordered[:5]
            for ord in ordered: 
                out = ord.user
                outstandings += [{'rank':ord.percent,'name': out.name, 'school':out.school, 'prov': out.prov, 'gov': out.gov, 'percent':ord.percent}]
            context['outstandings'] = outstandings            
            if user:
                ordered = [ord.percent for ord in ordered]
                context['user_rank'] = ordered.index(user_eval)+1
        else : 
            context['p']= object.p.k
            context['parent'] = object.p.name
            if b == 's' and user: 
                weaknesses = [] 
                for outcome in Outcome.objects.filter(s=object):
                    opercent = OutcomeEval.objects.get(k=outcome, user=user).score 
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
    if abs(num) < 0.001 or num > 1000: 
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
        un = '\\ '.join(un.split())
        num += '\ \mathrm{'+un+'}'
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

 

#_________________________________________________________________________________________


def gatherQuestions(k): 
    b = k[0]
    object = Mod[b].objects.get(k=k)    
    questions = [] 
    if b == 'o': 
        questions = [q for q in Question.objects.filter(p=object)] 
    else:         
        if b == 'l':
            outcomes = [o for o in Outcome.objects.filter(p=object)] 
        else: 
            if b == 'u' : 
                outcomes = [o for o in Outcome.objects.filter(u=object)] 
            elif b == 's' : 
                outcomes = [o for o in Outcome.objects.filter(s=object)] 
        nqsD = {'l':5, 'u':3, 's':1}
        nq = nqsD[b]
        for outc in outcomes: 
            outc_qs = [q for q in Question.objects.filter(p=outc)]
            shuffle(outc_qs) 
            questions += outc_qs[:nq]             
    return questions

def MakeQuestions(request, k, purpose): 
    questionL = gatherQuestions(k)    
    auth = request.user.is_authenticated
    if auth:    
        user = request.user    
        questionL = [[q, QEval.objects.get(k=q, user=user)] for q in questionL]        
        if purpose == 'pract':             
            questions = []            
            for f in [1,0]: 
                for l in ['1','2','3']: 
                    for r in ['exam','book','other']:
                        questions += [L for L in questionL if L[0].source==r and L[0].level==l and L[1].flag==f and L[1].score==-1] 
            for f in [1,0]: 
                for s in [0,1]:
                    for l in ['1','2','3']: 
                        for r in ['exam','book','other']:
                            questions += [L for L in questionL if L[0].source==r and  L[0].level==l and L[1].flag==f and L[1].score==s]
        else :
            nqs = len(questionL)  
            n = int(nqs/3)     
            l1, l2 = [],[] 
            for L in questionL:
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
            questions = split_for_test(l1)[:n]+split_for_test(l2)[n:nqs] 
    else: 
        questions = questionL[:3]

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
                'flag':flag, 'score':score, 'source':q.source, 'kind':q.kind} 
        
        d['question'] = a.name
        if a.file: 
            d['file'] = a.file.name
        if a.ansimg: 
            d['ansimg'] = a.file.name

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



dnqs = {'s':2, 'u':2, 'l':2, 'o':2}
def updatePercent(user,k):     
    def calcPercent(user, k) :   
        b = k[0]   
        [Obj, Modeval] = table[b][2:4] 
        object = Obj.objects.get(k=k)
        Eval = Modeval.objects.get(k=object, user=user)      
        score, total, freq, percent = Eval.score, Eval.total, Eval.freq, 0   
        if total > 0 and score > 0:      
            percent = 100*round(score/total,2)+1
        if b in ['s','u','l']: 
            c = csymbol[b]
            [midObj, midEval] = table[c][2:4]   
            midevals = [midEval.objects.get(k=m, user=user) for m in midObj.objects.filter(p=object)] 
            midpercents = [meval.percent for meval in midevals]
            midpercent = 0 
            if midpercents:                 
                midpercent = sum(midpercents)/len(midpercents)
            percent = 0.4*midpercent+0.6*percent
        if freq  == 1 : 
            percent = min(percent, 85)
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
            objectEval.save()
            updatePercent(user,k)
            context = {'k':k, 'name':object.name, 'ara':ara[b], 'questions':dumps(questions), 'purpose':'result'}
            return render (request,'courses/practice.html', context)
        else:
            return redirect('open', k)   
    else:                                 
        questions, fullMark = MakeQuestions(request, k, 'test')              
        objectEval.total += fullMark
        objectEval.freq += 1
        objectEval.save()        
        updatePercent(user,k)         
        context = {'name':object.name, 'k':k, 'ara':ara[b],  'questions':questions, 'purpose':'test'}      
        return render (request,'courses/practice.html', context)


def Result(request): 
    return render (request,'courses/practice.html')
























#=======================================================================================================

# def deleteAll():
#     for Mod in [YearEval, SubjectEval, UnitEval, LessonEval, OutcomeEval, QEval] : 
#         Mod.objects.all().delete()
#     for Mod in [Year, Subject, Unit, Lesson, Outcome, Question, QDubl] : 
#         Mod.objects.all().delete()

# def zeroEvals(ModEval): 
#     for Eval in ModEval.objects.all():
#         Eval.score = 0
#         Eval.flag = 0
#         Eval.total = 0
#         Eval.percdnt = 0        
#         Eval.save()

# from pandas to Model
    # import pandas as pd    
    # School.objects.all().delete()
    # df = pd.read_csv('schools.csv')
    # for index, row in df.iterrows():
    #     print(row['school'], row['province'], row['governorate'])
    #     School.objects.create(school=row['school'], prov=row['province'], gov=row['governorate'])
        # print(row)
    # for s in School.objects.filter(prov='البريمي'): 
    #     print(s.school)

# def weeklyReport() 
    # for user in User.objects.all(): 
        # email_subject = 'التقرير الأسبوعي من المؤسس التفاعلي'
        # message = ''
        # for subject in user.subjects.all() : 
        #     percent = str(SubjectEval.objects.get(k=subject.k, user=request.user).percent)
        #     message += 'Yout score in ' + subject.name + ' is ' + percent + '%'
        # EmailSender(email_subject, message, [user.email])


# for subject in Subject.objects.all(): 
#     for user in subject.users.all(): 
#         user.subjects.add(subject)
#     print(subject.k,subject.users.all())

# for user in User.objects.all(): 
#     print(user.subjects.all())


# def equation_tex(txt):
#     latins = ['alpha', 'beta', 'gamma', 'delta', 'theta', 'omega', 'lambda', 'rho', 'pi']
#     equations = txt.split('$')[1:-1]
#     equations = [q for q in equations if '!' in q]
#     for q in equations :
#         eq = q.strip('$').strip('!')
#         eq = eq.replace('*',' \\times ').replace('sqrt','\sqrt')
#         for lat in latins:
#             if lat == 'rho':
#                 eq = eq.replace(lat,'\\\\'+lat)
#             else:
#                 eq = eq.replace(lat,'\\'+lat)            
#         if '/' in eq :
#             fracs = eq.split()
#             fracs = [f for f in fracs if '/' in f]
#             new_fracs = ['\\frac {'+f.replace('/','}{')+'}' for f in fracs]
#             for i in range(len(fracs)):
#                 eq = eq.replace(fracs[i], new_fracs[i])
#         eq = '\(  ' + eq + '  \)' 
#         txt = txt.replace(q,eq)
#     txt = txt.strip('$')
#     return txt 