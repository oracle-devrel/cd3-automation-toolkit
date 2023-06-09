#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# SDDC


from oci.config import DEFAULT_LOCATION
from pathlib import Path
import argparse
import os
from commonTools import *
from jinja2 import Environment, FileSystemLoader


def parse_args():
    parser = argparse.ArgumentParser(description='Creates sddc TF file')
    parser.add_argument('inputfile', help='Full Path of input CD3 excel file')
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument("service_dir",
                        help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument('--config', default=DEFAULT_LOCATION, help='Config file name')
    return parser.parse_args()


# If input is CD3 excel file
def create_terraform_sddc(inputfile, outdir, service_dir, prefix, config):
    tfStr = {}
    filename = inputfile
    configFileName = config
    ct = commonTools()
    ct.get_subscribedregions(configFileName)


    ADS = ["AD1", "AD2", "AD3"]

    sheetName = "SDDCs"
    sheetNamenetwork = "SDDCs-Network"

    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('sddc-template')

    # Read cd3 using pandas dataframe
    # for item in sheetName:
    # adding 2 sheetname

    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    df_1, col_headers1 = commonTools.read_cd3(filename, sheetNamenetwork)
    df_1 = df_1.dropna(how='all')
    df_1 = df_1.reset_index(drop=True)

    #Ignore rows after End tag
    row = df_1[df_1['Region'].isin(commonTools.endNames)].index.tolist()
    if row!=[]:
        df_1=df_1.iloc[:row[0]]

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        tfStr[eachregion] = ''

    subnets = parseSubnets(filename)

    #Process SDDC Sheet
    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()

        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        sddc_name = str(df.loc[i, 'SDDC Name']).strip()

        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields

        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'SDDC Name']).lower() == 'nan' or str(
            df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
            df.loc[i, 'VMWare  Software Version']).lower() == 'nan' or str(
            df.loc[i, 'Availability Domain(AD1|AD2|AD3|multi-AD)']).lower() == 'nan'):
            print("\nOne/All of the Column/Columns from Region, Compartment Name, Availability Domain, SDDC Name, VMWare Software Version is empty in SDDC sheet of CD3..exiting...Please check.")
            exit(1)

        # Get corresponding data from SDDCs-Network tab
        df1 = df_1.loc[(df_1['Region'] == df.loc[i, 'Region']) & (df_1['SDDC Name'] == df.loc[i, 'SDDC Name'])]

        if (len(df1.index) !=1):
            print("SDDC " + sddc_name +" for region "+region +" does not have a single row in "+sheetNamenetwork + " sheet. Exiting!!!")
            exit()

        # List of column headers
        dfcolumns1 = df1.columns.values.tolist()


        for columnname in dfcolumns:
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'SDDC Name':
                sddc_name = columnvalue.strip()
                tempdict = {'display_tf_name': commonTools.check_tf_variable(sddc_name),'display_name':sddc_name}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Availability Domain(AD1|AD2|AD3|multi-AD)':
                columnname = 'availability_domain'

                if (columnvalue.strip()!= 'multi-AD'):
                    AD = columnvalue.upper()
                    ad = ADS.index(AD)
                    adString = ad
                else:
                    adString = "multi-AD"
                tempdict = {columnname: adString}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Iterate over Network sheet columns
        for columnname in dfcolumns1:
            columnvalue = str(df1[columnname][i]).strip()
            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)
            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname == 'Provisioning Subnet':
                subnet_tf_name = columnvalue.strip()
                if ("ocid1.subnet.oc1" in subnet_tf_name):
                    network_compartment_id = ""
                    vcn_name = ""
                    subnet_id = subnet_tf_name
                else:
                    try:
                        key = region, subnet_tf_name
                        network_compartment_id = subnets.vcn_subnet_map[key][0]
                        vcn_name = subnets.vcn_subnet_map[key][1]
                        subnet_id = subnets.vcn_subnet_map[key][2]
                    except Exception as e:
                        print("Invalid Subnet Name specified for row " + str(i + 3) + ". It Doesnt exist in SubnetsVLANs sheet. Exiting!!!")
                        exit()

                tempdict = {'network_compartment_id': commonTools.check_tf_variable(network_compartment_id),
                            'vcn_name': vcn_name,'provisioning_subnet': subnet_id}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:

        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

        if tfStr[reg] != '':
            # Generate Instances String
            src = "##Add New SDDCs for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)

            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            # Write to TF file
            outfile = reg_out_dir + "/" + auto_tfvars_filename
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print(outfile + " for OCVS cluster has been created for region " + reg)
            oname.write(tfStr[reg])
            oname.close()

if __name__ == '__main__':
    args = parse_args()
    # Execution of the code begins here
    create_terraform_sddc(args.inputfile, args.outdir, args.service_dir, args.prefix, args.config)










