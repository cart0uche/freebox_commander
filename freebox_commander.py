#!/usr/bin/env python
# -*- coding: utf-8 -*-
# freebox commander

import string
from cmd import Cmd
import sys
sys.path.append('..')
from pyfree import Freebox

BYTE_PER_MO = 1048576


class FreeboxCommander(Cmd):

	def __init__(self):
		self._remote_path = ["Disque dur"]
		self._current_file_list = []
		self._current_directories = []
		Cmd.__init__(self)


	def do_connect(self, args):
		""" Connect to a freebox. Syntax : ip:port"""
		# Connection
		if len(args) == 0:
			self._fb = Freebox(debug=False)
		else:
			url = string.split(args, ':')
			if len(url) != 2:
				print "Syntax : connect [ip:port]"
				return
			else:
				self._fb = Freebox(freebox_ip=url[0], freebox_port=url[1])

		# Authorization
		if self._fb.is_authorization_granted():
			print 'Authorization already granted.'
		else:
			print 'Asking authorisation ...'
			if self._fb.ask_authorization('1', 'Freebox Command Line', '0.1', 'theBeast') is not None:
				print 'Authorization granted.'
			else:
				print 'Authorization failed.'
				return

		# Login
		if self._fb.login("1") is not None:
			print 'Login successful.'
			self._connected = True
		else:
			print 'Login failed'
			return

		self.build_current_directories()
		self.update_prompt()


	def do_ls(self, args):
		"""List files on the freebox."""
		if self.is_connected() is False:
			return

		for file in  self._fb.get_file_list(self.current_path_name)['result']:
			if file["name"] not in [".", ".."]:
				if args == "-l":
					print "%s  %5dMo %s"  %  ("d" if file["type"]=="dir" else "-", file["size"]/BYTE_PER_MO, file["name"])
				else:
					print file['name']
				self._current_file_list.append(file['name'])


	def do_cd(self, args):
		""" Change remote directory. """
		if self.is_connected() is False:
			return

		if len(args) == 0:
			self._remote_path = ["Disque dur"]
		elif args == ".":
			return
		elif args == "..":
			if len(self._remote_path) != 0:
				self._remote_path.pop()
				self.build_current_directories()
				self.update_prompt()
		else:
			self._remote_path.append(args)
			if self._fb.get_file_list(self.current_path_name)['success'] is True:
				self.build_current_directories()
				self.update_prompt()
			else:
				self._remote_path.pop()
				print args + " does not exist."


	def complete_cd(self, text, line, begidx, endidx):
		return  [i for i in self._current_directories if i.lower().startswith(text.lower())]


	def do_get(self, args):
		"""Download file from freebox."""
		if self.is_connected() is False:
			return

		for file in self._current_file_list['result']:
			if file['name'] == args:
				self._fb.download_file(file['path'], file['name'])


	def complete_get(self, text, line, begidx, endidx):
		return  [i for i in self._current_file_list if i.lower().startswith(text.lower())]


	def do_quit(self, args):
		"""Quits the program."""
		print "Quitting."
		raise SystemExit


	def is_connected(self):
		if hasattr(self, "_connected") and self._connected is True:
			return True
		else:
			print "You must to connect to a freebox before all operation, with command connect."
			return False


	def build_current_directories(self):
		del self._current_directories[:]
		for file in  self._fb.get_file_list(self.current_path_name)['result']:
			if file["type"] == "dir" and file["name"] not in [".", ".."]:
				self._current_directories.append(file['name'])


	def update_prompt(self):
		fcl.prompt = 'freebox # ' + self.current_path_name + " ~ "


	@property
	def current_path_name(self):
		path = ""
		for repo in self._remote_path:
			path = path + "/" + repo
		return path


if __name__ == '__main__':
	fcl = FreeboxCommander()
	fcl.prompt = 'freebox # '
	fcl.cmdloop('Starting prompt...')
