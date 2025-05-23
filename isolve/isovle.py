# isolve
'''
- converts given quantities and units to tex format
- converts simple python formula to tex formula
- solves equations
- provides 4 options for problems 
'''



import re



qu = '5e10^3 m s^2'
qu = '6.022e23 mol^-1'
qu = '5e10 m s^-2'
qu = '25 m s^-1'
import re

def exptex(text):
    # fix exponents
    text = re.sub(r'([\-+]?\d*\.?\d+)[eE]([\-+]?\d+)', r'\1 \\times 10^{\2}', text)
    text = re.sub(r'\^(-?\d+)', r'^{\1}', text)
    return text

def qutex(text):
    # fix quantity and unit
    text = text.strip()
    pattern = r"^([\d\.\*\s\^eE\+\-\/\(\)]+)\s*([a-zA-Z\\/\*\^\-\d\s]*)$"
    match = re.match(pattern, text)
    [q, u] = match.group(1) , match.group(2)
    q = exptex(q)
    u = exptex(u)
    return (r'\( ' + q + r' \ \mathrm{'+u+r'}\) ')


def pytex(formula):
    # converts python formula to tex formula
    formula = formula.replace('sqrt',r'\sqrt').replace('3.14', 'pi')
    formula = formula.replace('pi',r'\pi').replace('phi',r'\phi').replace('rho',r'\rho').replace('ohm',r'\Omega').replace('del',r'\Delta')
    formula = formula.replace('pm',r'\pm').replace('circ',r'\circ').replace('%',r'\%')
    formula = formula.replace(r'\mathrm{%}',r'\%')
    forms = formula.split('=')
    for form in forms :
        if '/' in form :
            new = r'\dfrac{'+form.replace('/','}{').strip()+'}'
            formula = formula.replace(form, new)
    formula = r'\( ' + formula + r' \)'
    return formula
            

given = 'E = 5 W, I = 3 A, t = 40 s'
formula = 'V = E/(It) = rep = val = V'
def solve(given='', formula=''):
    given = given.split(',')
    givens = {}
    for giv in given :
        giv = giv.split('=')
        givens[giv[0].strip()] = giv[1].strip()
    if 'rep' in formula:
        forms = formula.split('=')
        forms = [f.strip() for f in forms]
        i = forms.index('rep')-1
        form = forms[i]
        for f in form:
            if f in givens:
                form = form.replace(f, givens[f])
        formula = formula.replace('rep', form)
    if 'val' in formula :
        forms = formula.split('=')
        forms = [f.strip() for f in forms]
        i = forms.index('val')-1
        if len(forms) == i + 3 :
            unit = forms[-1]
            formula = ' = '.join(forms[:-1]) + ' ' + unit
        form = forms[i]
        out = eval(form)
        if float(out) == int(out):
            out = int(out)
        else :
            out = round(out,1)        
        formula = formula.replace('val', str(out))
        formula = pytex(formula).replace(r'\(',r'\[').replace(r'\)',r'\]')        
                
        nums = [float(givens[g]) for g in givens]
        options = [nums[0] * nums[1]]
        if nums[0] != 0 :
            options += [nums[1]/nums[0]]
        if nums[1] != 0 :
            options += [nums[0]/nums[1]]
        options += [sum(options)/len(options)]
        outs = [out]
        for op in options:
            if float(op) == int(op):
                op = int(op)
            else :
                op = round(op,1)
            if op != out :
                outs += [op]
        for op in outs:
            if float(op) == int(op): 
                print(pytex(str(op)+ r' \ mathrm{' + unit + '}') + '..')
            else :
                print(pytex(str(round(op,1))+ r' \ mathrm{' + unit + '}') + '..')
    print(formula)
          

solve(given, formula)
    
    
    
'''
sf = open('question.txt', 'r')
question = sf.readline()
variables = sf.readline().split(',')
variables = [v.strip() for v in variables]
print(variables)
for var in variables:
    [v, q] = var.split('=')
    q = qunit(q)
    print(v, q)
    print(question)
    if v in question:
        print(v, '----------------')
    question = question.replace(v,q)
    print(question)
    print('__________________________________')
'''
    
    