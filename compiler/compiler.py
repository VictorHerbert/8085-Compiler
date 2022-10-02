from fileinput import filename
import re
from typing import Dict

from compiler.instruction import Instruction

from .tokens import *

class Compiler:

    WORD_SIZE = 2<<8

    
    def __init__(self,
        code: str,
        output_file : str,
        listings_file : str = None
    ) -> None:

        self.idx = 0
        self.labels = {}
        self.equ = {}
        self.memory = []
        self.memory_size = 0
        self.instructions = []

        self.lines = code.split('\n')
        self.output_file = output_file
        self.listings_file = listings_file

    def set_isa(self, isa: Dict[str, Instruction]) -> None:
        self.isa = isa

        
    def evaluate_expr(self, expr):
        expr = re.sub(fr'(?P<init>^|[+-/*()])(?P<name>{NAME})', lambda match: match.group('init') + str(self.labels[match.group('name')]), expr)
        expr = re.sub(r'(?P<hex_number>[0-9a-f]+)h', r'0x\g<hex_number>', expr)

        return eval(expr)
   
    def pre_compile(self, line_idx: int, line: str):
        rg = fr'^(?P<equ_label>{NAME}) *equ *(?P<expression>{EXPRESSION}) *$'
        match = re.match(rg, line)
        if match:
            equ_label = match.group('equ_label')
            equ_expression = match.group('expression')

            self.labels[equ_label] = self.evaluate_expr(equ_expression)
        else:
            rg = fr'^((?P<label>{NAME}) *:)? *(?P<mnemonic>{NAME}) *(?P<args>.*) *$'
            match = re.match(rg, line)

            if match:
                label = match.group('label')
                mnemonic = match.group('mnemonic')
                args = match.group('args').split(',')
            
                if not mnemonic in self.isa:
                    raise ValueError('Instruction not found')

                if mnemonic == 'org':
                    self.memory_size = max(self.memory_size, self.idx)
                    self.idx = int(args[0])

                if label:
                    self.labels[label] = self.idx

                self.instructions.append((line_idx, self.idx, mnemonic, args))
                
                self.idx += self.isa[mnemonic].length(args)


    def compile_instruction(self, instruction: str):
        line_idx, idx, mnemonic, args = instruction
        for i, v in enumerate(self.isa[mnemonic].assemble(args)):
            self.memory[idx+i] = v
    
    def compile(self, output, listing = None):
        error_count = 0
        for i, line in enumerate(self.lines):
            if line != '':
                try:
                    self.pre_compile(i, line)
                except KeyError as e:
                    error_count += 1
                    print(f'[ERROR](precompilation) {self.filename}({i+1}): Unknown symbol {e}')
                except SyntaxError as e:
                    error_count += 1
                    print(f'[ERROR](precompilation) {self.filename}({i+1}): {e.args[0]}')
                
        self.memory_size = max(self.memory_size, self.idx)
        self.memory = [0]*self.memory_size

        listing_str = r''
        for instruction in self.instructions:
            i, idx, mnemonic, args = instruction
            
            if mnemonic != 'org':
                self.compile_instruction(instruction)
            try:
                listing_str += f'{hex(idx).ljust(10)}{self.lines[i]}\n'
            except KeyError as e:
                error_count += 1
                print(f'[ERROR](compilation) {self.filename}({i}): Unknown symbol {e}')

        if not listing is None:
            print(listing_str, file=listing)
        if not error_count:
            output.write(bytearray(self.memory))

        return  error_count
