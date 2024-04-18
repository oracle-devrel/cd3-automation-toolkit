#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Compartments
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF if (columnvalue not in ckeys):Upgrade): Shruthi Subramanian
#

import os
from oci.config import DEFAULT_LOCATION
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from commonTools import *
import oci

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_compartments(inputfile, outdir, service_dir, prefix, ct):
    # Declare variables
    filename = inputfile

    sheetName = 'Compartments'
    auto_tfvars_filename = '_'+sheetName.lower()+'.auto.tfvars'
    outfile = {}
    oname = {}
    c = 0

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('compartments-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    home_region = ct.home_region

    srcdir = outdir + "/" + home_region + "/" + service_dir + "/"
    var_file = f'{srcdir}/variables_{home_region}.tf'
    ct.get_compartment_map(var_file, 'Compartments')
    resource = sheetName.lower()
    commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    # Initialise empty TF string for each region
    tfStr = ''
    root_compartments = ''
    sub_compartments_level1 = ''
    sub_compartments_level2 = ''
    sub_compartments_level3 = ''
    sub_compartments_level4 = ''
    sub_compartments_level5 = ''

    # Separating Compartments and ParentComparements into list
    ckeys = []
    pvalues = []

    # reversal path function
    def travel(parent, keys, values, c):
        if (parent == "" or parent == "nan" or parent == "root"):
            return ""
        else:
            if ("::" in str(values[keys.index(parent)])):
                if (c == 0):
                    return values[keys.index(parent)] + "::" + parent
                c = c + 1
                return values[keys.index(parent)]
            return travel(values[keys.index(parent)], keys, values, c) + "::" + parent

    for i in df.index:
        if (str(df.loc[i, 'Region']) in commonTools.endNames):
            break
        ckeys.append(str(df.loc[i, 'Name']).strip())
        pvalues.append(str(df.loc[i, 'Parent Compartment']).strip())

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region'])

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        region = region.strip().lower()

        # If some invalid region is specified in a row
        if region != ct.home_region:
            print("\nERROR!!! Invalid Region; It should be Home Region of the tenancy..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan':
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit(1)

        var_c_name = ""
        nf=0
        for columnname in dfcolumns:

            # Column value
            if 'description' in columnname.lower():
                columnvalue = str(df[columnname][i])
                tempdict = {'description': columnvalue}
            else:
                columnvalue = str(df[columnname][i]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            if "::" in columnvalue:
                if columnname != "Parent Compartment":
                    # Check for multivalued columns
                    tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Parent Compartment":
                columnname = commonTools.check_column_headers(columnname)
                if (columnvalue.lower() == 'nan' or columnvalue.lower() == 'root' or columnvalue.lower() == ""):
                    parent_compartment = 'var.tenancy_ocid'
                    var_c_name = str(df.loc[i, 'Name']).strip()
                    tempdict = {'parent_compartment': parent_compartment}
                    tempStr.update(tempdict)

                else:
                    if (ckeys.count(str(columnvalue)) > 1):
                        r = 0
                        for check in range(len(ckeys)):
                            if (ckeys[check] == str(columnvalue)):
                                if (pvalues[check].lower() == "root" or pvalues[check].lower() == "nan"):
                                    r = 1
                        if (r == 1):
                            var_c_name = columnvalue + "::" + str(df.loc[i, 'Name']).strip()
                            parent_compartment = commonTools.check_tf_variable(columnvalue)
                            tempdict = {'parent_compartment': parent_compartment}
                            tempStr.update(tempdict)
                        else:
                            print("Error!! Could not find Path for " + str(
                                df.loc[i, 'Name']).strip() + " Please give Full Path")
                            exit(1)

                    elif (columnvalue not in ckeys):
                            if columnvalue in ct.ntk_compartment_ids.keys():
                                #parent_compartment = 'var.'+commonTools.check_tf_variable(columnvalue)
                                parent_compartment = commonTools.check_tf_variable(columnvalue)
                                var_c_name=columnvalue + "::" +commonTools.check_tf_variable(str(df.loc[i, 'Name']).strip())
                                tempdict = {'parent_compartment': parent_compartment}
                                tempStr.update(tempdict)
                            elif ("::" in columnvalue):
                                var_c_name = columnvalue + "::" + str(df.loc[i, 'Name']).strip()
                                parent_compartment = commonTools.check_tf_variable(columnvalue)
                                tempdict = {'parent_compartment': parent_compartment}
                                tempStr.update(tempdict)
                            else:
                                print("Error!! There is no parent compartment with name " + columnvalue + " either in OCI or in input CD3..Skipping this row")
                                nf=1
                                break

                    else:
                        parent_compartment = travel(str(columnvalue).strip(), ckeys, pvalues, c)
                        var_c_name = parent_compartment + "::" + str(df.loc[i, 'Name']).strip()
                        tempdict = {'parent_compartment': parent_compartment}
                        tempStr.update(tempdict)

                        if (len(parent_compartment) > 1 and parent_compartment[0] == ":" and parent_compartment[
                            1] == ":"):
                            parent_compartment = parent_compartment[2:]
                            var_c_name = parent_compartment + "::" + str(df.loc[i, 'Name']).strip()
                        parent_compartment = commonTools.check_tf_variable(parent_compartment)
                        tempdict = {'parent_compartment': parent_compartment}
                        tempStr.update(tempdict)

            var_c_name = commonTools.check_tf_variable(var_c_name)
            tempStr['comp_tf_name'] = var_c_name

            if columnname == 'Name':
                if (str(columnvalue).lower() != "nan"):
                    region = region.strip().lower()
                    columnvalue = str(columnvalue).strip()

            # If description field is empty; put name as description
            if columnname == 'Description':
                if columnvalue == "" or columnvalue == 'nan':
                    columnvalue = df.loc[i, 'Name']
                    tempdict = {'description': columnvalue}


            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        if nf==0:
            if tempStr['parent_compartment'] == "var.tenancy_ocid" or tempStr['parent_compartment'] == "root":
                tempStr.update({'compartment_details' : True})
                root_compartments = str(root_compartments) + template.render(tempStr)
            elif len(tempStr['parent_compartment'].split("--")) == 1:
                tempStr.update({'compartment_details' : True})
                sub_compartments_level1 = str(sub_compartments_level1) + template.render(tempStr)
            elif len(tempStr['parent_compartment'].split("--")) == 2:
                tempStr.update({'compartment_details' : True})
                sub_compartments_level2 = str(sub_compartments_level2) + template.render(tempStr)
            elif len(tempStr['parent_compartment'].split("--")) == 3:
                tempStr.update({'compartment_details' : True})
                sub_compartments_level3 = str(sub_compartments_level3) + template.render(tempStr)
            elif len(tempStr['parent_compartment'].split("--")) == 4:
                tempStr.update({'compartment_details' : True})
                sub_compartments_level4 = str(sub_compartments_level4) + template.render(tempStr)
            elif len(tempStr['parent_compartment'].split("--")) == 5:
                tempStr.update({'compartment_details' : True})
                sub_compartments_level5 = str(sub_compartments_level5) + template.render(tempStr)

    tfStr = tfStr + template.render(count=0,root=root_compartments,compartment_level1=sub_compartments_level1,compartment_level2=sub_compartments_level2,compartment_level3=sub_compartments_level3,compartment_level4=sub_compartments_level4,compartment_level5=sub_compartments_level5)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + ct.home_region + "/" + service_dir
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    reg = ct.home_region
    outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename

    if (tfStr != ''):
        tfStr = "".join([s for s in tfStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname[reg] = open(outfile[reg], 'w')
        oname[reg].write(tfStr)
        oname[reg].close()
        print(outfile[reg] + " for Compartments has been created for region " + reg)

        fetch_comp_file = f'{outdir}/.safe/fetchcompinfo.safe'
        with open(fetch_comp_file, 'w') as f:
            f.write('run_fetch_script=1')
        f.close()
