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

ash_dir=outdir+"/ashburn"
phx_dir=outdir+"/phoenix"

if not os.path.exists(ash_dir):
        os.makedirs(ash_dir)

if not os.path.exists(phx_dir):
        os.makedirs(phx_dir)

outfile_ash=ash_dir + "/" + prefix + '-groups.tf'
outfile_phx=phx_dir + "/" + prefix + '-groups.tf'

tempStrASH = ""
tempStrPHX = ""

if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Groups',skiprows=1)
    df.dropna(how='all')
    NaNstr = 'NaN'
    endNames = {'<END>', '<end>'}

    for i in df.index:
        region=df.iat[i,0]
        if (region in endNames):
            break
        group_name = df.iat[i, 1]
        group_desc = df.iat[i, 2]
        if(str(group_name).lower()!= NaNstr.lower()):
            region = region.strip().lower()
            group_name = group_name.strip()
            if (str(group_desc).lower() == NaNstr.lower()):
                group_desc = group_name
            if(region=='ashburn'):
                tempStrASH=tempStrASH + """
resource "oci_identity_group" \"""" + group_name.strip() + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc.strip() + """"
	    name = \"""" + group_name.strip() + """"
	} """
            if (region == 'phoenix'):
                tempStrPHX = tempStrPHX + """
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

if(tempStrASH!=''):
    oname_ash = open(outfile_ash, "w")
    oname_ash.write(tempStrASH)
    oname_ash.close()
    print(outfile_ash + " containing TF for groups has been created")

if(tempStrPHX!=''):
    oname_phx = open(outfile_phx, "w")
    oname_phx.write(tempStrASH)
    oname_phx.close()
    print(outfile_phx + " containing TF for groups has been created")

