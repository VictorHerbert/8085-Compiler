import sys
import argparse

from .instruction import Instruction
from .tokens import *
from .compiler import Compiler


parser = argparse.ArgumentParser(prog='Compiler', description='Process some integers.')
parser.add_argument('-i', required=True, type=argparse.FileType('r'))
parser.add_argument('-o', required=True, type=argparse.FileType('wb'))
parser.add_argument('-l', required=False, type=argparse.FileType('w'))
args = parser.parse_args()


code = args.i.read()
compiler = Compiler(code, args.i.name)

error_count = compiler.compile(args.o, args.l)

if error_count == 0:
    print('Successful Compilation')
else:
    print()
    print(f'{error_count} error{"s" if error_count != 1 else ""} found')
    print('Compilation aborted')