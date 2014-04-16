import os
from ..sc2bank import (Section, Key, inspect_path, sign, sign_file, parse,
    parse_string, safe_list_get, PathInfo)
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from mock import patch
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.author_id = '1-S2-1-4337146'
        self.user_id = '1-S2-1-4253458'
        self.bank_name = 'llIlIIlIlIllIllI'
        self.bank = [
            Section('lllllIIlIllIIllI', [
                Key('lllllllIlIllIIII', 'int', '5')
            ]),
            Section('IIlIlIIlllIIII', [
                Key('IllIIIIIlIIIII', 'int', '780000')
            ])
        ]
        self.contents = """<?xml version="1.0" encoding="utf-8"?>
<Bank version="1">
    <Section name="lllllIIlIllIIllI">
        <Key name="lllllllIlIllIIII">
            <Value int="5"/>
        </Key>
    </Section>
    <Section name="IIlIlIIlllIIII">
        <Key name="IllIIIIIlIIIII">
            <Value int="780000"/>
        </Key>
    </Section>
    <Signature value="3ECC1CCD9762908DE09D322235D5ED4D13CD1C53"/>
</Bank>
"""
        self.signature = '3ECC1CCD9762908DE09D322235D5ED4D13CD1C53'

    def test_inspect_path(self):
        path = ('Blizzard', 'StarCraft II', 'Accounts', '12345678',
                '1-S2-1-9876543', 'Banks', '1-S2-1-123456',
                'mySc2bank.SC2Bank')
        minimal_path = path[4:]
        correct = ('1-S2-1-123456', '1-S2-1-9876543', 'mySc2bank')
        self.assertEquals(inspect_path(os.sep.join(path)), correct)
        self.assertEquals(inspect_path(os.sep.join(minimal_path)), correct)
        self.assertEquals(inspect_path(''), (None, None, None))

    def test_sign(self):
        self.assertEquals(sign(self.author_id, self.user_id, self.bank_name, self.bank), self.signature)

    def test_parse(self):
        mock_file = StringIO(self.contents)
        self.assertEquals(parse(mock_file), (self.bank, self.signature))
        self.assertRaises(RuntimeError, parse, StringIO('<someelement/>'))
        self.assertRaises(RuntimeError, parse,
            StringIO("""<Bank>
                            <Section name="bogus">
                                <Key name="TestKey">
                                    <Value int="5" string="hello"/>
                                </Key>
                            </Section>
                        </Bank>"""))
        self.assertEquals(parse(StringIO("""<Bank>
                                                <Section name="bogus">
                                                    <Key name="TestKey">
                                                        <Value int="5"/>
                                                    </Key>
                                                </Section>
                                            </Bank>""")), ([Section('bogus', [Key('TestKey', 'int', '5')])], None))

    def test_parse_string(self):
        self.assertEquals(parse_string(self.contents), (self.bank, self.signature))

    def test_Section(self):
        s1, s2 = self.bank[0], self.bank[1]
        self.assertEquals(s1, s1)
        self.assertNotEqual(s1, s2)
        self.assertLess(s2, s1)

    def test_Key(self):
        k1, k2 = self.bank[0].keys[0], self.bank[1].keys[0]
        self.assertEquals(k1, k1)
        self.assertNotEqual(k1, k2)
        self.assertLess(k2, k1)

    def test_safe_list_get(self):
        self.assertEquals(safe_list_get([], 1), None)
        self.assertEquals(safe_list_get([], 1, 'nadda'), 'nadda')

    def test_sign_file(self):
        mock_file = StringIO(self.contents)
        self.assertEquals(sign_file(mock_file, self.author_id, self.user_id, self.bank_name), (self.signature, self.signature))
        with patch('sc2bank.sc2bank.inspect_path') as mock_inspect_path:
            mock_file.seek(0)
            mock_inspect_path.return_value = PathInfo(self.author_id, self.user_id, self.bank_name)
            self.assertEquals(sign_file(mock_file), (self.signature, self.signature))



if __name__ == '__main__':
    unittest.main()