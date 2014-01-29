#!/usr/bin/env python
#
# Copyright (c) 2014, SystemW
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice and this permission notice appear
# in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

from hashlib import sha1
import os
import os.path
import xml.etree.ElementTree as ET

class Section(object):
	"""Section XML tag container for descendent Key tags."""

	def __init__(self, name, keys):
		"""
		Keyword arguments:
		name -- Section tag's name attribute
		keys -- list of Key tags within this Section
		"""
		self.name = name
		self.keys = keys

	def __lt__(self, other):
		return self.name < other.name

class Key(object):
	"""Key XML tag container for a single descendent Value tag."""

	def __init__(self, name, value_type, value):
		"""
		Keyword arguments:
		name       -- Key tag's name attribute
		value_type -- name of the Value tag's attribute with data
		value      -- the value of the Value tag's value_type attribute
		"""
		self.name = name
		self.type = value_type
		self.value = value

	def __lt__(self, other):
		return self.name < other.name

def sign_file(fname, author_id=None, user_id=None, bank_name=None):
	"""Sign a SC2Bank file.

	Keyword arguments:
	fname     -- Path to the SC2Bank file
	author_id -- Author ID (default None)
	user_id   -- User ID (default None)
	bank_name -- SC2Bank filename without .SC2Bank and file's path
	             (default None)

	Returns:
	Tuple of the calculated signature and the signature recorded in
	the XML document.
	"""
	directory = os.path.dirname(fname).split(os.sep)
	if not author_id:
		author_id = directory[-1]
	if not user_id:
		user_id = directory[-3]
	if not bank_name:
		bank_name = os.path.basename(fname).rstrip('.SC2Bank')

	bank, signature = parse_sc2bank(fname)

	return sign(author_id, user_id, bank_name, bank), signature


def parse_sc2bank(fname):
	"""Parse a SC2Bank file.

	Keyword arguments:
	fname -- Path to teh SC2Bank file

	Returns:
	Tuple of the parsed Bank element and the signature recorded in
	the XML document.
	"""
	root = ET.parse(fname).getroot()
	if root.tag != 'Bank':
		raise RuntimeError('Invalid root tag: '+root.tag)
	bank = []
	for section in [x for x in root if x.tag == 'Section']:
		keys = []
		for key in [x for x in section if x.tag == 'Key']:
			value = key[0]
			if 'int' in value.attrib:
				value_type = 'int'
			elif 'string' in value.attrib:
				value_type = 'string'
			else:
				raise RuntimeError('Unknown value type.')
			keys.append(Key(key.attrib['name'], value_type, value.attrib[value_type]))
		bank.append(Section(section.attrib['name'], keys))
	signature_element = root.find('Signature')
	if signature_element is not None:
		signature = signature_element.get('value')
	else:
		signature = None
	return bank, signature

def sign(author_id, user_id, bank_name, bank):
	"""Sign a SC2Bank file representation.

	Keyword arguments:
	author_id -- Author ID
	user_id   -- User ID
	bank_name -- SC2Bank filename without .SC2Bank and file's path
	bank -- List of Section class instances

	Returns:
	String that should be the Signature tag's "value" attribute's value.
	"""
	s = author_id + user_id + bank_name
	for section in sorted(bank):
		s += section.name
		for key in sorted(section.keys):
			s += key.name + 'Value' + key.type + key.value
	return sha1(s.encode('UTF-8')).hexdigest().upper()


def test():
	"""Quick and dirty assert-based test suite for this module."""
	author_id = '1-S2-1-4337146'
	user_id = '1-S2-1-4253458'
	bank_name = 'llIlIIlIlIllIllI'
	bank = [
		Section('lllllIIlIllIIllI', [
			Key('lllllllIlIllIIII', 'int', '3')
		]),
		Section('IIlIlIIlllIIII', [
			Key('IllIIIIIlIIIII', 'int', '33619')
		])
	]
	assert sign(author_id, user_id, bank_name, bank) \
		== '267B50FB94512FD93A28345D93A519639F4F3F0D'
	print('All tests succeeded.')


if __name__ == '__main__':
	import sys
	def usage(v):
		print('Usage: {0} path/to/Starcraft/BankFile.SC2Bank'.format(sys.argv[0]))
		sys.exit(v)

	if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
		usage(0)

	fname = sys.argv[1]
	if not os.path.isfile(fname):
		print('"{0}" is not a file.'.format(fname))
		usage(1)

	signature, recorded_signature = sign_file(fname)
	print('Calculated signature: {0}'.format(signature))
	if recorded_signature is None:
		recorded_signature = '(No signature in XML document.)'
	print('Recorded signature:   {0}'.format(recorded_signature))
	if signature != recorded_signature:
		print('Signatures are NOT equal!')
		sys.exit(1)
