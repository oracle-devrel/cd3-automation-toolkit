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
tempStr=''


if('.xls' in args.inputfile):
    vcnInfo = parseVCNInfo(args.inputfile)
    df = pd.read_excel(args.inputfile, sheet_name='Policies',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    count = 0
    regions=df['Region']
    regions.dropna()

    check_diff_region=[]

    for j in regions.index:
        if(regions[j] not in check_diff_region and regions[j] not in commonTools.endNames and str(regions[j]).lower() != "nan"):
            check_diff_region.append(regions[j])

    if(len(check_diff_region)>1):
        print("Policies can be created only in Home Region; You have specified different regions for different policies...Exiting...")
        exit(1)
    for i in df.index:
        region=df.iat[i,0]
        if (region in commonTools.endNames):
            break
        if check_diff_region[0].strip().lower() not in vcnInfo.all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)
        policy_name = df.iat[i, 1]

        if (str(policy_name).lower() != "nan"):
            policy_tf_name = commonTools.tfname.sub("-", policy_name)
            count=count +1
            policy_compartment_name = df.iat[i, 2]
            if (str(policy_compartment_name).lower() == "nan" or policy_compartment_name.lower() == 'root'):
                policy_compartment = '${var.tenancy_ocid}'
            else:
                #policy_compartment = '${oci_identity_compartment.' + policy_compartment_name + '.id}'
                policy_compartment = '${var.' + policy_compartment_name + '}'


            policy_desc = df.iat[i, 3]
            if (str(policy_desc).lower() == "nan"):
                policy_desc = policy_name

            policy_statement = df.iat[i,4]
            actual_policy_statement = policy_statement
            if ('$' in policy_statement):
                policy_statement_grps = df.iat[i, 5]

                """policy_statement_grps = policy_statement_grps.split(",")
                grp_tf=""
                k = 0
                for policy_statement_grp in policy_statement_grps:
                    k=k+1
                    if(k==1):
                        grp_tf = grp_tf +'${oci_identity_group.' + policy_statement_grp + '.name}'
                    if(k!=1):
                        grp_tf=grp_tf+","+'${oci_identity_group.' + policy_statement_grp + '.name}'
                actual_policy_statement=policy_statement.replace('$', grp_tf)
                """
                actual_policy_statement=policy_statement.replace('$', policy_statement_grps)
            if('compartment *' in policy_statement):
                policy_statement_comp = df.iat[i, 6]
                #comp_tf = '${oci_identity_compartment.' + policy_statement_comp + '.name}'
                #comp_tf = '${var.' + policy_statement_comp + '}'
                comp_tf = policy_statement_comp
                actual_policy_statement=actual_policy_statement.replace('compartment *', 'compartment '+comp_tf)
            if(count!=1):
                tempStr = tempStr + """ ]
        }"""
            tempStr=tempStr + """
    resource "oci_identity_policy" \"""" + policy_tf_name + """" {
            compartment_id = \"""" + policy_compartment + """" 
            description = \"""" + policy_desc.strip() + """"
            name = \"""" + policy_name.strip() + """"
            statements = [ \"""" + actual_policy_statement.strip() + """" """

        if(str(policy_name).lower() == "nan"):
            policy_statement = df.iat[i, 4]
            if(str(policy_statement).lower() != "nan"):
                actual_policy_statement = policy_statement
                if ('$' in policy_statement):
                    policy_statement_grps = df.iat[i, 5]
                    """policy_statement_grps= policy_statement_grps.split(",")
                    grp_tf = ""
                    j = 0
                    for policy_statement_grp in policy_statement_grps:
                        j = j + 1
                        if (j == 1):
                            grp_tf = grp_tf + '${oci_identity_group.' + policy_statement_grp + '.name}'
                        if (j != 1):
                            grp_tf = grp_tf + "," + '${oci_identity_group.' + policy_statement_grp + '.name}'

                    actual_policy_statement = policy_statement.replace('$', grp_tf)
                    """
                    actual_policy_statement = policy_statement.replace('$', policy_statement_grps)
                if ('compartment *' in policy_statement):
                    policy_statement_comp = df.iat[i, 6]
                    #comp_tf = '${oci_identity_compartment.' + policy_statement_comp + '.name}'
                    #comp_tf = '${var.' + policy_statement_comp + '}'
                    comp_tf = policy_statement_comp
                    actual_policy_statement = actual_policy_statement.replace('compartment *', 'compartment '+comp_tf)

                tempStr = tempStr + """, 
                    \"""" + actual_policy_statement.strip() + "\""""

    tempStr = tempStr + """ ]
        }
    """

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx")
    exit()

if(len(check_diff_region)!=0):
    reg=check_diff_region[0].strip().lower()
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-policies.tf'

    oname[reg]=open(outfile[reg],'w')
    oname[reg].write(tempStr)
    oname[reg].close()
    print(outfile[reg] + " containing TF for policies has been created for region "+reg)

