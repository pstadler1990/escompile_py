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
parser.add_argument('-f', '--file', type=str)
parser.add_argument('-e', '--execute', action='store_true')
args = parser.parse_args()

file_handle = None

if __name__ == '__main__':

    if args.file and len(args.file):
        if os.path.isabs(args.file):
            # Open file directly if exists
            with open(args.file, 'r') as f:
                file_handle = f.read()
        else:
            if C_CONFIG['script_dirs'] is None or not len(C_CONFIG['script_dirs']):
                raise FileNotFoundError('No script directories given')
            base_file = os.path.basename(args.file)
            # Walk through all dirs (and config.additional_dirs) if file found there
            found_file = False
            for a_dir in C_CONFIG['script_dirs']:
                for (dirpath, dirnames, filenames) in os.walk(a_dir):
                    for filename in filenames:
                        if filename == base_file:
                            found_file = True
                            with open(os.sep.join([dirpath, filename]), 'r') as f:
                                file_handle = f.read()
                            break
            if not found_file:
                raise FileNotFoundError('File {f} not found'.format(f=base_file))

    p = Parser()
    statements = p.parse(file_handle)

    if not args.parse:
        # Default
        c = CodeGenerator()
        for statement in statements:
            c.generate(statement)

        print(c.bytes_out)
        print(c.format())
        fbytes = c.finalize()

        # Execute parsed script?
        if args.execute:
            if C_CONFIG['vm_exe'] and os.path.exists(C_CONFIG['vm_exe']):
                # CALL vm.exe with bytes_out -b option
                subprocess.Popen([C_CONFIG['vm_exe'], "-b"] + fbytes)
                os.system('taskkill /f /im es_vm.exe')
