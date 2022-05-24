#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Block Volumes
#
# Author: Murali N V
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
def parse_args():
    # Read the arguments
    parser = argparse.ArgumentParser(description="Creates TF files for Block Volumes")
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()



# If input is CD3 excel file
def create_terraform_block_volumes(inputfile, outdir, prefix,config=DEFAULT_LOCATION):
    filename = inputfile
    configFileName = config
    tfStr = {}

    sheetName="BlockVolumes"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'
    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('block-volume-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        tfStr[eachregion] = ''

    for i in df.index:

        region = str(df.loc[i,"Region"])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        #temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields - to create volumes
        if str(df.loc[i,'Region']).lower() == 'nan' or str(df.loc[i, 'Block Name']).lower() == 'nan' or str(df.loc[i,'Compartment Name']).lower()  == 'nan' or str(df.loc[i,'Availability Domain(AD1|AD2|AD3)']).lower()  == 'nan':
            print( " The values for Region, Block Name, Compartment Name and Availability Domain cannot be left empty. Please enter a value and try again !!")
            exit(1)

        # Check if values are entered for mandatory fields - to attach volumes to instances
        if str(df.loc[i,'Attached To Instance']).lower()  != 'nan' and str(df.loc[i,'Attach Type(iscsi|paravirtualized)']).lower()  == 'nan' :
            print("Attach Type cannot be left empty if you want to attach  the volume to instance "+df.loc[i,'Attached To Instance']+". Please enter a value and try again !!")
            exit(1)
        elif str(df.loc[i,'Attach Type(iscsi|paravirtualized)']).lower()  != 'nan' and str(df.loc[i,'Attached To Instance']).lower()  == 'nan' :
            print("Attached To Instance cannot be left empty if Attachment Type is "+df.loc[i,'Attach Type(iscsi|paravirtualized)']+". Please enter a value and try again !!")
            exit(1)

        blockname_tf = commonTools.check_tf_variable(df.loc[i, 'Block Name'])
        tempStr['block_tf_name'] = blockname_tf

        # Fetch data; loop through columns
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            #Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {'compartment_tf_name': columnvalue}

            if columnname == 'Custom Policy Compartment Name':
                if columnvalue != "":
                    custom_policy_compartment_name = columnvalue.strip()
                    custom_policy_compartment_name = commonTools.check_tf_variable(custom_policy_compartment_name)
                    tempdict = {'custom_policy_compartment_name': custom_policy_compartment_name}


            # Process Freeform Tags and Defined Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Availability Domain(AD1|AD2|AD3)":
                columnname = "availability_domain"
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)

            if columnname == "Attached To Instance":
                if str(columnvalue).strip() != '':
                    columnvalue = commonTools.check_tf_variable(columnvalue)

            if (columnname == 'Backup Policy'):
                columnname = 'backup_policy'
                columnvalue = str(columnvalue).strip()

            if columnname == "Attach Type(iscsi|paravirtualized)":
                columnname = "attach_type"

            if columnname == "Size In GBs":
                if columnvalue != '':
                    columnvalue = int(float(columnvalue))

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:

        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if tfStr[reg] != '':
            # Generate Final String
            src = "## Add block volumes for "+reg.lower()+" here ##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src,tfStr[reg])
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            resource=sheetName.lower()
            commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

            # Write to TF file
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            outfile = reg_out_dir+ "/" + auto_tfvars_filename
            oname = open(outfile, "w+")
            print(outfile + " for Block Volume and its Backup Policy has been created for region " + reg)
            oname.write(tfStr[reg])
            oname.close()


if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_block_volumes(args.file, args.outdir, args.prefix, args.config)
