"""
Validate SC2Bank XML document signatures.

This module parses and validates SC2Bank files used to store player
data associated with a StarCraft II map. SC2Bank files are utilized
to track player unlocks in the Arcade. Armed with a text editor, one
may artificially achieve player unlocks. This module can be either
used as a program or to build other programs. Example usage:

$ python sc2bank.py "$HOME/Library/Application Support/Blizzard/StarCraft II\
/Accounts/12345678/1-S2-1-1234567/Banks/1-S2-1-4337146/\
llIlIIlIlIllIllI.SC2Bank"
"""

from collections import namedtuple
import hashlib
import os
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO  # Python 3.x
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


def safe_list_get(l, index, default=None):
    """
    Get value for index in l. If index is out of range, return default
    instead.
    """
    try:
        return l[index]
    except IndexError:
        return default


def inspect_path(path):
    """
    Inspect a SC2Bank file's path for metadata necessary to generate a
    signature.

    path -- Path to the SC2Bank file

    Returns:
    Tuple of the Author ID, User ID, and Bank name. Each element may be None
    if the information could not be deduced.
    """
    elements = os.path.dirname(path).split(os.sep)
    id_ = re.compile('^[0-9]-S2-[0-9]-[0-9]{6,7}$')
    # Author ID & User ID are no use if in lower case.
    author_element = safe_list_get(elements, -1, '').upper()
    user_element = safe_list_get(elements, -3, '').upper()
    author_id, user_id = [e if re.match(id_, e) else None
                          for e in (author_element, user_element)]
    found = re.match('^(.+)(\.SC2Bank)$', os.path.basename(path), re.I)
    if found:
        bank_name = found.group(1)
    else:
        bank_name = None
    return PathInfo(author_id, user_id, bank_name)


def parse(fname):
    """
    Parse a SC2Bank file.

    fname -- Path to the SC2Bank file

    Returns:
    Tuple of the parsed Bank element and the signature recorded in
    the XML document.
    """
    root = ET.parse(fname).getroot()
    if root.tag != 'Bank':
        raise RuntimeError('Invalid root tag: ' + root.tag)
    bank = []
    for section in root.findall('./Section'):
        keys = []
        for key in section.findall('./Key'):
            value = key.find('./Value')
            # Do not look for "int" or "string" attributes. Instead get only
            # the attribute's name or raise an exception. This future-proofs
            # for unknown value types.
            if len(value.attrib) == 1:
                value_type = list(value.attrib.keys())[0]
            else:
                element = ET.tostring(value).rstrip().decode('UTF-8')
                raise RuntimeError('Unknown value type in {}'.format(element))
            key = Key(key.attrib['name'], value_type, value.attrib[value_type])
            keys.append(key)
        bank.append(Section(section.attrib['name'], keys))
    signature_element = root.find('./Signature')
    if signature_element is not None:
        signature = signature_element.get('value')
    else:
        signature = None
    return bank, signature


def parse_string(xml_string):
    """Parse SC2Bank from a string."""
    buf = StringIO(xml_string)
    parsed_sc2bank = parse(buf)
    buf.close()
    return parsed_sc2bank


def sign(author_id, user_id, name, bank):
    """
    Sign a SC2Bank file representation.

    author_id -- Author ID, e.g. "1-S2-1-1234567"
    user_id   -- User ID, e.g. "1-S2-1-1234567"
    name      -- SC2Bank filename without .SC2Bank and file's path
    bank      -- List of Section class instances

    Returns:
    String that should be the Signature tag's "value" attribute's value.
    """
    h = hashlib.sha1()
    update = lambda s: h.update(''.join(s).encode('UTF-8'))
    update([author_id, user_id, name])
    for section in sorted(bank):
        update(section.name)
        for key in sorted(section.keys):
            update([key.name, 'Value', key.type, key.value])
    return h.hexdigest().upper()


def sign_file(fname, author_id=None, user_id=None, name=None):
    """
    Sign a SC2Bank file.

    fname     -- Path to the SC2Bank file
    author_id -- Author ID, e.g. "1-S2-1-1234567"
                 (default None, derived from last directory element)
    user_id   -- User ID, e.g. "1-S2-1-1234567" (default None,
                 derived from third to last directory element)
    name      -- SC2Bank filename without .SC2Bank or the file's path
                 (default None)

    Returns:
    Tuple of the calculated signature and the signature recorded in
    the XML document.
    """
    if None in (author_id, user_id, name):
        info = inspect_path(fname)
        if author_id is None:
            author_id = info.author_id
        if user_id is None:
            user_id = info.user_id
        if name is None:
            name = info.name

    bank, signature = parse(fname)

    return sign(author_id, user_id, name, bank), signature


def sign_string(xml_string, author_id, user_id, name):
    """
    Sign a SC2Bank from a string.

    xml_string -- SC2Bank string to sign
    author_id  -- Author ID, e.g. "1-S2-1-1234567"
    user_id    -- User ID, e.g. "1-S2-1-1234567"
    name       -- SC2Bank filename without .SC2Bank or the file's path

    Returns:
    Tuple of the calculated signature and the signature recorded in
    the XML document.
    """
    bank, signature = parse_string(xml_string)

    return sign(author_id, user_id, name, bank), signature
