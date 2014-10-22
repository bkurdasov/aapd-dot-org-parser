import requests
from lxml.html import fromstring,tostring
import csv
from lxml import etree
import sys
import re
import time

countries=[]
countries_lower=[]
with open('countries-filtered.txt') as countries_file:
	for line in countries_file:
		line=line.strip()
		countries.append(line)
		countries_lower.append(line.lower())

#print countries
#print countries_lower
uri='http://www.aapd.org/finddentist/search/?pg=%s'
# get total number of pages
r=requests.get(uri%1,timeout=10)
doc=fromstring(r.text)
total_items=int(doc.xpath('//a[@class="all"]/text()')[0].split(' ')[-1][1:-1])
items_per_page=len(doc.xpath('//div[@class="oneDentist"]'))
last_page=total_items/items_per_page+1
print "There are %s items total, %s pages, %s items per page" % (total_items,last_page,items_per_page)

with open('result.csv','wb') as outfile:
	writer=csv.writer(outfile)
	writer.writerow(['Business name','Address','City','State','Zipcode','Country','Phone','Fax','Website'])
	for pagenum in xrange(1,last_page+1):
		print "Doing page %4s..." % pagenum,
		r=requests.get(uri%pagenum,timeout=10)
		doc=fromstring(r.text)
		for element in doc.xpath('//div[@class="oneDentist"]/div[@style="float:left"]'):
			name=element.xpath('strong/text()')[0]
			html=tostring(element)
			#print etree.tostring(element)
			#print html
			#print re.split('<br>',html)
			country_idx=0
			lines=html.split(r'<br>')[1:-1]
			for idx,line in  enumerate(lines):
				#print idx,line.strip()
				if line.strip().lower() in set(countries_lower):
					country_idx=idx
					break
					#print "Country at index ",idx
			city_state_zipcode=lines[country_idx-1].strip()
			address_lines=lines[:country_idx-1]
			country=lines[country_idx].strip()
			#print name
			#print address_lines
			if 'child' in address_lines[0].lower() or 'dentist' in address_lines[0].lower() or 'dental' in address_lines[0].lower() or 'pllc' in address_lines[0].lower():
				#name+=' '+address_lines[0]
				name='%s %s'%(name,address_lines[0].strip())
				address=' '.join(address_lines[1:])
			else:
				address=' '.join(address_lines)
			phone_num=''
			fax_num=''
			website=''
			for line in lines[country_idx+1:]:
				line=line.strip().lower()
				#print line.strip()
				if line.startswith('ph'):
					phone_num=line[3:]
				if line.startswith('fx'):
					fax_num=line[3:]
				if 'a href' in line:
					atag=fromstring(line)
					website=atag.text
			city=''
			state=''
			zipcode=''
			#print city_state_zipcode
			if ',' in city_state_zipcode:
				city=city_state_zipcode.split(',')[0]
				rest=city_state_zipcode.split(',')[1]
				zipmatch=re.search(r'[A-Z0-9]+[\s\-]?[A-Z0-9]+',rest)
				if zipmatch:
					zipcode=zipmatch.group()
				state=rest[:-len(zipcode)].strip()
			else:
				zipmatch=re.search(r'[A-Z0-9]+[\s\-]?[A-Z0-9]+',city_state_zipcode)
				if zipmatch:
					zipcode=zipmatch.group()
				city=city_state_zipcode.split(' ')[0]
				state=' '.join(city_state_zipcode.split(' ')[1:])	
			#print '%s,\t\t%s,\t\t%s,'%(city,state,zipcode)
			#print name,address,city,state,zipcode,country,phone_num,fax_num,website
			writer.writerow(map(lambda x:x.encode('utf-8'),[name,address,city,state,zipcode,country,phone_num,fax_num,website]))
		print "done."
		time.sleep(0.5)	
	print "Done."