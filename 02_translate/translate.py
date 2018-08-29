# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json


def tran(sentence):
	url='http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc'
	head={}
	head['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'

	data = {}
	data['action'] = 'FY_BY_REALTIME'
	data['client'] = 'fanyideskweb'
	data['doctype'] = 'json'
	data['from'] = 'AUTO'
	data['i'] = sentence
	data['keyfrom'] = 'fanyiweb'
	data['salt'] = '1521946585047'
	data['sign'] = '8bb00619ab82714eccd2d7bbcc0fce15'
	data['smartresult'] = 'dict'
	data['to'] = 'AUTO'
	data['typoResult']= 'false'
	data['version']= '2.1'

	data = urllib.parse.urlencode(data).encode('utf-8')
	response = urllib.request.urlopen(url,data)
	html= response.read().decode('utf-8')
	target = json.loads(html)
	type(target)
	print('翻译结果：%s' % (target['translateResult'][0][0]['tgt']))

quit = False

while quit == False:
	sentence = input("请输入要翻译的句子： ")
	if sentence != 'q':
		tran(sentence)
	else:
		quit = True


