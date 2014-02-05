from __future__ import print_function
import os
import sc2bank
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
