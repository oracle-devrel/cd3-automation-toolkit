#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Policies
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######

# If input is cd3 file
def main():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Create Compartments terraform file")
    parser.add_argument("inputfile", help="Full Path of input file. It could be CD3 excel file")
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    # Declare variables
    filename = args.inputfile
    outdir = args.outdir
    prefix = args.prefix
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    outfile = {}
    oname = {}
    tempStr = ''
    tempStr1 = {}

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('policy-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Policies")

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    count = 0
    regions = df['Region']
    regions.dropna()

    check_diff_region = []
    # Get a list of unique region names
    for j in regions.index:
        if (regions[j] not in check_diff_region and regions[j] not in commonTools.endNames and str(
                regions[j]).lower() != "nan"):
            check_diff_region.append(regions[j])

    # If some invalid region is specified in a row which is not part of VCN Info Tab
    for j in check_diff_region:
        if str(j).strip().lower() not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

    # Regions listed in Policies tab should be same for all rows as policies can only be created in home region
    if (len(check_diff_region) > 1):
        print("\nPolicies can be created only in Home Region; You have specified different regions for different policies...Exiting...")
        exit(1)

    # Iterate over rows
    for i in df.index:

        region = str(df.loc[i, "Region"]).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        # Temporary dictionary1
        tempdict = {}

        # Loop through the columns; used to fetch newdly added columns and values
        for columnname in dfcolumns:

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df.loc[i, columnname]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = columnvalue.strip()
                if compartmentVarName.lower() == 'root':
                    columnvalue = 'tenancy_ocid'
                else:
                    compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                    columnvalue = str(compartmentVarName)
                tempdict = {'compartment_tf_name': columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr1[columnname] = str(columnvalue).strip()
            tempStr1.update(tempdict)

        # Fetch column values for each row for creating policies.
        policy_name = str(df.loc[i, "Name"])

        if (str(policy_name).lower() != "nan"):
            count = count + 1
            policy_compartment_name = df.loc[i, "Compartment Name"]
            if (str(policy_compartment_name).lower() == "nan" or policy_compartment_name.lower() == 'root'):
                policy_comp = ""
                policy_compartment = 'tenancy_ocid'
            else:
                policy_comp = policy_compartment_name
                policy_compartment_name = commonTools.check_tf_variable(policy_compartment_name)
                policy_compartment = policy_compartment_name

            policy_desc = str(df.loc[i, "Description"])
            if (str(policy_desc).lower() == "nan"):
                policy_desc = policy_name

            policy_statement = str(df.loc[i, "Policy Statements"])
            actual_policy_statement = policy_statement

            # assign groups in policy statements
            if ('$' in policy_statement):
                policy_statement_grps = str(df.loc[i, "Policy Statement Groups"])
                actual_policy_statement = policy_statement.replace('$', policy_statement_grps)

            # assign compartment in policy statements
            if ('compartment *' in policy_statement):
                policy_statement_comp = str(df.loc[i, "Policy Statement Compartment"])
                # comp_tf = '${var.' + policy_statement_comp + '}'
                comp_tf = policy_statement_comp
                actual_policy_statement = actual_policy_statement.replace('compartment *', 'compartment ' + comp_tf)
            if (count != 1):
                # Do not change below line;
                tempStr = tempStr + " ]\n            }\n\n"
            if (policy_comp != ""):
                policy_tf_name = policy_comp + "_" + policy_name
            else:
                policy_tf_name = policy_name
            policy_tf_name = commonTools.check_tf_variable(policy_tf_name)

            actual_policy_statement = "\"" + actual_policy_statement + "\""

            tempStr1['policy_tf_name'] = policy_tf_name
            tempStr1['compartment_name'] = policy_compartment
            tempStr1['description'] = policy_desc
            tempStr1['name'] = policy_name.strip()
            tempStr1['policy_statements'] = actual_policy_statement

            tempStr = tempStr + template.render(tempStr1)

        if (str(policy_name).lower() == "nan"):
            policy_statement = df.loc[i, "Policy Statements"]

            if (str(policy_statement).lower() != "nan"):
                actual_policy_statement = policy_statement
                if ('$' in policy_statement):
                    policy_statement_grps = df.loc[i, "Policy Statement Groups"]
                    """policy_statement_grps= policy_statement_grps.split(",")
                    grp_tf = ""
                    j = 0
                    for policy_statement_grp in policy_statement_grps:
                        j = j + 1
                        if (j == 1):
                            grp_tf = grp_tf + 'oci_identity_group.' + policy_statement_grp + '.name'
                        if (j != 1):
                            grp_tf = grp_tf + "," + 'oci_identity_group.' + policy_statement_grp + '.name'

                    actual_policy_statement = policy_statement.replace('$', grp_tf)
                    """

                    actual_policy_statement = policy_statement.replace('$', policy_statement_grps)
                if ('compartment *' in policy_statement):
                    policy_statement_comp = str(df.loc[i, "Policy Statement Compartment"])
                    # comp_tf = '${oci_identity_compartment.' + policy_statement_comp + '.name}'
                    # comp_tf = '${var.' + policy_statement_comp + '}'
                    comp_tf = policy_statement_comp
                    actual_policy_statement = actual_policy_statement.replace('compartment *', 'compartment ' + comp_tf)

                tempStr = tempStr + """,\"""" + actual_policy_statement.strip() + "\" """

    tempStr = tempStr + """ ]
                } \n """

    # re-places the placeolder -Addstmt]} of Render template
    tempStr = tempStr.replace('-#Addstmt]}', '')

    # Write TF string to the file in respective region directory
    if (len(check_diff_region) != 0):
        reg = check_diff_region[0].strip().lower()
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        srcdir = reg_out_dir + "/"
        resource = 'Policies'
        commonTools.backup_file(srcdir, resource, "-policies.tf")

        outfile[reg] = reg_out_dir + "/" + prefix + '-policies.tf'

        #If the excel sheet has <end> in first row; exit; no rows to process
        if str(regions[0]) in commonTools.endNames:
            exit(1)
        oname[reg] = open(outfile[reg], 'w')
        oname[reg].write(tempStr)
        oname[reg].close()
        print(outfile[reg] + " containing TF for policies has been created for region " + reg)

if __name__ == '__main__':

    # Execution of the code begins here
    main()