#!/bin/bash
# Author: Shruthi Subramanian
# Attach the tags created to the servers
import sys
import argparse

parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
parser.add_argument("file", help="Full Path of CSV file.Ex:tag_server-csv-example.csv in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file

outdir = args.outdir

args = parser.parse_args()

fname = open(filename, "r")

# Read csv file
for line in fname:
    if not line.startswith('#'):
        if line.startswith('Hostname'):
            linearr = line.split(",")
            header = linearr[0].strip()
            namespace_1 = linearr[1].strip()
            namespace_2 = linearr[2].strip()
            namespace_3 = linearr[3].strip()
            namespace_4 = linearr[4].strip()
        else:
            print ("\n")
            print line
            # [availability_domain, compartment_name,imag_var_name, shape, subnet_name, display_name, hostname_label, private_ip, skip_source_dest_check,assign_public_ip,fault_domain,source_type,ssh_public_key] = line.split(',')
            linearr = line.split(",")
            hostname = linearr[0].strip()

            tmp1 = linearr[1].strip()
            tmp = tmp1.split("=")
            tag1key = tmp[0].strip()
            value1 = tmp[1].strip()
            print (tag1key, value1)

            tmp2 = linearr[2].strip()
            tmp = tmp2.split("=")
            tag2key = tmp[0].strip()
            value2 = tmp[1].strip()
            print (tag2key, value2)

            tmp3 = linearr[3].strip()
            tmp = tmp3.split("=")
            tag3key = tmp[0].strip()
            value3 = tmp[1].strip()
            print (tag3key, value3)

            tmp4 = linearr[4].strip()
            tmp = tmp4.split("=")
            tag4key = tmp[0].strip()
            value4 = tmp[1].strip()
            print (tag4key, value4)

            tmpstr = """
            defined_tags = {
                    \"""" + namespace_1 + """.""" + tag1key + """\"=\"""" + value1 + """\",
                    \"""" + namespace_2 + """.""" + tag2key + """\"=\"""" + value2 + """\",
                    \"""" + namespace_3 + """.""" + tag3key + """\"=\"""" + value3 + """\",
                    \"""" + namespace_4 + """.""" + tag4key + """\"=\"""" + value4 + """\"
            }
            ## Defined Tag Info ##
            """
            testToSearch = "## Defined Tag Info ##"
            terrafile = hostname + ".tf"
            print terrafile

            with open(terrafile, 'r') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace(testToSearch, tmpstr)

            # Write the file out again
            with open(terrafile, 'w') as file:
                file.write(filedata)
fname.close()




