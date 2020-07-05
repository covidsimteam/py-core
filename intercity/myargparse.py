# ensure that we load the standard argparse here
#import sys
#path = sys.path[:]
#print path
#for pwd in ('/user/jrichard/opt/share/python', ''):
#	for i in xrange(sys.path.count(pwd)):
#		sys.path.remove(pwd)
#sys.path.insert(0, '/usr/lib64/python2.6/site-packages')
#print sys.path
#import argparse
#help(argparse)
#sys.path = path
#print sys.path
#del i, pwd, path

from argparse import *
from textwrap import dedent

class RawDescriptionDefaultsHelpFormatter(RawDescriptionHelpFormatter, ArgumentDefaultsHelpFormatter):
	def _fill_text(self, text, width, indent):
		return ''.join([indent + line for line in dedent(text).splitlines(True)])

class RawTextDefaultsHelpFormatter(RawTextHelpFormatter, ArgumentDefaultsHelpFormatter):
	pass

class MyArgumentParser(ArgumentParser):
	def __init__(self, *args, **kwargs):
		if 'formatter_class' not in kwargs:
			kwargs['formatter_class'] = RawDescriptionDefaultsHelpFormatter
		ArgumentParser.__init__(self, *args, **kwargs)
	def convert_arg_line_to_args(self, arg_line):
		if arg_line.strip().startswith('#'):
			args = []
		else:
			args = arg_line.split()
		return args
