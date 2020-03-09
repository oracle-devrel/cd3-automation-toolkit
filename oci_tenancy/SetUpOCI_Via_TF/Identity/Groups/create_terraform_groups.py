#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../..")
from commonTools import *


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
    vcnInfo = parseVCNInfo(args.inputfile)
    df = pd.read_excel(args.inputfile, sheet_name='Groups',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for reg in vcnInfo.all_regions:
        tfStr[reg] = ''

    for i in df.index:
        region=df.iat[i,0]
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()
        if region not in vcnInfo.all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

        group_name = df.iat[i, 1]
        group_desc = df.iat[i, 2]
        if(str(group_name).lower()!= "nan"):
            region = region.strip().lower()
            group_name = group_name.strip()
            group_tf_name = commonTools.tfname.sub("-", group_name)

            if (str(group_desc).lower() == "nan"):
                group_desc = group_name
            tfStr[region]=tfStr[region] + """
resource "oci_identity_group" \"""" +group_tf_name + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc.strip() + """"
	    name = \"""" + group_name.strip() + """"
	} """

#If input is a csv file
elif('.csv' in args.inputfile):
    all_regions = os.listdir(outdir)
    for reg in all_regions:
        tfStr[reg] = ''

    group_file_name = args.inputfile
    fname = open(group_file_name, "r")

    endNames = {'<END>', '<end>', '<End>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [region,group_name, group_desc] = line.split(',')
            region=region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
            group_name=group_name.strip()
            group_desc=group_desc.strip()

            if(group_name!='Name' and group_name!=''):
                if (group_desc.strip() == ''):
                    group_desc = group_name
                tfStr[region]=tfStr[region] + """
resource "oci_identity_group" \"""" + group_name + """" {
	    compartment_id = "${var.tenancy_ocid}"
	    description = \"""" + group_desc + """"
	    name = \"""" + group_name + """"
	} """

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

for reg in vcnInfo.all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-groups.tf'

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for groups has been created for region "+reg)

