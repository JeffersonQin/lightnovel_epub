import click
import sys


def init_subroutine():
	global subroutine_stack
	subroutine_stack = []


def push_subroutine(cmd_name: str):
	global subroutine_stack
	subroutine_stack.append(cmd_name)


def pop_subroutine():
	global subroutine_stack
	last = subroutine_stack[-1]
	subroutine_stack = subroutine_stack[:-1]
	return last


def get_subroutine():
	return subroutine_stack[-1]


def _clog(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(message)


def clog(*messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_clog(val)


def _cerr(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'bright_red'))


def cerr(*messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_cerr(val)


def _csuccess(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'green'))


def csuccess(*messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_csuccess(val)


def _cexit(message: str):
	cerr(f'{message}, exiting program.')
	sys.exit(1)


def cexit(*messages):
	val = ''
	for message in messages:
		val = val + ' ' + str(message)
	_cexit(val)
