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
# if properties file is the input then Code will read input compartment file name from Default Section
# Compartments are defined in csv format
# outfile is the name of output terraform file generated
######

## Start Processing

parser = argparse.ArgumentParser(description="Create Compartments terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("prefix", help="customer name/prefix for all file names")


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

#Declare variables
filename=args.inputfile
outdir=args.outdir
prefix=args.prefix
outfile={}
oname={}
tfStr={}

c=0

#reversal path function
def travel(parent, keys, values, c):
    if (parent == "" or parent =="nan" or parent == "root"):
        return ""
    else:
        if ( "::" in str(values[keys.index(parent)])):
           if(c==0):
               return values[keys.index(parent)]+"::"+parent
           c = c + 1
           return values[keys.index(parent)]
        return travel(values[keys.index(parent)],keys,values,c)+"::"+parent



#If input in cd3 file
if('.xls' in args.inputfile):
    # Get vcnInfo object from commonTools
    vcnInfo = parseVCNInfo(args.inputfile)

    #Read cd3 using pandas dataframe
    df = pd.read_excel(args.inputfile, sheet_name='Compartments',skiprows=1)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    #To handle duplicates during export process
    df=df.drop_duplicates(ignore_index=True)

    #Initialise empty TF string for each region
    for reg in vcnInfo.all_regions:
        tfStr[reg] = ''
    #Separating Compartments and ParentComparements into list
    ckeys=[]
    pvalues=[]
    for i in df.index:
        if (df.iat[i,0] in commonTools.endNames):
            break
        ckeys.append(str(df.iat[i, 1]).strip())
        pvalues.append(str(df.iat[i, 3]).strip())


    #Iterate over rows
    for i in df.index:
        region = str(df.iat[i,0])

        #Encountered <End>
        if (region in commonTools.endNames):
            break

        region=region.strip().lower()

        #If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in vcnInfo.all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

        #Fetch column values for each row
        compartment_name = str(df.iat[i, 1]).strip()
        compartment_desc = str(df.iat[i, 2]).strip()
        parent_compartment_name = str(df.iat[i, 3]).strip()
        var_c_name = ""
        # Build compartment TF
        if (str(parent_compartment_name).lower() == "nan" or str(parent_compartment_name).lower() == 'root' or str(parent_compartment_name).lower() == ""):
            var_c_name = compartment_name
            parent_compartment = '${var.tenancy_ocid}'
        else:
            if (ckeys.count(str(parent_compartment_name)) > 1):
                print("Could not find Path for " + compartment_name + "Please give Full Path")
                exit(1)
            elif ("::" in parent_compartment_name):
                var_c_name = parent_compartment_name + "::" + compartment_name
                parent_compartment = commonTools.check_tf_variable(parent_compartment_name)
                parent_compartment = '${oci_identity_compartment.' + parent_compartment + '.id}'
            else:
                if (parent_compartment_name not in ckeys):
                    print("There is no parent compartment with name " + parent_compartment_name + " to create " + compartment_name + " compartment")
                    exit(1)
                parent_compartment = travel(parent_compartment_name, ckeys, pvalues, c)
                var_c_name = parent_compartment + "::" + compartment_name
                if (len(parent_compartment) > 1 and parent_compartment[0] == ":" and parent_compartment[1] == ":"):
                    parent_compartment = parent_compartment[2:]
                    var_c_name = parent_compartment + "::" + compartment_name
                parent_compartment = commonTools.check_tf_variable(parent_compartment)
                parent_compartment = '${oci_identity_compartment.' + parent_compartment + '.id}'

        var_c_name = commonTools.check_tf_variable(var_c_name)

        if (str(compartment_name).lower() != "nan"):
            region = region.strip().lower()
            compartment_name = compartment_name.strip()
            # If description field is empty; put name as description
            if (str(compartment_desc).lower() == "nan"):
                compartment_desc = compartment_name

            # Write all info to TF string
            tfStr[region] = tfStr[region] + """
        resource "oci_identity_compartment" \"""" + var_c_name + """" {
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

#Write TF string to the file in respective region directory
for reg in vcnInfo.all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-compartments.tf'

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for compartments has been created for region "+reg)
