from __future__ import print_function
import os
from . import sc2bank
import sys
import argparse


def parse_args(args):
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
    return parser.parse_args(args), parser


def main(args):
    args, parser = parse_args(args)

    fname = args.sc2bank
    author_id, user_id, bank_name = args.authorid, args.userid, args.bankname

    if fname == '-':
        if None in (author_id, user_id, bank_name):
            sys.stderr.write('Error: Must specify --userid, --authorid, and '
                             '--bankname to sign SC2Bank from stdin.\n\n')
            parser.print_help()
            sys.exit(2)
        signature, recorded_signature = sc2bank.sign_string(
            sys.stdin.read(),
            author_id=args.authorid,
            user_id=args.userid,
            name=args.bankname
        )
    elif os.path.isfile(fname):
        signature, recorded_signature = sc2bank.sign_file(
            fname,
            author_id=args.authorid,
            user_id=args.userid,
            name=args.bankname
        )
    else:
        sys.stderr.write('Error: "{0}" is not a file.\n\n'.format(fname))
        parser.print_help()
        sys.exit(2)

    print('Calculated signature: {0}'.format(signature))
    print('Recorded signature:   {0}'
          .format(recorded_signature or '(No signature in XML document.)'))
    if signature != recorded_signature:
        print('Signatures are NOT equal!')
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
