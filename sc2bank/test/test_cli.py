from ..cli import main, parse_args
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.valid_userid = '1-S2-1-4253458'
        self.valid_authorid = '1-S2-1-4337146'
        self.valid_bankname = 'somefile'
        self.valid_file = 'somefile.SC2Bank'
        self.valid_userid_flags = ['--userid', '-u']
        self.valid_authorid_flags = ['--authorid', '-a']
        self.valid_bankname_flags = ['--bankname', '-b']

    def test_parse_args(self):
        valid_flags = zip(self.valid_userid_flags,
                          self.valid_authorid_flags,
                          self.valid_bankname_flags)
        for userid_flag, authorid_flag, bankname_flag in valid_flags:
            test_args = [userid_flag, self.valid_userid,
                    authorid_flag, self.valid_authorid,
                    bankname_flag, self.valid_bankname,
                    self.valid_file]
            args, _ = parse_args(test_args)
            self.assertEquals(args.sc2bank, self.valid_file)
            self.assertEquals(args.userid, self.valid_userid)
            self.assertEquals(args.authorid, self.valid_authorid)
            self.assertEquals(args.bankname, self.valid_bankname)


if __name__ == '__main__':
    unittest.main()