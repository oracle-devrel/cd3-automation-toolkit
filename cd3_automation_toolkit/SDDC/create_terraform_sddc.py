#!/usr/bin/python3
# Copyright (c) 2016, 2019,2024 Oracle and/or its affiliates. All rights reserved.
# This script will produce a Terraform file that will be used to set up OCI core components
# SDDC management cluster and workload clusters
from pathlib import Path
import os
from commonTools import *
from jinja2 import Environment, FileSystemLoader

# Function to pre-process the data
def data_process(filename, sheetName):
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all').reset_index(drop=True)
    if df['Region'].isin(commonTools.endNames).any():
        end_index = df[df['Region'].isin(commonTools.endNames)].index[0]
        df = df.iloc[:end_index]
    return df

# Function to set up Jinja2 environment
def setup_jinja2_env(template_name):
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    return env.get_template(template_name)

# Main Function to create clusters
def create_terraform_sddc(inputfile, outdir, service_dir, prefix, ct):
    df = data_process(inputfile, "SDDCs")
    df_vshere_type = df['vsphere type'].str.strip().str.lower().values
    for sddc_type in ["management", "workload"]:
        if sddc_type in df_vshere_type:
            create_terraform_sddc_cluster(inputfile, outdir, service_dir, prefix, ct, sddc_type)

########function for creating SDDC cluster #########
def create_terraform_sddc_cluster(inputfile, outdir, service_dir, prefix, ct, sddc_type):
    tfStr = {}
    filename = inputfile
    sheetName = "SDDCs"
    sheetNamenetwork = "SDDCs-Network"
    ADS = ["AD1", "AD2", "AD3"]
    auto_tfvars_filename = prefix + '_' + sheetName.lower()+('_cluster' if sddc_type == 'workload' else '') + '.auto.tfvars'
    df = data_process(inputfile, "SDDCs")
    df = df[df['vsphere type'].str.strip().str.lower() == sddc_type]
    df_1 = data_process(inputfile, "SDDCs-Network")
    template = setup_jinja2_env('sddc-cluster-template' if sddc_type == 'workload' else 'sddc-template')
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
        sddc_hw_type = str(df.loc[i, 'SDDC Hardware Type'])
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        sddc_name = str(df.loc[i, 'SDDC Name']).strip()
        sddc_compartment = str(df.loc[i, 'Compartment Name']).strip()
        sddc_compartment = commonTools.check_tf_variable(sddc_compartment)
        tempStr = {}
        tempdict = {}
        mgmt_volumes = []
        workload_volumes = []
        # Check if values are entered for mandatory fields
        if any(str(df.loc[i, col]).lower() == 'nan' for col in ['Region', 'SDDC Name', 'Compartment Name', 'VMWare  Software Version', 'Availability Domain(AD1|AD2|AD3|multi-AD)']):
            print("\nOne/All of the Column/Columns from Region, Compartment Name, Availability Domain, SDDC Name, VMWare Software Version is empty in SDDC sheet of CD3..exiting...Please check.")
            exit(1)
        # Get corresponding data from SDDCs-Network tab
        df1 = df_1.loc[(df_1['Region'] == df.loc[i, 'Region']) & (df_1['SDDC Name'] == df.loc[i, 'SDDC Name'])]
        if (len(df1.index) !=1):
            print("SDDC " + sddc_name +" for region "+region +" does not have a single row in "+sheetNamenetwork + " sheet. Exiting!!!")
            exit(1)
        # List of column headers
        dfcolumns1 = df1.columns.values.tolist()
        for columnname in dfcolumns:
            columnvalue = commonTools.check_columnvalue(str(df[columnname][i]).strip())
            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
            if columnname == 'SDDC Name':
                sddc_name = columnvalue.strip()
                sddc_display_name,sddc_cluster_display_name = sddc_name.split("::")
                tempdict = {'display_tf_name': commonTools.check_tf_variable(sddc_name),'display_name':sddc_name,'sddc_display_name': sddc_display_name,'sddc_cluster_display_name':sddc_cluster_display_name}
            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}
            if columnname == 'Availability Domain(AD1|AD2|AD3|multi-AD)':
                columnname = 'availability_domain'
                adString = columnvalue.upper() if columnvalue.strip()!= 'multi-AD' else 'multi-AD'
                tempdict = {columnname: ADS.index(adString) if adString != 'multi-AD' else 'multi-AD'}
            if sddc_type == "management":
                if columnname == 'Management Block Volumes':
                    if columnvalue != "":
                        columnvalue = columnvalue.split(',')
                        for item in columnvalue:
                            if '@' in item:
                                items = item.strip().split("@")
                                item = commonTools.check_tf_variable(items[0].strip()) + "@" + items[1].strip()
                                mgmt_volumes.append(item)
                            else:
                                mgmt_volumes.append(sddc_compartment+'@'+item)
                    tempdict = {'mgmt_data': mgmt_volumes}
            if columnname == 'Workload Block Volumes':
                if columnvalue != "":
                    columnvalue = columnvalue.split(',')
                    for item in columnvalue:
                        if '@' in item:
                            items = item.strip().split("@")
                            item = commonTools.check_tf_variable(items[0].strip()) + "@" + items[1].strip()
                            workload_volumes.append(item)
                        else:
                            workload_volumes.append(sddc_compartment + '@' + item)
                    tempdict = {'workload_data': workload_volumes}
            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        # Iterate over Network sheet columns
        for columnname in dfcolumns1:
            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(str(df1[columnname][i]).strip())
            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            subnet_id = ''
            network_compartment_id = ''
            vcn_name = ''
            if columnname == 'Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id = "root"
                    vcn_name = ""
                    subnet_id = columnvalue
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'provisioning_subnet': subnet_id}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        os.makedirs(reg_out_dir, exist_ok=True)
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
            with open(outfile, "w+") as oname:
                print(outfile + " for OCVS cluster has been created for region " + reg)
                oname.write(tfStr[reg])
                oname.close()
