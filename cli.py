import click
import sys
import traceback
import os
import opencc
import time

from lightnovel import LightNovel
from utils import echo
from provider import lk_new
from provider import wenku8
from provider import lk_mobile


echo.init_subroutine()


@click.group()
def cli():
	pass


@cli.command()
# general options
@click.option('--dump-path', type=click.Path(), default='./dump', 
	help='directory for dumping files and caches')
@click.option('--title', default=None, 
	help='title of light novel')
@click.option('--authors', default=None, 
	help='authors\' names, separated by comma (,)')
@click.option('--identifier', default=None, 
	help='identifier of light novel')
@click.option('--cover-link', default=None, 
	help='cover link of light novel. cover link can either be web link or file path. if it is not beginned with "http", it would be recognized as file path. if nothing was given, then it will use the first picture of webpage.')
@click.option('--cvt', default=None, 
	help='OpenCC conversion configuration, used to convert between different Chinese characters. you can choose the value from "s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t". if nothing is provided, no conversion would be performed. for more information, please visit: https://github.com/BYVoid/OpenCC')
@click.option('--path', type=click.Path(exists=True), default='./', 
	help='directory for saving the light novel')
# lightnovel.us
@click.option('--lk-html-dump', type=click.Path(exists=True), default=None, 
	help='(lightnovel.us) html content dump file path')
# wenku8.net
@click.option('--wenku8-volume', default=-1,
	help='(wenku8.net) identify the index of the volume to generate. -1 means every volume, which is also the default option. index starts from 1.')
# lk mobile
@click.option('--lk-mobile-top-area-height', default=325, 
	help='(lk mobile) the height of the top area')
@click.option('--lk-mobile-bottom-area-height', default=200, 
	help='(lk mobile) the height of the bottom area')
@click.option('--lk-mobile-image-equal-threshold', default=1, 
	help='(lk mobile) the threshold of judging whether two images are equal')
@click.option('--lk-mobile-safe-area-padding', default=20, 
	help='(lk mobile) the padding of the safe area')
@click.option('--lk-mobile-vert-dump', type=click.Path(exists=True), default=None, 
	help='(lk mobile) vertical content dump file path')
@click.option('--lk-mobile-horz-dump', type=click.Path(exists=True), default=None, 
	help='(lk mobile) horizontal content dump file path')
@click.option('--lk-mobile-html-dump', type=click.Path(exists=True), default=None, 
	help='(lk mobile) html content dump file path')
@click.option('--lk-mobile-conflict-mode', type=bool, default=False, 
	help='(lk mobile) whether to resolve conflict manually')
@click.option('--lk-mobile-ignore-newline', type=bool, default=True, 
	help='(lk mobile) whether to ignore newline')
# general arguments
@click.argument('url')
def download(
	dump_path, 
	title: str, 
	authors: str, 
	identifier: str, 
	cover_link: str, 
	cvt: str, 
	path: str, 
	lk_html_dump, 
	wenku8_volume: int, 
	lk_mobile_top_area_height: int, 
	lk_mobile_bottom_area_height: int, 
	lk_mobile_image_equal_threshold: int, 
	lk_mobile_safe_area_padding: int, 
	lk_mobile_vert_dump, 
	lk_mobile_horz_dump,
	lk_mobile_html_dump,
	lk_mobile_conflict_mode: bool,
	lk_mobile_ignore_newline: bool, 
	url: str):
	'''
	download the light novel

	ARGUMENTS:

	* URL: url of light novel to download
	'''
	def convert_str(content, cvt):
		# chinese conversion
		if cvt in ["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp", "tw2sp", "t2tw", "hk2t", "t2hk", "t2jp", "jp2t", "tw2t"]:
			converter = opencc.OpenCC(f'{cvt}.json')
			return converter.convert(content)
		return content

	echo.push_subroutine(sys._getframe().f_code.co_name)

	try:
		# init directory
		if not os.path.exists(dump_path):
			os.mkdir(dump_path)

		if cover_link is None:
			cover_link = input('(Optional) Input cover_link of light novel (see --help for further explanation): ')

		if url.startswith('https://www.lightnovel.us/'):
			contents = lk_new.get_contents(url, dump_path, lk_html_dump)
			cover_link = lk_new.get_cover(cover_link, dump_path) if cover_link.startswith('http') else cover_link
		elif url.startswith('https://www.wenku8.net/'):
			(source, authors, identifier, title, books, contents) = wenku8.get_contents(url, dump_path, wenku8_volume)
			cover_link = wenku8.get_cover(cover_link, dump_path) if cover_link.startswith('http') else cover_link
		elif url == 'lk-mobile':
			contents = lk_mobile.get_contents(lk_mobile_top_area_height, lk_mobile_bottom_area_height, lk_mobile_image_equal_threshold, lk_mobile_safe_area_padding, dump_path, lk_mobile_vert_dump, lk_mobile_horz_dump, lk_mobile_html_dump, lk_mobile_conflict_mode, lk_mobile_ignore_newline)
			cover_link = lk_mobile.get_cover(cover_link, dump_path) if cover_link.startswith('http') else cover_link
			url = '轻之国度 APP'
		else:
			echo.cexit('unsupported url')

		if type(contents) == str:
			contents = convert_str(contents, cvt)
		elif type(contents) == list:
			for content in contents:
				content['title'] = convert_str(content['title'], cvt)
				content['content'] = convert_str(content['content'], cvt)
		else:
			echo.cexit('CONTENTS MUST BE STRING OR LIST')


		TITLE_INPUT_HINT = 'Input title of light novel: '
		AUTHOR_INPUT_HINT = '(Optional) Input authors\' names, separated by comma (,): '
		IDENTIFIER_INPUT_HINT = '(Optional) Input identifier of light novel: '
		def isempty(instr) -> bool:
			if instr is None:
				return True
			if len(instr) == 0 or str.isspace(instr):
				return True
			return False
		if isempty(title):
			title = input(TITLE_INPUT_HINT)
		else:
			user_title = input(f'Current Title: {title}. (Optional) {TITLE_INPUT_HINT}')
			title = title if isempty(user_title) else user_title
		if isempty(authors):
			authors = input(AUTHOR_INPUT_HINT)
		else:
			user_authors = input(f'Current Authors: {authors}. {AUTHOR_INPUT_HINT}')
			authors = authors if isempty(user_authors) else user_authors
		if isempty(identifier):
			identifier = input(IDENTIFIER_INPUT_HINT)
		else:
			user_identifier = input(f'Current identifier: {identifier}. {IDENTIFIER_INPUT_HINT}')
			identifier = identifier if isempty(user_identifier) else user_identifier

		novel = LightNovel(source=url, authors=authors.split(','), identifier=identifier, title=title, cover_link=cover_link)
		novel.contents = contents
		novel.write_epub(path)
	except Exception as e:
		echo.cerr(f'Error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD LIGHTNOVEL FAILED')
	finally:
		echo.pop_subroutine()


if __name__ == '__main__':
	cli()
