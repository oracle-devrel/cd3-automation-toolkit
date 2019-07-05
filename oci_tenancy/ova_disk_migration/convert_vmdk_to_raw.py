#!/bin/python

### Converts a VMDK File to RAW ####

import argparse
import os
import sys
import subprocess
import glob

parser = argparse.ArgumentParser(description="Convert all vmdk files in a dir to raw format.  Using the -file option will convert only that particular file. Files with the name -disk1 will automatically be skipped")
group = parser.add_mutually_exclusive_group()
group.add_argument("-vmdk_dir",help="The full path of where the vmdk can be found <staging_dir/vm_name>")
group.add_argument("-file",help="Full Path of file to process.")


args = parser.parse_args()

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

process_all = 0
if not args.file:
        process_all = 1

glob_search = ""
if process_all == 1:
        glob_search = args.vmdk_dir + "/*.vmdk"
        vmdks =  glob.glob(glob_search)
else:
        vm_file = args.file
        vmdks = [vm_file]

for vm in vmdks:
        if "-disk1" not in vm:
                ova_pos = vm.rfind(".")
                raw_file_name = vm[0:ova_pos] + ".raw"
                print ("raw_file_name")
                print ("Converting " + vm + " to raw format " + raw_file_name)
                subprocess.call(['qemu-img','convert', '-f','vmdk', '-O','raw' ,vm,raw_file_name])
