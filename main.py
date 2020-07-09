import os
import subprocess
from esc.codegen import CodeGenerator
from esc.parser import Parser
import argparse
import yaml
import sys

with open('config.yml') as file:
    C_CONFIG = yaml.load(file, Loader=yaml.FullLoader)

C_VERSION = '0.1a'

if C_CONFIG['debug'] is True:
    print("Debug mode enabled")
    sys.tracebacklimit = 1
else:
    sys.tracebacklimit = 0

parser = argparse.ArgumentParser(description='evoscript CLI {v}'.format(v=C_VERSION))
parser.add_argument('-p', '--parse', action='store_true')
parser.add_argument('-i', '--input', type=str)
parser.add_argument('-o', '--output', type=str)
parser.add_argument('-e', '--execute', action='store_true')
parser.add_argument('-l', '--stdlib', type=str)
parser.add_argument('-v', '--vm', type=str)
# Compiler specific limits for pre-executional boundary checking (optional)
parser.add_argument('-vmos', '--vmoutsize', type=int)

args = parser.parse_args()

file_dir = None
file_handle = None

if __name__ == '__main__':

    if args.input and len(args.input):
        if os.path.isabs(args.input):
            # Open file directly if exists
            with open(args.input, 'r') as f:
                file_handle = f.read()
        else:
            if C_CONFIG['script_dirs'] is None or not len(C_CONFIG['script_dirs']):
                raise FileNotFoundError('No script directories given')
            base_file = os.path.basename(args.input)
            # Walk through all dirs (and config.additional_dirs) if file found there
            found_file = False
            for a_dir in C_CONFIG['script_dirs']:
                for (dirpath, dirnames, filenames) in os.walk(a_dir):
                    for filename in filenames:
                        if filename == base_file:
                            found_file = True
                            file_dir = dirpath
                            with open(os.sep.join([dirpath, filename]), 'r') as f:
                                file_handle = f.read()
                            break
            if not found_file:
                raise FileNotFoundError('File {f} not found'.format(f=base_file))
    else:
        print("** No file option given, exit")
        sys.exit(-1)

    if args.stdlib:
        lib_dir = args.stdlib
    else:
        lib_dir = C_CONFIG['stdlib_dir']

    p = Parser(stdlib_dir=lib_dir)
    statements = p.parse(file_handle)

    if not args.parse:
        # Default
        c = CodeGenerator()
        for statement in statements:
            c.generate(statement)

        # print(c.bytes_out)
        print(c.format())
        fbytes = c.finalize(rle=C_CONFIG['use_rle'], poutsize=args.vmoutsize)

        if args.output:
            # Write file to output
            if os.path.isabs(args.output):
                out = args.output
            else:
                out = os.sep.join([file_dir, args.output])
            with open(out, 'w') as f:
                if C_CONFIG['use_rle']:
                    f.write(fbytes)
                else:
                    for b in fbytes:
                        out_f = format(int(b), 'x')
                        if len(out_f) < 2:
                            out_f = '0'+out_f
                        f.write(out_f)
            print("** WROTE {b} bytes to file {f}".format(b=len(fbytes), f=out))

        # Execute parsed script?
        if args.execute:
            if args.vm:
                vm_dir = args.vm
            else:
                vm_dir = C_CONFIG['vm_exe']
            if os.path.exists(vm_dir):
                # CALL vm.exe with bytes_out -b option
                subprocess.Popen([vm_dir, "-b"] + fbytes)
                os.system('taskkill /f /im es_vm.exe')
