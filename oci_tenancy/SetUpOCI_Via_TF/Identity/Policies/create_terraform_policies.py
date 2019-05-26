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
oname = open(outfile,"w")

tempStr = ""

if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='Policies')
    NaNstr = 'NaN'
    endNames = {'<END>', '<end>'}
    count = 0
    for i in df.index:
        policy_name = df.iat[i, 0]

        if (policy_name in endNames):
            break

        if (str(policy_name).lower() != NaNstr.lower() and policy_name!='Name'):
            count=count +1
            policy_compartment_name = df.iat[i, 1]
            if (str(policy_compartment_name).lower() == NaNstr.lower() or policy_compartment_name.lower() == 'root'):
                policy_compartment = '${var.tenancy_ocid}'
            else:
                policy_compartment = '${oci_identity_compartment.' + policy_compartment_name + '.id}'


            policy_desc = df.iat[i, 2]
            if (str(policy_desc).lower() == NaNstr.lower()):
                policy_desc = policy_name

            policy_statement = df.iat[i,3]
            policy_statement_grps = df.iat[i, 4]
            policy_statement_grps = policy_statement_grps.split(",")
            grp_tf=""
            k = 0
            for policy_statement_grp in policy_statement_grps:
                k=k+1
                if(k==1):
                    grp_tf = grp_tf +'${oci_identity_group.' + policy_statement_grp + '.name}'
                if(k!=1):
                    grp_tf=grp_tf+","+'${oci_identity_group.' + policy_statement_grp + '.name}'

            actual_policy_statement=policy_statement.replace('$', grp_tf)
            if('*' in policy_statement):
                policy_statement_comp = df.iat[i, 5]
                comp_tf = '${oci_identity_compartment.' + policy_statement_comp + '.name}'
                actual_policy_statement=actual_policy_statement.replace('*', comp_tf)
            if(count!=1):
                tempStr = tempStr + """ ]
        }"""
            tempStr=tempStr + """
    resource "oci_identity_policy" \"""" + policy_name + """" {
            compartment_id = \"""" + policy_compartment + """" 
            description = \"""" + policy_desc + """"
            name = \"""" + policy_name + """"
            statements = [ \"""" + actual_policy_statement + """" """

        if(str(policy_name).lower() == NaNstr.lower()):
            policy_statement = df.iat[i, 3]
            if(str(policy_statement).lower() != NaNstr.lower()):
                policy_statement_grps = df.iat[i, 4]
                policy_statement_grps= policy_statement_grps.split(",")
                grp_tf = ""
                j = 0
                for policy_statement_grp in policy_statement_grps:
                    j = j + 1
                    if (j == 1):
                        grp_tf = grp_tf + '${oci_identity_group.' + policy_statement_grp + '.name}'
                    if (j != 1):
                        grp_tf = grp_tf + "," + '${oci_identity_group.' + policy_statement_grp + '.name}'

                actual_policy_statement = policy_statement.replace('$', grp_tf)

                if ('*' in policy_statement):
                    policy_statement_comp = df.iat[i, 5]
                    comp_tf = '${oci_identity_compartment.' + policy_statement_comp + '.name}'
                    actual_policy_statement = actual_policy_statement.replace('*', comp_tf)

                tempStr = tempStr + """, 
                    \"""" + actual_policy_statement + """" """

    tempStr = tempStr + """ ]
        }
    """


#If input is a csv file


oname.write(tempStr)
oname.close()