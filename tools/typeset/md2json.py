import json,re,sys
L=open(sys.argv[1]).read().split('\n')
fm=L.index('---',1); meta={}
for l in L[1:fm]:
    k,v=l.split(':',1); meta[k]=v.strip().strip('"')
out=[{'t':'title','x':meta['title'],'sub':meta['subtitle']}]
i=fm+1; para=[]
def flush():
    global para
    if para: out.append({'t':'p','x':' '.join(para)}); para=[]
def q(s):  # smart quotes
    s=re.sub(r'(^|[\s(\[*—])"',r'\1“',s); s=s.replace('"','”')
    s=re.sub(r"(^|[\s(\[*—])'",r'\1‘',s); return s.replace("'",'’')
while i<len(L):
    l=L[i]
    if not l.strip(): flush(); i+=1; continue
    if l.startswith('### '): flush(); out.append({'t':'h2','x':q(l[4:])})
    elif l.startswith('## '): flush(); out.append({'t':'h1','x':q(l[3:])})
    elif l.startswith('> '): flush(); out.append({'t':'quote','x':q(l[2:])})
    elif l.startswith('|'):
        flush(); rows=[]
        while i<len(L) and L[i].startswith('|'):
            c=[x.strip() for x in L[i].strip('|').split('|')]
            if not set(''.join(c))<=set('-: '): rows.append([q(x) for x in c])
            i+=1
        out.append({'t':'table','rows':rows}); continue
    elif re.match(r'^(- |\d+\. )',l):
        flush(); kind='bullets' if l.startswith('- ') else 'numbers'; items=[]
        while i<len(L) and re.match(r'^(- |\d+\. )',L[i]):
            items.append(q(re.sub(r'^(- |\d+\. )','',L[i]))); i+=1
        out.append({'t':kind,'items':items}); continue
    else: para.append(q(l.strip()))
    i+=1
flush()
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,indent=1)
print(len(out))
