#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# DNS-Zones
#
import os
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_dns_zones(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile
    sheetName = "DNS-Views-Zones-Records"
    auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"

    outfile = {}
    oname = {}
    tfStr = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('dns-zones-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''

    # Iterate over rows
    prevregion = ""

    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if (region != prevregion):
            zone_done = []
        prevregion = region
        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'View Name']).lower() == 'nan':
            print(
                "\nRegion, Compartment Name, View Name fields are mandatory. Please enter a value and try again !!")
            print("\n** Exiting **")
            exit(1)

        # set key for template items
        view_name = str(df["View Name"][i]).strip()
        zone_name = str(df["Zone"][i]).strip()
        zone_tf_name = view_name + "_" + zone_name.replace(".", "_")
        tempStr['zone_tf_name'] = zone_tf_name

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            """if columnname == "Zone Compartment":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {'zone_compartment_name': columnvalue}"""

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Zone':
                tempdict = {'display_name': zone_name}

            if columnname == 'View Name':
                tempdict = {'view_id': view_name}

            if columnname == 'Compartment Name':
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {'view_compartment_name': columnvalue}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write zone info to TF string if not written previously
        if zone_tf_name not in zone_done:
            zone_done.append(zone_tf_name)
            tfStr[region] = tfStr[region] + template.render(tempStr)


    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + auto_tfvars_filename

        if (tfStr[reg] != ''):
            src = "##Add New DNS Zones for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            tfStr[reg] = "\n\n"+tfStr[reg]
            oname[reg] = open(outfile[reg], 'a')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for DNS Zones has been updated for region " + reg+ " with zones data")

