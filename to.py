import json
with open('hzpy.txt','r') as f:
	lines=f.read().split('\n');
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

