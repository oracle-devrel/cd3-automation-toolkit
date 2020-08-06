#!/usr/bin/python3
# Author: Suruchi
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader

sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs- Either properties file: vcn-info.properties or CD3 excel file AND Outfile
# if properties file is the input then Code will read input compartment file name from Default Section
# Compartments are defined in csv format
# outfile is the name of output terraform file generated
######

## Start Processing

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
tfStr = {}
c = 0

# Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('compartments-template')

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


# If input in cd3 file
if ('.xls' in args.inputfile):

    # Read cd3 using pandas dataframe
    df = pd.read_excel(args.inputfile, sheet_name='Compartments', skiprows=1, dtype=object)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # To handle duplicates during export process
    # df=df.drop_duplicates(ignore_index=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''

    # Separating Compartments and ParentComparements into list
    ckeys = []
    pvalues = []

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

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Name']).lower() == 'nan':
            print("\nThe values for Region and Name cannot be left empty. Please enter a value and try again !!")
            exit()

        var_c_name = ""
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            if "::" in columnvalue:
                if columnname != "Parent Compartment":
                    # Check for multivalued columns
                    tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname in commonTools.tagColumns:
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
                            parent_compartment = 'oci_identity_compartment.' + parent_compartment + '.id'
                            tempdict = {'parent_compartment': parent_compartment}
                            tempStr.update(tempdict)
                        else:
                            print("Error!! Could not find Path for " + str(
                                df.loc[i, 'Name']).strip() + " Please give Full Path")
                            exit(1)

                    elif ("::" in columnvalue):
                        var_c_name = columnvalue + "::" + str(df.loc[i, 'Name']).strip()
                        parent_compartment = commonTools.check_tf_variable(columnvalue)
                        parent_compartment = 'oci_identity_compartment.' + parent_compartment + '.id'
                        tempdict = {'parent_compartment': parent_compartment}
                        tempStr.update(tempdict)
                    else:
                        if (columnvalue not in ckeys):
                            print(
                                "Error!! There is no parent compartment with name " + columnvalue + " to create " + str(
                                    df.loc[i, 'Name']).strip() + " compartment")
                            exit(1)
                        parent_compartment = travel(str(columnvalue).strip(), ckeys, pvalues, c)
                        var_c_name = parent_compartment + "::" + str(df.loc[i, 'Name']).strip()
                        tempdict = {'parent_compartment': parent_compartment}
                        tempStr.update(tempdict)

                        if (len(parent_compartment) > 1 and parent_compartment[0] == ":" and parent_compartment[
                            1] == ":"):
                            parent_compartment = parent_compartment[2:]
                            var_c_name = parent_compartment + "::" + str(df.loc[i, 'Name']).strip()
                        parent_compartment = commonTools.check_tf_variable(parent_compartment)
                        parent_compartment = 'oci_identity_compartment.' + parent_compartment + '.id'
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

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        tfStr[reg] = tfStr[reg] + template.render(tempStr)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx")
    exit()

# Write TF string to the file in respective region directory
for reg in ct.all_regions:
    reg_out_dir = outdir + "/" + reg
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)
    outfile[reg] = reg_out_dir + "/" + prefix + '-compartments.tf'

    if (tfStr[reg] != ''):
        oname[reg] = open(outfile[reg], 'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for compartments has been created for region " + reg)
