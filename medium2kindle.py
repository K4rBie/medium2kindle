#!/usr/bin/python3
# author: Karol Bieńkowski
# license: GPL v3


import sys, subprocess, os, io, requests
from bs4 import BeautifulSoup
from PIL import Image

hotmail_pass = 'password'
hotmail_adress = 'example@hotmail.com' # script assumes it is your login, too
kindle_adress = 'example@kindle.com'

def convert ( file_name, author ):
	print('\nFile conversion started...')
	
	# ebook-convert file_name+'.html' file_name+'.mobi' --output-profile kindle --mobi-file-type=both --enable-heuristics --authors authors
	subprocess.run(['ebook-convert', file_name+'.html', file_name+'.mobi', '--no-inline-toc', '--pretty-print', '--output-profile', 'kindle', '--mobi-file-type=both', '--authors', author], stdout=subprocess.DEVNULL)

	print('Conversion successful.')


def send (file_name):
	print('\nSending file to Kindle device...')
	# you can add --fork but then photos will do weird shit. do sth to fix that.
	calibre_smtp = ' --relay smtp.live.com --port 587 --username ' + hotmail_adress + ' --password ' + hotmail_pass + ' --encryption-method TLS ' + hotmail_adress + ' ' + kindle_adress + ' ""'
	subprocess.call(['calibre-smtp', '-a', file_name+'.mobi'] + calibre_smtp.split(), stdout=subprocess.DEVNULL)
	
	print('File sent.')


def clean (file_name, n):	
	try:
		for ext in ['.html','.mobi']:	#'.html',
			os.remove(file_name+ext)
	except:
		pass
	
	if n == 0:
		return
	
	# you can simplify if you change the way you count imgs
	for i in range(1 , n+1):
		try:
			os.remove('img'+str(i))
		except:
			pass


def draw_line ():
	print('\n' + '_' * 40 + '\n')


def find_author (page):
	try:
		return page.find('meta', {'name': 'author'})['content']
	except:
		print('Som Ding Wong. Could not find author name in requested article page.')
		return 'unknown'


def find_title (page):
	# It just looks for multiple sources for title in site
	try:
		return page.find('meta', {'property': 'og:title'})['content']
	except:
		try:
			return page.find('meta', {'property': 'twitter:title'})['content']		
		except:
			try:
				return page.find('meta', {'name': 'title'})['content'].split('|')[0]
			except:
				try:
					return page.head.title.get_text().split('|')[0]
				except:
					print('Som Ding Wong. Could not find any title in requested article page.')
					return 'unknown'
				

def sanitize_images (section, n):
	for image in section.select('img[src]'):
		if image['src'].split('?')[-1] == 'q=20' or int(image['width']) <= 100:
			image.decompose()
			continue
		
		n += 1
		#resource = urlopen(Request(image['src'], None, header), timeout=10)
		resource = requests.get(image['src'], headers=header).content
		
		img = Image.open(io.BytesIO(resource))
		width, height = img.size
		
		if width >= 1600 or height >= 1600:
			if width >= height:
				divider = int(width/800)
			else:
				divider = int(height/800)
				
			img = img.resize((int(width/divider), int(height/divider)))
		
		img.save('img'+str(n), 'PNG')
		image['src'] = 'img'+str(n)
			
	return [section, n]


##################################################################

article_links = sys.argv

for article in range(1,len(article_links)):
	url = article_links[article]
	header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}	
	html = requests.get(url, headers=header).text
	page = BeautifulSoup(html, 'lxml')
	
	draw_line()
	
	author = find_author(page)
	title = find_title (page)
	file_name = title
	print('title: ', file_name, '\nauthor: ', author)
	
	sections = page.body.div.div.article
	
	for svg in sections.find_all("svg"):
		svg.decompose()
	
	for h1 in sections.find_all("h1"):
		h1.decompose()
	'''
	orig_file = open(file_name+'_orig.html', 'w')
	orig_file.write(page.prettify(formatter='html'))
	orig_file.close()
	'''
	#print('number of sections: ', len(sections))

	g = open(file_name+'.html', 'w')
	g.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN"><html lang="en"><head><title>' + title + '</title><meta http-equiv="content-type" content="text/html; charset=utf-8"/></head><body><div>\n')
	
	n = 0
	article_len = 0
	for section in sections:
		[section, n] = sanitize_images(section, n)
		article_len += len(section.get_text())
		g.write(section.prettify(formatter="html"))
		
		for image in section.select('img[src]'):
			image.wrap(page.new_tag("div"))
			
		for figure in section.select('figure'):
			figure.replace_with(page.new_tag("div"))

	g.write('</div></body></html>')
	g.close()
	
	if article_len < 1050:
		print("Article is too short, probably partial, not sending.")
		clean (file_name, n)
	else:
		convert ( file_name, author )
		send (file_name)
		clean (file_name, n)
