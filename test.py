from sc2bank import *
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

    def test_inspect_file_path(self):
        path = ('Blizzard', 'StarCraft II', 'Accounts', '12345678', '1-S2-1-9876543', 'Banks', '1-S2-1-123456', 'mySc2bank.SC2Bank')
        orig_sep = os.sep
        for sep in ('\\', '/'):
            os.sep = sep
            self.assertEquals(inspect_file_path(sep.join(path)), ('1-S2-1-123456', '1-S2-1-9876543', 'mySc2bank'))
        os.sep = orig_sep

    def test_sign(self):
        self.assertEquals(sign(self.author_id, self.user_id, self.bank_name, self.bank), self.signature)

    def test_parse(self):
        self.assertEquals(parse(self.contents, from_string=True), (self.bank, self.signature))


if __name__ == '__main__':
    unittest.main()