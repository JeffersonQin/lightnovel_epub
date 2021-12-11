import os
import sys
import requests
import traceback
import tempfile
from bs4 import BeautifulSoup
from ebooklib import epub

from utils import echo
from utils import download
from utils.checker import is_not_null, is_null

class LightNovel():
	'''
	object of light novel
	'''
	
	url = ''
	'''
	url of web page
	'''

	authors = []
	'''
	author (Optional)
	'''
	
	identifier = None
	'''
	identifier (Optional)
	'''

	title = ''
	'''
	title of the book
	'''

	content = ''
	'''
	HTML content
	'''

	cover_link = None
	'''
	link of cover. if `None`, then use the first picture of webpage.\n
	cover_link can either be web link or file path.\n
	if it is not beginned with `http`, it would be recognized as file path.
	'''

	def __init__(self, url: str, authors=None, identifier=None, title=None, cover_link=None):
		'''
		initialize light novel object
		'''
		self.url = url
		if authors is not None: self.authors = authors
		if identifier is not None: self.identifier = identifier
		if title is not None: self.title = title
		if cover_link is not None: self.cover_link = cover_link


	def download_content(self):
		'''
		download web content
		'''
		echo.push_subroutine(sys._getframe().f_code.co_name)

		echo.clog(f'start downloading: {self.url} => memory')
		# download
		try:
			res = requests.get(url=self.url, headers={
				'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
				'accept-encoding': 'gzip, deflate, br',
				'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
				'cache-control': 'no-cache',
				'pragma': 'no-cache',
				'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
				'sec-ch-ua-mobile': '?0',
				'sec-fetch-dest': 'document',
				'sec-fetch-mode': 'navigate',
				'sec-fetch-site': 'same-origin',
				'sec-fetch-user': '?1',
				'upgrade-insecure-requests': '1',
				'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
			}).text
		except Exception as e:
			echo.cerr(f'error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('DOWNLOAD FAILED')
		# parse
		try:
			soup = BeautifulSoup(res, 'lxml')
			article = soup.find('article', id='article-main-contents')
			self.content = str(article)
		except Exception as e:
			echo.cerr(f'error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('PARSING FAILED')

		echo.pop_subroutine()


	def write_epub(self, path: str):
		'''
		generate the ebook to `path`
		'''
		echo.push_subroutine(sys._getframe().f_code.co_name)

		echo.clog(f'start generating...')

		try:
			# create epub book
			book = epub.EpubBook()
			
			# set metadata
			if is_not_null(self.authors):
				for author in self.authors:
					book.add_author(author=author)
			
			if is_not_null(self.identifier):
				book.set_identifier(self.identifier)

			book.set_title(self.title)
			book.set_language('zh-CN')
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('CREATING EPUB BOOK FAILED')
		
		# parse images
		try:
			soup = BeautifulSoup(self.content, 'lxml')
			image_tags = soup.find_all('img')
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('PARSING HTML FAILED')

		# store images
		first_flag = True # flag for storing first image
		first_name = None # name of first downloaded image
		first_dir = None # dir of first downloaded image

		try:
			i = 0
			for tag in image_tags:
				i = i + 1
				echo.clog(f'Processing images: ({i} / {len(image_tags)})')
				# parse
				link = str(tag.attrs['src'])

				if link.startswith('http') or link.startswith('//'):
					file_name = link.split('?')[0].split('/')[-1]
					file_dir = os.path.join(tempfile.gettempdir(), file_name)
					# download
					res = download.download_file(link, file_dir)
				else:
					file_name = os.path.basename(link)
					file_dir = link
				if first_flag:
					first_name = file_name
					first_dir = file_dir
					first_flag = False
				# convert href
				tag.attrs['src'] = f'../Images/{file_name}'
				image = epub.EpubImage()
				image.file_name = f'Images/{file_name}'
				image.content = open(file_dir, 'rb').read()
				book.add_item(image)
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('PROCESSING IMAGES FAILED')

		# set cover
		try:
			if is_not_null(self.cover_link):
				if str(self.cover_link).startswith('http'):
					cover_name = self.cover_link.split('?')[0].split('/')[-1]
					cover_dir = os.path.join(tempfile.gettempdir(), cover_name)
					res = download.download_file(self.cover_link, cover_dir)
					if (res == 0):
						echo.cerr(f'download cover failed: {link}')
					else:
						book.set_cover(cover_name, open(cover_dir, 'rb').read())
				elif os.path.exists(self.cover_link):
					book.set_cover(os.path.basename(self.cover_link), open(self.cover_link, 'rb').read())
			elif first_dir is not None:
				book.set_cover(first_name, open(first_dir, 'rb').read())
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('SETTING COVER IMAGE FAILED')
		
		try:
			# set content
			if is_not_null(self.url):
				about_text = f'<p>本书由<a href="https://github.com/JeffersonQin/lightnovel_epub">JeffersonQin/lightnovel_epub</a>工具自动生成。<br>仅供学习交流使用，禁作商业用途。</p><br><p>本书根据<a href="{self.url}">{self.url}</a>生成</p>'
			else:
				about_text = f'<p>本书由<a href="https://github.com/JeffersonQin/lightnovel_epub">JeffersonQin/lightnovel_epub</a>工具自动生成。<br>仅供学习交流使用，禁作商业用途。</p><br><p>本书根据LK客户端内容生成</p>'
			about_content = epub.EpubHtml(title='关于本电子书', file_name='Text/about.xhtml', lang='zh-CN', content=about_text)
			main_content = epub.EpubHtml(title=self.title, file_name='Text/lightnovel.xhtml', lang='zh-CN', content=str(soup))

			book.add_item(about_content)
			book.add_item(main_content)

			# configure book
			book.toc = (about_content, main_content)
			book.spine = [about_content, main_content]

			# generate book
			epub.write_epub(os.path.join(path, f'{self.title}.epub'), book, {})
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('BOOK CONFIGURATION & GENERATION FAILED')
		
		echo.pop_subroutine()
