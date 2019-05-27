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
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)
if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w+")

#compartments=[]
tempStr = ""

if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Compartments')
    NaNstr = 'NaN'
    endNames = {'<END>', '<end>'}

    for i in df.index:
        compartment_name = df.iat[i, 0]
        compartment_name = compartment_name.strip()

        if (compartment_name in endNames):
            break

        compartment_desc = df.iat[i, 1]
        parent_compartment_name = df.iat[i, 2]
        compartment_desc = compartment_desc.strip()
        parent_compartment_name = parent_compartment_name.strip()

        if (str(parent_compartment_name).lower()== NaNstr.lower() or parent_compartment_name.lower() == 'root'):
            parent_compartment='${var.tenancy_ocid}'
        else:
            parent_compartment='${oci_identity_compartment.'+parent_compartment_name+'.id}'

        if(compartment_name!='Name' and str(compartment_name).lower()!= NaNstr.lower()):
            if (str(compartment_desc).lower() == NaNstr.lower()):
                compartment_desc = compartment_name

            tempStr=tempStr + """
resource "oci_identity_compartment" \"""" + compartment_name + """" {
	    compartment_id = \"""" + parent_compartment + """"
	    description = \"""" + compartment_desc + """"
  	    name = \"""" + compartment_name + """"

	} """

#If input is a csv file
elif('.csv' in args.inputfile):
    compartment_file_name = args.inputfile
    fname = open(compartment_file_name, "r")

    endNames = {'<END>', '<end>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [compartment_name, compartment_desc, parent_compartment_name] = line.split(',')
            compartment_name=compartment_name.strip()
            compartment_desc=compartment_desc.strip()
            parent_compartment_name=parent_compartment_name.strip()

            if (parent_compartment_name.strip() == '' or parent_compartment_name.lower() == 'root'):
                parent_compartment = '${var.tenancy_ocid}'
            else:
                parent_compartment = '${oci_identity_compartment.' + parent_compartment_name + '.id}'

            if(compartment_name.strip()!='Name' and compartment_name.strip()!=''):
                #compartments.append(compartment_name)
                if (compartment_desc.strip() == ''):
                    compartment_desc = compartment_name

                tempStr=tempStr + """
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
        compartment_id = \"""" + parent_compartment + """"
        description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"

    } """
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")


oname.write(tempStr)
oname.close()
print(outfile +" containing TF for compartments has been created")
