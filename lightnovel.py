import os
import sys
import requests
import traceback
import tempfile
import base64
from bs4 import BeautifulSoup
from ebooklib import epub

from utils import echo
from utils import downloader
from utils.checker import is_not_null, is_null

class LightNovel():
	'''
	object of light novel
	'''
	
	source = ''
	'''
	source of light novel
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

	contents = ''
	'''
	HTML content
	'''

	cover_link = None
	'''
	link of cover. if `None`, then use the first picture of webpage.\n
	cover_link can either be web link or file path.\n
	if it is not beginned with `http`, it would be recognized as file path.
	'''

	def __init__(self, source: str, authors=None, identifier=None, title=None, cover_link=None):
		'''
		initialize light novel object
		'''
		self.source = source
		if authors is not None: self.authors = authors
		if identifier is not None: self.identifier = identifier
		if title is not None: self.title = title
		if cover_link is not None: self.cover_link = cover_link


	def process_image_content(self, content, book):
		'''
		process image content
		:param content: HTML content
		:return: content, first image bytes
		'''
		echo.push_subroutine(sys._getframe().f_code.co_name)

		# parse images
		try:
			soup = BeautifulSoup(content, 'lxml')
			image_tags = soup.find_all('img')
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('PARSING HTML FAILED')

		# store images
		first_flag = True # flag for storing first image
		first_image = None

		try:
			i = 0
			for tag in image_tags:
				i = i + 1
				echo.clog(f'Processing images: ({i} / {len(image_tags)})')
				# parse
				link = str(tag.attrs['src'])

				r_image = None

				if link.startswith('data:'):
					r_image = base64.decodebytes(link.split(';')[1].split(',')[1].encode('utf-8'))
				else:
					file_name = os.path.basename(link)
					file_dir = link
					
					# convert href
					tag.attrs['src'] = f'../Images/{file_name}'
					image = epub.EpubImage()
					image.file_name = f'Images/{file_name}'
					image.content = open(file_dir, 'rb').read()
					book.add_item(image)
					r_image = image.content
				
				if first_flag and r_image is not None:
					first_image = r_image
					first_flag = False
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('PROCESSING IMAGES FAILED')
		
		return soup, first_image


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
		
		if type(self.contents) == str:
			soup, first_image = self.process_image_content(self.contents, book)
		elif type(self.contents) == list:
			_contents = []
			first_image = None
			for content in self.contents:
				soup, _first_image = self.process_image_content(content['content'], book)
				if first_image is None:
					first_image = _first_image
				_contents.append({
					'content': str(soup),
					'title': content['title'],
				})
		else:
			echo.cexit('CONTENTS MUST BE STRING OR LIST')
		
		# set cover
		try:
			if is_not_null(self.cover_link):
				if str(self.cover_link).startswith('http'):
					cover_name = self.cover_link.split('?')[0].split('/')[-1]
					cover_dir = os.path.join(tempfile.gettempdir(), cover_name)
					downloader.download_file(self.cover_link, cover_dir)
					book.set_cover(cover_name, open(cover_dir, 'rb').read())
				elif os.path.exists(self.cover_link):
					book.set_cover(os.path.basename(self.cover_link), open(self.cover_link, 'rb').read())
			elif first_image is not None:
				book.set_cover('cover', first_image)
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('SETTING COVER IMAGE FAILED')
		
		try:
			# set content
			about_text = f'<p>本书由<a href="https://github.com/JeffersonQin/lightnovel_epub">JeffersonQin/lightnovel_epub</a>工具自动生成。<br>仅供学习交流使用，禁作商业用途。</p><br><p>本书根据 {self.source} 生成</p>'
			if type(self.contents) == str:
				about_content = epub.EpubHtml(title='关于本电子书', file_name='Text/about.xhtml', lang='zh-CN', content=about_text)
				main_content = epub.EpubHtml(title=self.title, file_name='Text/lightnovel.xhtml', lang='zh-CN', content=str(soup))

				book.add_item(about_content)
				book.add_item(main_content)

				# configure book
				book.toc = (about_content, main_content)
				# add default NCX and Nav file
				book.add_item(epub.EpubNcx())
				book.add_item(epub.EpubNav())
				book.spine = ['nav', about_content, main_content]
			elif type(self.contents) == list:
				about_content = epub.EpubHtml(title='关于本电子书', file_name='Text/about.xhtml', lang='zh-CN', content=about_text)
				i = 0
				epub_nav = ['nav', about_content]
				epub_toc = [about_content]
				epub_contents = [about_content]
				for content in _contents:
					i += 1
					item = (epub.EpubHtml(title=content['title'], file_name=f'Text/Section{i}.xhtml', lang='zh-CN', content=content['content']))
					epub_toc.append(item)
					epub_nav.append(item)
					epub_contents.append(item)
				
				book.add_item(about_content)
				for epub_content in epub_contents:
					book.add_item(epub_content)

				# configure book
				book.toc = tuple(epub_toc)
				
				# add default NCX and Nav file
				book.add_item(epub.EpubNcx())
				book.add_item(epub.EpubNav())
				
				book.spine = epub_nav

			# generate book
			epub.write_epub(os.path.join(path, f'{self.title}.epub'), book, {})
		except Exception as e:
			echo.cerr(f'Error: {repr(e)}')
			traceback.print_exc()
			echo.cexit('BOOK CONFIGURATION & GENERATION FAILED')
		
		echo.pop_subroutine()
