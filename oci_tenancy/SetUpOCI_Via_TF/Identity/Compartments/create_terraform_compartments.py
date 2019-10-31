#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import os
import pandas as pd

######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input compartment file name from Default Section
# Compartments are defined in csv format
# outfile is the name of output terraform file generated
######


parser = argparse.ArgumentParser(description="Create Compartments terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir=args.outdir
prefix=args.prefix

outfile={}
oname={}
tfStr={}


if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Compartments',skiprows=1)
    df.dropna(how='all')
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    # Get Property Values
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions=all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        tfStr[reg] = ''

    NaNstr = 'NaN'
    endNames = {'<END>', '<end>', '<End>'}

    for i in df.index:
        region = df.iat[i,0]

        if (region in endNames):
            break

        region=region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)
        compartment_name = df.iat[i, 1]


        compartment_desc = df.iat[i, 2]
        parent_compartment_name = df.iat[i, 3]
        if (str(parent_compartment_name).lower()== NaNstr.lower() or parent_compartment_name.lower() == 'root'):
            parent_compartment='${var.tenancy_ocid}'
        else:
            parent_compartment='${oci_identity_compartment.'+parent_compartment_name.strip()+'.id}'
        if (str(compartment_name).lower() != NaNstr.lower()):
            region = region.strip().lower()

            compartment_name = compartment_name.strip()
            if (str(compartment_desc).lower() == NaNstr.lower()):
                compartment_desc = compartment_name
            tfStr[region]=tfStr[region] + """
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
	    compartment_id = \"""" + parent_compartment + """"
	    description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"
} """

#If input is a csv file
elif('.csv' in args.inputfile):
    all_regions = os.listdir(outdir)
    for reg in all_regions:
        tfStr[reg] = ''
    compartment_file_name = args.inputfile
    fname = open(compartment_file_name, "r")

    endNames = {'<END>', '<end>', '<End>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [region,compartment_name, compartment_desc, parent_compartment_name] = line.split(',')
            region=region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
            compartment_name=compartment_name.strip()
            compartment_desc=compartment_desc.strip()
            parent_compartment_name=parent_compartment_name.strip()

            if (parent_compartment_name.strip() == '' or parent_compartment_name.lower() == 'root'):
                parent_compartment = '${var.tenancy_ocid}'
            else:
                parent_compartment = '${oci_identity_compartment.' + parent_compartment_name + '.id}'

            if(compartment_name.strip()!='Name' and compartment_name.strip()!=''):
                if (compartment_desc.strip() == ''):
                    compartment_desc = compartment_name
                tfStr[region]=tfStr[region] + """
resource "oci_identity_compartment" \"""" + compartment_name.strip() + """" {
        compartment_id = \"""" + parent_compartment + """"
        description = \"""" + compartment_desc.strip() + """"
  	    name = \"""" + compartment_name.strip() + """"
} """

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()


for reg in all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-compartments.tf'

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for compartments has been created for region "+reg)


