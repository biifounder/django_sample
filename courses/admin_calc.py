from django.shortcuts import render
from random import shuffle
from django.conf import settings
from .views import is_teacher
import re
from random import uniform, shuffle



def texpy(txt):
    txt = txt.replace('frac{','(').replace('sqrt{','(').replace('}{',')/(').replace('}',')').replace('^','**')
    return txt

def fixtex(txt):
    txt = txt.replace('frac',r'\frac').replace('sqrt',r'\sqrt').replace('3.14', 'pi').replace('/','}{')
    txt = txt.replace('pi',r'\pi').replace('phi',r'\phi').replace('rho',r'\rho').replace('Omega',r'\Omega').replace('del',r'\Delta')
    txt = txt.replace('pm',r'\pm').replace('circ',r'\circ').replace('%',r'\%')
    txt = txt.replace('e+','e').replace('e0','e').replace('e-0','e-')
    txt = txt.replace('\mathrm{%}','\%')
    txt = re.sub(r'(\d+(\.\d+)?e[+-]?\d+)', lambda x: x.group().replace('e', ' \\times 10^{') + '}', txt)    
    return txt

def unit(unit):
    unit = r' \ '.join(unit.split())
    unit = re.sub(r'\^(-?\d+)', r'^{\1}', unit)
    return r' \ \mathrm{'+unit+'}'


def base10(num):
    if abs(num) < 0.001 or abs(num) > 1000: 
        num = "{:.2e}".format(num)
    elif len(str(num)) > 3:
        num = float("{:.3g}".format(num))
    tex_num = fixtex(str(num))
    return tex_num, num

def value(txt):    
    txt = texpy(txt)
    txt = float(eval(txt))
    tex_num, num = base10(txt)       
    return tex_num, str(num)

def numsym(item , values):
    new = item.replace('sqrt','$').replace('dfrac','@').replace('frac','!')
    for v in values :
        new = new.replace(v, values[v])
    new = new.replace('$','sqrt').replace('@','dfrac').replace('!','frac')
    return new


def given(entries):
    entries += ', G = 6.67e-11 un N m^2 kg^-2, pi = 3.14'
    entries = entries.split(',')    
    values = {}
    for ent in entries:
        ents = ent.split('=')
        unk = ents[0]
        un = ''
        if 'un' in ents[1] : 
            [num , un] = ents[1].split('un')
            un = unit(un)
        else: 
            num = ents[1]
        values[unk.strip()] = num.strip()
        num = fixtex(num)      
    return values 



def optr(txts):
    txts = txts.split(',')
    results = [] 
    for txt in txts:
        txt = txt.split('un')
        num, _ = base10(float(txt[0]))            
        if len(txt) == 2 :
            un = unit(txt[1])
            num = num + un
        num = r'\('+ num + r' \)'
        num = num.replace('\mathrm{%}','\%')
        results += [num + ' .. ']
    correct = float(txts[0].split('un')[0])
    if 'un' in txts[0]:
        un = unit(txts[0].split('un')[1])    
    for i in range(len(txts), 4): 
        rnds = [uniform(0.1*correct,0.5*correct), uniform(1.5*correct,2*correct), uniform(4*correct,10*correct)]
        shuffle(rnds)
        num, _  = base10(rnds[0])
        if 'un' in txts[0]:
            num = num + un
        num = r'\('+ num + r' \)'
        num = num.replace('\mathrm{%}','\%')
        if i < 3 :
            num = num
        results += [num + ' .. ']
    return results

def optf(txts):
    txts = txts.split(',')
    options = ''
    for txt in txts :
        txt = txt.split('un')
        num = value(txt[0])
        if len(txt) == 2 :
            num = num + ' un ' + txt[1]
        options += num+ ' , '
    options = options.strip(', ')
    results = optr(options)
    return results


values = {}
def steps(txts, values=values): 
    txts = txts.split(',')
    expressions = [] 
    for txt in txts:
        parts= txt.split('=')
        unk = parts[0].strip() 
        for i in range(len(parts)) :
            step = parts[i]
            if 'rep' in step : 
                torep = step.split('rep')[0]
                if '=' in torep: 
                    torep = torep.split('=')[-1]
                reped = numsym(torep, values)
                txt = txt.replace('rep' , ' = ' +reped)
                step = step.replace('rep' , ' = ' +reped)
            if 'val' in step :               
                vals = step.split('val')                
                toval = vals[0]             
                if '=' in toval: 
                    toval = toval.split('=')[-1]
                valed, pyval = value(toval)
                values[unk] = pyval
                if vals[1] : 
                    valed = valed + unit(vals[1]) 
                txt = txt.replace('val','').replace(vals[1],' = ' +valed)
            if 'un' in step : 
                un = step.split('un')[1]
                new = unit(un) 
                txt = txt.replace('un','').replace(un, new) 
        txt = fixtex(txt)
        txt = txt.replace('\mathrm{%}','\%')
        expressions += [r'\[' + txt + r'\]']
    return expressions

def expression(txts, values=values): 
    txts = txts.split(',')
    expressions = [] 
    for txt in txts:
        parts= txt.split('=')
        unk = parts[0].strip() 
        for i in range(len(parts)) :
            step = parts[i]
            if 'rep' in step : 
                torep = step.split('rep')[0]
                if '=' in torep: 
                    torep = torep.split('=')[-1]
                reped = numsym(torep, values)
                txt = txt.replace('rep' , ' = ' +reped)
                step = step.replace('rep' , ' = ' +reped)
            if 'val' in step :               
                vals = step.split('val')                
                toval = vals[0]             
                if '=' in toval: 
                    toval = toval.split('=')[-1]
                valed, pyval = value(toval)
                values[unk] = pyval
                if vals[1] : 
                    valed = valed + unit(vals[1]) 
                txt = txt.replace('val','').replace(vals[1],' = ' +valed)
            if 'un' in step : 
                un = step.split('un')[1]
                new = unit(un) 
                txt = txt.replace('un','').replace(un, new) 
        txt = fixtex(txt)
        txt = txt.replace('frac','dfrac')
        txt = txt.replace('\mathrm{%}','\%')
        expressions += [r'\(' + txt + r'\)']
    return expressions

def Solve(request): 
    if request.method == 'POST':   
        context = {'teacher':is_teacher(request)}
        if request.POST.get('py_values'):    
            py_values = request.POST.get('py_values')   
            context['py_values'] = py_values
            values = given(py_values)
        else: 
            values = {}
        
        if request.POST.get('py_forms'):                 
            py_forms = request.POST.get('py_forms')   
            context['py_forms'] = py_forms 
            if "steps" in request.POST:   
                context['tex_forms'] = steps(py_forms, values)
            elif "exps" in request.POST: 
                context['tex_forms'] = expression(py_forms, values) 
            elif "optfs" in request.POST:  
                context['tex_forms'] = optf(py_forms, values)    
            elif "optrs" in request.POST:  
                context['tex_forms'] = optr(py_forms)      
        if request.POST.get('clipboard'): 
            context['clipboard'] = request.POST.get('clipboard')
        return render(request, 'courses/solve.html', context)
    else: 
        context = {'teacher':is_teacher(request)}
        return render(request, 'courses/solve.html', context)
