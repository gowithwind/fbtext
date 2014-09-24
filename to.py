import json
def hzpy():
	with open('hzpy.txt','r') as f:
		lines=f.read().split('\n')
	with open('py.js','w') as f:
		cidian={}
		for line in lines:
			cols=line.split('	')
			hanzi,pinyin=cols[0],cols[1]
			item=cidian.get(pinyin)
			if item:
				item.append(hanzi)
			else:
				cidian[pinyin]=[hanzi]
		#f.write(str(cidian))
		f.write('var cidian=')
		f.write(json.dumps(cidian).encode('utf-8'))

def save(f,name,obj):
	f.write('var %s='%name)
	f.write(json.dumps(obj, ensure_ascii=False))
	f.write('\n')

def add_index(index,name,i):
	item=index.get(name)
	if item:
		index[name].append(i)
	else:
		index[name]=[i]

def zidian():
	with open('zidian.txt','r') as f:
		lines=f.read().split('\n')
	index={}
	full_index={}
	words=[]
	weights=[]
	pinyins=[]
	with open('py2.js','w') as f:
		i=0
		for line in lines:
			cols=line.split(' ')
			hanzi=cols[0]
			pinyin=cols[3:]
			first=pinyin[0]

			length=len(pinyin)
			#for single hanzi
			if length==1:
				all=''
				for char in first:
					all+=char
					add_index(index,all,i)
			#for ciyu
			all_sheng=''
			for p in pinyin:
				all_sheng+=p[0]
				add_index(full_index,all_sheng,i)
			#print hanzi,pinyin
			words.append(hanzi)
			weights.append(float(cols[1]))
			pinyins.append(first)
			i+=1

		for i in index:
			list_i=index[i]
			index[i]=sorted(list_i,key=lambda x:weights[x],reverse=True)
			#if i=='e':print index[i]
		pinyins=list(set(pinyins))
		save(f,'pinyins',pinyins)
		save(f,'words',words)
		save(f,'weights',weights)
		save(f,'first_index',index)
		save(f,'full_index',full_index)

zidian()
