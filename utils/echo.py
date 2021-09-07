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


def clog(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(f" {message}")


def cerr(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'bright_red'))


def csuccess(message: str):
	click.echo(click.style(f"[{get_subroutine()}]", bg='magenta', fg='white'), nl=False)
	click.echo(click.style(f" {message}", fg = 'green'))


def cexit(message: str):
	cerr(f'{message}, exiting program.')
	sys.exit(1)
