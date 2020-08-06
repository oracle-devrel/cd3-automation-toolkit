#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com



import sys
import argparse
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd()+"/../..")
from commonTools import *


######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input groups file name from Default Section
# Groups are defined in csv format
# outfile is the name of output terraform file generated
######

## Start Processing

parser = argparse.ArgumentParser(description="Create Groups terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--configFileName", help="Config file name", required=False)


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

#Declare variables
args = parser.parse_args()
filename=args.inputfile
outdir=args.outdir
prefix=args.prefix

if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

outfile={}
oname={}
tfStr={}

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('groups-template')

#If input is cd3 file
if('.xls' in args.inputfile):

    # Read cd3 using pandas dataframe
    df = pd.read_excel(args.inputfile, sheet_name='Groups',skiprows=1,dtype=object)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region=region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan' :
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit()

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            #Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Name':
                columnvalue = columnvalue.strip()
                group_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'group_tf_name': group_tf_name}

            # If description field is empty; put name as description
            if columnname == 'Description':
                if columnvalue == "" or columnvalue == 'nan':
                    columnvalue = df.loc[i,'Name']

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region]=tfStr[region] + template.render(tempStr)

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

                compartment_id = 'var.tenancy_ocid'

                tfStr[region]=tfStr[region] + template.render(group_tf_name=group_name,compartment_id=compartment_id,group_desc=group_desc,group_name=group_name)
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

#Write TF string to the file in respective region directory
for reg in ct.all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-groups.tf'

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for groups has been created for region "+reg)

