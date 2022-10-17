import re
from typing import BinaryIO
from xml.dom import NotFoundErr

from compiler.instruction import Instruction

from .tokens import *

class Compiler:

    WORD_SIZE = 2<<8

    VERBOSE_ERRORS = 1
    VERBOSE_WARNINGS = 2
    VERBOSE_INFOS = 3

    
    def __init__(self,
        code: str,
        filename : str,
        listings_file : str = None,
        verbose : int = VERBOSE_ERRORS
    ) -> None:

        self.idx = 0
        self.labels = {}
        self.equ = {}
        self.memory = []
        self.memory_size = 0
        self.instructions = []

        self.lines = code.lower().split('\n')
        self.filename = filename
        self.listings_file = listings_file
        self.verbose = verbose

        macros = {
            'org'   : Instruction(fr'{EXPRESSION}', 0, lambda args: []),
            'db'    : Instruction(fr'{EXPRESSION}', 1, lambda args: [self.evaluate_expr(args[0])]),
            'ds'    : Instruction(fr'{EXPRESSION}', lambda args: int(args[0]), lambda args: [0]*int(args[0]))
        }

        single_inst = lambda op : Instruction([], 1, lambda args: [op])
        imm_inst = lambda op : Instruction([fr'{EXPRESSION}'], 2, lambda args: [op, self.evaluate_expr(args[0])])
        addr_imm_inst = lambda op : Instruction([fr'{EXPRESSION}'], 3, lambda args: [op, self.evaluate_expr(args[0], 1<<16)%256, self.evaluate_expr(args[0], 1<<16)//256])
        reg_inst_s = lambda op : Instruction([fr'{REGISTER}'], 1, lambda args: [op + self.evaluate_register(args[0])])
        reg_inst_d = lambda op : Instruction([fr'{REGISTER}'], 1, lambda args: [op + (self.evaluate_register(args[0])<<3)])
        reg_inst_ds = lambda op : Instruction([fr'{REGISTER}', fr'{REGISTER}'], 1, lambda args: [op + (self.evaluate_register(args[0])<<3) + self.evaluate_register(args[1])])
        reg_imm_inst_d = lambda op : Instruction([fr'{REGISTER}', fr'{EXPRESSION}'], 2, lambda args: [op + self.evaluate_register(args[0])<<3, self.evaluate_expr(args[1])])
        reg_double_inst = lambda op : Instruction([fr'{REGISTER}'], 1, lambda args: [op + self.evaluate_double_register(args[0])<<4])
        reg_double_inst_r = lambda op : Instruction([fr'{REGISTER}'], 1, lambda args: [op + self.evaluate_bd_register(args[0])<<4])
        reg_double_inst_addr = lambda op : Instruction([fr'{REGISTER}', fr'{EXPRESSION}'], 3, lambda args: [op + self.evaluate_double_register(args[0])<<4, self.evaluate_expr(args[1], 1<<16)%256, self.evaluate_expr(args[1], 1<<16)//256])
        rst_inst = lambda op : Instruction([fr'{NUMBER}'], 1, lambda args: [op + self.evaluate_expr(args[0], 1<<3)<<3])

        instructions = {
            'aci':  imm_inst(0b11001110),
            'adc':  reg_inst_s(0b10001000),
            'add':  reg_inst_s(0b10000000),
            'adi':  imm_inst(0b11000110),
            'ana':  reg_inst_s(0b10100000),
            'ani':  imm_inst(0b11100110),
            'call': addr_imm_inst(0b11001101),
            'cc':   addr_imm_inst(0b11011100),
            'cm':   addr_imm_inst(0b11111100),
            'cma':  single_inst(0b00101111),
            'cmc':  single_inst(0b00111111),
            'cmp':  reg_inst_s(0b10111000),
            'cnc':  addr_imm_inst(0b11011100),
            'cnz':  addr_imm_inst(0b11000100),
            'cp':   addr_imm_inst(0b11110100),
            'cpe':  addr_imm_inst(0b11101100),
            'cpi':  imm_inst(0b11111110),
            'cpo':  addr_imm_inst(0b11100100),
            'cz':   addr_imm_inst(0b11001100),
            'daa':  single_inst(0b00100111),
            'dad':  reg_double_inst(0b00001001),
            'dcr':  reg_inst_d(0b00000101),
            'dcx':  reg_double_inst(0b00001011),
            'ei':   single_inst(0b11111011),
            'hlt':  single_inst(0b01110110),
            'in':   imm_inst(0b11011011),
            'inr':  reg_inst_d(0b00000100),
            'inx':  reg_double_inst(0b00000011),
            'jc':   addr_imm_inst(0b11011010),
            'jm':   addr_imm_inst(0b11111010),
            'jmp':  addr_imm_inst(0b11000011),
            'jnc':  addr_imm_inst(0b11010010),
            'jnz':  addr_imm_inst(0b11000010),
            'jp':   addr_imm_inst(0b11110010),
            'jpe':  addr_imm_inst(0b11101010),
            'jpo':  addr_imm_inst(0b11100010),
            'jz':   addr_imm_inst(0b11001010),
            'lda':  addr_imm_inst(0b00111010),
            'ldax': reg_double_inst_r(0b00001010),
            'lhld': addr_imm_inst(0b00101010),
            'lxi':  reg_double_inst_addr(0b00000001),
            'mov':  reg_inst_ds(0b01000110),
            'mvi':  reg_imm_inst_d(0b00000110),
            'not':  single_inst(0b00000000),
            'ora':  reg_inst_d(0b10110000),
            'ori':  imm_inst(0b11110110),
            'out':  imm_inst(0b11010011),
            'phcl': single_inst(0b11101001),
            'pop':  reg_double_inst(0b11000001),
            'push': reg_double_inst(0b11000101),
            'ral':  single_inst(0b00010111),
            'rar':  single_inst(0b00011111),
            'rc':   single_inst(0b11011000),
            'ret':  single_inst(0b11001001),
            'rim':  single_inst(0b00100000),
            'rlc':  single_inst(0b00000111),
            'rm':   single_inst(0b11111000),
            'rnc':  single_inst(0b11010000),
            'rnz':  single_inst(0b11000000),
            'rp':   single_inst(0b11110000),
            'rpe':  single_inst(0b11101000),
            'rpo':  single_inst(0b11100000),
            'rrc':  single_inst(0b00001111),
            'rst':  rst_inst(0B11000111),
            'sbb':  reg_inst_s(0b100111000),
            'sbi':  single_inst(0b11011110),
            'shld': addr_imm_inst(0b00100010),
            'sim':  single_inst(0b00110000),
            'sphl': single_inst(0b11111001),
            'sta':  addr_imm_inst(0b00110010),
            'stax': reg_double_inst_r(0b00000010),
            'stc':  single_inst(0b00110111),
            'sub':  reg_inst_s(0b10010000),
            'sui':  single_inst(0b11010110),
            'xchg': single_inst(0b11101011),
            'xra':  reg_inst_s(0b10101000),
            'xri':  imm_inst(0b11101110),
            'xthl': single_inst(0b11100011),
        }

        self.isa = instructions | macros

    def  evaluate_register(self, register: str) -> int:
        regs = {'a': 0b111, 'b': 0b000, 'c': 0b001, 'd': 0b010, 'e': 0b011, 'h': 0b100, 'l': 0b101, 'm': 0b110}

        if not register in regs:
            raise NotFoundErr(register)
        
        return regs[register]

    def  evaluate_double_register(self, register: str) -> int:
        regs = {'b': 0b000, 'd': 0b010, 'h': 0b100}

        if not register in regs:
            raise NotFoundErr(register)
        
        return regs[register]
    
    def  evaluate_bd_register(self, register: str) -> int:
        bd = {'b' : 0b0, 'd': 0b1}
        
        if not register in bd:
            raise NotFoundErr(register)
        
        return bd[register]
        
    def evaluate_expr(self, expr: str, limit: int = 1<<8) -> int:
        expr = re.sub(fr'(?P<init> |^|[+-/*()])(?P<name>{NAME})', lambda match: match.group('init') + str(self.labels[match.group('name')]), expr)
        expr = re.sub(r'(?P<hex_number>[0-9a-f]+)h', r'0x\g<hex_number>', expr)
        res = eval(expr)

        if res > limit:
            raise OverflowError()

        return res
   
    def pre_compile(self, line_idx: int, line: str) -> None:
        rg = fr'^ *(?P<equ_label>{NAME}) *equ *(?P<expression>{EXPRESSION}) *$'
        match = re.match(rg, line)
        if match:
            equ_label = match.group('equ_label')
            equ_expression = match.group('expression')

            self.labels[equ_label] = self.evaluate_expr(equ_expression, 1<<16)
        else:
            rg = fr'^ *((?P<label>{NAME}) *:)? *(?P<mnemonic>{NAME}) *(?P<args>.*) *$'
            match = re.match(rg, line)

            if match:
                label = match.group('label')
                mnemonic = match.group('mnemonic')
                args = match.group('args').replace(' ','').split(',')
            
                if not mnemonic in self.isa:
                    raise SyntaxError()

                if mnemonic == 'org':
                    self.memory_size = max(self.memory_size, self.idx)
                    self.idx = int(args[0])

                if label:
                    self.labels[label] = self.idx

                self.instructions.append((line_idx, self.idx, mnemonic, args))
                
                self.idx += self.isa[mnemonic].length(args)


    def compile_instruction(self, instruction: str) -> None:
        line_idx, idx, mnemonic, args = instruction
        for i, v in enumerate(self.isa[mnemonic].assemble(args)):
            if (not self.memory[idx+i] is None) and self.verbose >= 2:
                print(f'[Warning] {self.filename}({line_idx}): Memory overwrite at {hex(idx+i)}')

            self.memory[idx+i] = v
    
    def compile(self, output: BinaryIO, listing = None) -> int:
        error_count = 0
        for i, line in enumerate(self.lines):
            if line != '':
                line = line.split(';')[0]
                try:
                    self.pre_compile(i, line)
                except KeyError as e:
                    error_count += 1
                    print(f'[ERROR] {self.filename}({i+1}): Unknown symbol {e}')
                except SyntaxError as e:
                    error_count += 1
                    print(f'[ERROR] {self.filename}({i+1}): Instruction not found')
                
        self.memory_size = max(self.memory_size, self.idx)
        self.memory = [None]*self.memory_size

        listing_str = r''
        padding = 10
        for instruction in self.instructions:
            i, idx, mnemonic, args = instruction
            
            try:
                if mnemonic != 'org':
                    self.compile_instruction(instruction)
                    listing_str += f'{hex(idx).ljust(padding)}{self.lines[i]}\n'
                else:
                    listing_str += f'{" "*padding} {self.lines[i]}\n'
            except KeyError as e:
                error_count += 1
                print(f'[ERROR] {self.filename}({i+1}): Unknown symbol {e}')
            except OverflowError as e:
                error_count += 1
                print(f'[ERROR] {self.filename}({i+1}): Overflow error {e}')
            except NotFoundErr as e:
                error_count += 1
                print(f'[ERROR] {self.filename}({i+1}): Register {e} not found')
            
        
        if error_count == 0:
            if not listing is None:
                print(listing_str, file=listing)

            self.memory = [(x if (not x is None) else 0) for x in self.memory]
            output.write(bytearray(self.memory))

            if self.verbose >= self.VERBOSE_INFOS:
                print('Successful Compilation')
        else:
            print()
            print(f'{error_count} error{"s" if error_count != 1 else ""} found')
            print('Compilation aborted')

        return error_count
 