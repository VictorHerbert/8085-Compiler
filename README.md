# 8085-Compiler
A simple yet functional 8085 Compiler

# Requirements

* Python 3.10

# Usage

## CLI

To run it, just type 

    python -m compiler -i input_file.asm -o output_file.bin -l listings.txt

where -l is an optional listing output

## VsCode

![](https://github.com/VictorHerbert/8085-Compiler/blob/main/resources/screenshot.png?raw=true2)

The compiler can be run as a task or even in debug mode using provided launch.json and tasks.json files on .vscode folder.