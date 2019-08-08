#!/bin/python
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import pandas as pd
import os

######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input groups file name from Default Section
# Groups are defined in csv format
# outfile is the name of output terraform file generated
######

parser = argparse.ArgumentParser(description="Create Groups terraform file")
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
    df = pd.read_excel(args.inputfile, sheet_name='Groups',skiprows=1)
    df.dropna(how='all')
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    # Get Property Values
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        tfStr[reg] = ''

    NaNstr = 'NaN'
    endNames = {'<END>', '<end>'}

    for i in df.index:
        region=df.iat[i,0]
        if (region in endNames):
            break
        region=region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

        group_name = df.iat[i, 1]
        group_desc = df.iat[i, 2]
        if(str(group_name).lower()!= NaNstr.lower()):
            region = region.strip().lower()
            group_name = group_name.strip()
            if (str(group_desc).lower() == NaNstr.lower()):
                group_desc = group_name
            tfStr[region]=tfStr[region] + """
resource "oci_identity_group" \"""" + group_name.strip() + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc.strip() + """"
	    name = \"""" + group_name.strip() + """"
	} """

#If input is a csv file
elif('.csv' in args.inputfile):
    group_file_name = args.inputfile
    fname = open(group_file_name, "r")

    endNames = {'<END>', '<end>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [region,group_name, group_desc] = line.split(',')
            region=region.strip().lower()
            group_name=group_name.strip()
            group_desc=group_desc.strip()

            if(group_name!='Name' and group_name!=''):
                if (group_desc.strip() == ''):
                    group_desc = group_name
                if(region=='ashburn'):
                    tempStrASH=tempStrASH + """
resource "oci_identity_group" \"""" + group_name + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc + """"
	    name = \"""" + group_name + """"
	} """
                if (region == 'phoenix'):
                    tempStrPHX = tempStrPHX + """
                resource "oci_identity_group" \"""" + group_name + """" {
                	    compartment_id = "${var.tenancy_ocid}"
                	    description = \"""" + group_desc + """"
                	    name = \"""" + group_name + """"
                	} """
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

for reg in all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-groups.tf'

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for groups has been created for region "+reg)

