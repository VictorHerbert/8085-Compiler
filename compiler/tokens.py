import re

HEX_NUMBER = r'([0-9a-f]+h)'
DEC_NUMBER = r'([0-9]+)'
NUMBER = fr'({HEX_NUMBER}|{DEC_NUMBER})'
NAME = r'([a-z][a-z0-9]*)'
LABEL = fr'({NUMBER}|{NAME})'
REGISTER = r'(a|b|c|d|e|h|l)'
OPERATORS = r'[-+/*]'
EXPRESSION = fr'(\(* *{LABEL} *\)* *( *{OPERATORS} *\(* *{LABEL} *\)*)*)'
NUMERIC_EXPRESSION = fr'(\(* *{NUMBER} *\)* *( *{OPERATORS} *\(* *{NUMBER} *\)*)*)'
