import click
import sys
import traceback
import os
import opencc

from lightnovel import LightNovel
from utils import downloader
from utils import echo
from provider import lk_new
from provider import wenku8


echo.init_subroutine()


@click.group()
def cli():
	pass


@cli.command()
@click.option('--dump-path', type=click.Path(exists=True), default='./dump', 
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
@click.option('--lk-html-dump', type=click.Path(exists=True), default=None, 
				help='(lightnovel.us) html content dump file path')
@click.option('--wenku8-volume', default=-1,
				help='(wenku8.net) identify the index of the volume to generate. -1 means every volume, which is also the default option. index starts from 1.')
@click.argument('url')
def download(dump_path, 
			title: str, 
			authors: str, 
			identifier: str, 
			cover_link: str, 
			cvt: str, 
			path: str, 
			lk_html_dump, 
			wenku8_volume: int, 
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
			cover_link = input('(optional) Input cover_link of light novel (see --help for further explanation): ')

		if url.startswith('https://www.lightnovel.us/'):
			contents = lk_new.get_contents(url, dump_path, lk_html_dump)
			cover_link = lk_new.get_cover(cover_link, dump_path) if cover_link.startswith('http') else cover_link
		elif url.startswith('https://www.wenku8.net/'):
			lightNovel = wenku8.get_contents(url, dump_path, wenku8_volume)
			contents, title, authors, identifier = lightNovel.contents, lightNovel.title, lightNovel.authors, lightNovel.identifier
			cover_link = wenku8.get_cover(cover_link, dump_path) if cover_link.startswith('http') else cover_link
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

		if title is None:
			title = input('Input title of light novel: ')
		if authors is None:
			authors = input('(optional) Input authors\' names, separated by comma (,): ')
		if identifier is None:
			identifier = input('(optional) Input identifier of light novel: ')

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
