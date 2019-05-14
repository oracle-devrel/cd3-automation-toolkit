#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import configparser
import pandas as pd

######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input groups file name from Default Section
# Groups are defined in csv format
# outfile is the name of output terraform file generated
######

parser = argparse.ArgumentParser(description="Create Compartments terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the properties file eg vcn-info.properties or CD3 excel file")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w")

tempStr = ""

if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Groups')
    for i in df.index:
        group_name = df.iat[i, 0]
        group_desc = df.iat[i, 1]

        NaNstr = 'NaN'
        if (str(group_desc).lower()== NaNstr.lower()):
            group_desc=''

        endNames = {'<END>', '<end>'}
        if (group_name in endNames):
            break

        if(group_name!='Name' and str(group_name).lower()!= NaNstr.lower()):
            tempStr=tempStr + """
resource "oci_identity_group" \"""" + group_name + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc + """"
	    name = \"""" + group_name + """"
	} """

if('.properties' in args.inputfile):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    group_file_name = config.get('Default', 'groups_file_name')
    fname = open(group_file_name, "r")

    # Read compartment file
    for line in fname:
        endNames = {'<END>', '<end>'}
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [group_name, group_desc] = line.split(',')

            if (group_desc.strip() == ''):
                group_desc=''


            if(group_name.strip()!='Name' and group_name.strip()!=''):
                tempStr=tempStr + """
resource "oci_identity_group" \"""" + group_name.strip() + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc.strip() + """"
	    name = \"""" + group_name.strip() + """"
	} """


oname.write(tempStr)
oname.close()