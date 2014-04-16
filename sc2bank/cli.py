from __future__ import print_function
import os
from . import sc2bank
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description='Verify a SC2Bank signature.')
    parser.add_argument('--userid',
                        '-u',
                        default=None,
                        help='User ID to verify the SC2Bank with')
    parser.add_argument('--authorid',
                        '-a',
                        default=None,
                        help='Author ID to verify the SC2Bank with')
    parser.add_argument('--bankname',
                        '-b',
                        default=None,
                        help='SC2Bank name to verify with (is usually the '
                             'filename without the extension)')
    parser.add_argument('sc2bank',
                        metavar='SC2BANK',
                        help='Path of the SC2Bank to verify')
    args = parser.parse_args()

    fname = args.sc2bank
    if not os.path.isfile(fname):
        sys.stderr.write('"{0}" is not a file.\n'.format(fname))
        parser.print_help()
        sys.exit(2)

    signature, recorded_signature = sc2bank.sign_file(fname,
                                                      author_id=args.authorid,
                                                      user_id=args.userid,
                                                      name=args.bankname)
    print('Calculated signature: {0}'.format(signature))
    if recorded_signature is None:
        recorded_signature = '(No signature in XML document.)'
    print('Recorded signature:   {0}'.format(recorded_signature))
    if signature != recorded_signature:
        print('Signatures are NOT equal!')
        sys.exit(1)


if __name__ == '__main__':
    main()
