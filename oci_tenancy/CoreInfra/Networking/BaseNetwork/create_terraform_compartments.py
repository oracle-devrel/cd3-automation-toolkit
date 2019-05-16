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
# if properties file is the input then Code will read input compartment file name from Default Section
# Compartments are defined in csv format
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
    df = pd.read_excel(args.inputfile, sheet_name='Compartments')
    for i in df.index:
        compartment_name = df.iat[i, 0]
        compartment_desc = df.iat[i, 1]
        parent_compartment_name = df.iat[i, 2]

        NaNstr = 'NaN'
        if (str(parent_compartment_name).lower()== NaNstr.lower()):
            parent_compartment_name='tenancy_ocid'

        if (str(compartment_desc).lower()== NaNstr.lower()):
            compartment_desc=''

        endNames = {'<END>', '<end>'}
        if (compartment_name in endNames):
            break

        if(compartment_name!='Name' and str(compartment_name).lower()!= NaNstr.lower()):
            tempStr=tempStr + """
resource "oci_identity_compartment" \"""" + compartment_name + """" {
	    compartment_id = "${var.""" + parent_compartment_name + """}"
	    description = \"""" + compartment_desc + """"
  	    name = \"""" + compartment_name + """"

	} """

if('.properties' in args.inputfile):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    compartment_file_name = config.get('Default', 'compartments_file_name')
    fname = open(compartment_file_name, "r")

    # Read compartment file
    for line in fname:
        endNames = {'<END>', '<end>'}
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [compartment_name, compartment_desc, parent_compartment_name] = line.split(',')

            if (parent_compartment_name.strip() == ''):
                parent_compartment_name='tenancy_ocid'

            if (compartment_desc.strip() == ''):
                compartment_desc=''

            if(compartment_name.strip()!='Name' and compartment_name.strp()!=''):
                tempStr=tempStr + """`
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
        compartment_id = "${var.""" + parent_compartment_name.strip() + """}"
        description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"

    } """



oname.write(tempStr)
oname.close()