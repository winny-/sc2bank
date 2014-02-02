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

"""Validate SC2Bank XML document signatures.

This module parses and validates SC2Bank files used to store player
data associated with a StarCraft II map. SC2Bank files are utilized
to track player unlocks in the Arcade. Armed with a text editor, one
may artificially achieve player unlocks. This module can be either
used as a program or to build other programs. Example usage:

$ python sc2bank.py "$HOME/Library/Application Support/Blizzard/StarCraft II/Accounts/12345678/1-S2-1-1234567/Banks/1-S2-1-4337146/llIlIIlIlIllIllI.SC2Bank"
"""

from __future__ import print_function
from collections import namedtuple
import hashlib
import os
import re
import xml.etree.ElementTree as ET


class Section(object):
    """Section XML tag container for descendent Key tags."""

    def __init__(self, name, keys):
        """
        name -- Section tag's name attribute
        keys -- list of Key tags within this Section
        """
        self.name = name
        self.keys = keys

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Key(object):
    """Key XML tag container for a single descendent Value tag."""

    def __init__(self, name, value_type, value):
        """
        name       -- Key tag's name attribute
        value_type -- name of the Value tag's attribute with data. Should
                      be 'int', 'string', or 'fixed'.
        value      -- the value of the Value tag's value_type attribute
        """
        self.name = name
        self.type = value_type
        self.value = value

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


PathInfo = namedtuple('PathInfo', ['author_id', 'user_id', 'name'])


def inspect_file_path(path):
    """Inspect a SC2Bank file's path for metadata necessary to generate a signature.

    path -- Path to the SC2Bank file

    Returns:
    Tuple of the Author ID, User ID, and Bank name. Each element may be None if
    the information could not be deduced.
    """
    elements = os.path.dirname(path).split(os.sep)
    id_ = re.compile('^[0-9]-S2-[0-9]-[0-9]{6,7}$')
    author_id, user_id = map(lambda e: e if re.match(id_, e) else None,
                             [elements[-1], elements[-3]])
    found = re.match('^(.+)(\.SC2Bank)$', os.path.basename(path))
    if found:
        bank_name = found.group(1)
    else:
        bank_name = None
    return PathInfo(author_id, user_id, bank_name)


def sign_file(fname, author_id=None, user_id=None, bank_name=None):
    """Sign a SC2Bank file.

    fname     -- Path to the SC2Bank file
    author_id -- Author ID, e.g. "1-S2-1-1234567"
                 (default None, derived from last directory element)
    user_id   -- User ID, e.g. "1-S2-1-1234567" (default None,
                 derived from third to last directory element)
    bank_name -- SC2Bank filename without .SC2Bank or the file's path
                 (default None)

    Returns:
    Tuple of the calculated signature and the signature recorded in
    the XML document.
    """
    inspected_author_id, inspected_user_id, inspected_bank_name = inspect_file_path(fname)
    if not author_id:
        author_id = inspected_author_id
    if not user_id:
        user_id = inspected_user_id
    if not bank_name:
        bank_name = inspected_bank_name

    bank, signature = parse(fname)

    return sign(author_id, user_id, bank_name, bank), signature


def parse(fname, from_string=False):
    """Parse a SC2Bank file.

    fname       -- Path to the SC2Bank file
    from_string -- Whether to parse from a string instead of a file.

    Returns:
    Tuple of the parsed Bank element and the signature recorded in
    the XML document.
    """
    if from_string:
        root = ET.fromstring(fname)
    else:
        root = ET.parse(fname).getroot()
    if root.tag != 'Bank':
        raise RuntimeError('Invalid root tag: '+root.tag)
    bank = []
    for section in root.findall('./Section'):
        keys = []
        for key in section.findall('./Key'):
            value = key.find('./Value')
            # Do not look for "int" or "string" attributes. Instead get the only
            # attribute's name or raise an exception. This future-proofs for unknown
            # value types.
            if len(value.attrib) == 1:
                value_type = list(value.attrib.keys())[0]
            else:
                raise RuntimeError('Unknown value type in {}'
                                   .format(ET.tostring(value).rstrip().decode('UTF-8')))
            keys.append(Key(key.attrib['name'], value_type, value.attrib[value_type]))
        bank.append(Section(section.attrib['name'], keys))
    signature_element = root.find('./Signature')
    if signature_element is not None:
        signature = signature_element.get('value')
    else:
        signature = None
    return bank, signature

def sign(author_id, user_id, bank_name, bank):
    """Sign a SC2Bank file representation.

    author_id -- Author ID, e.g. "1-S2-1-1234567"
    user_id   -- User ID, e.g. "1-S2-1-1234567"
    bank_name -- SC2Bank filename without .SC2Bank and file's path
    bank      -- List of Section class instances

    Returns:
    String that should be the Signature tag's "value" attribute's value.
    """
    h = hashlib.sha1()
    h.update(''.join([author_id, user_id, bank_name]))
    for section in sorted(bank):
        h.update(section.name)
        for key in sorted(section.keys):
            h.update(''.join([key.name, 'Value', key.type, key.value]))
    return h.hexdigest().upper()


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
