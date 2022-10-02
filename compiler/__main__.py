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


isa = {
    'org'   : Instruction(fr'{EXPRESSION}', 0, lambda args: []),
    'jmp'   : Instruction(fr'{EXPRESSION}', 3, lambda args: [20, compiler.evaluate_expr(args[0])>>compiler.WORD_SIZE, compiler.evaluate_expr(args[0])%compiler.WORD_SIZE]),
    'db'    : Instruction(fr'{EXPRESSION}', 1, lambda args: [compiler.evaluate_expr(args[0])]),
    'ds'    : Instruction(fr'{EXPRESSION}', lambda args: int(args[0]), lambda args: [0]*int(args[0])),
    'mvi'   : Instruction(fr'{REGISTER}, *{EXPRESSION}', 2, lambda args: [66,67])
}

compiler.set_isa(isa)

error_count = compiler.compile(args.o, args.l)

if error_count == 0:
    print('Successful Compilation')
else:
    print()
    print(f'{error_count} error{"s" if error_count != 1 else ""} found')
    print('Compilation aborted')