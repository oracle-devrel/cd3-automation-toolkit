#!/usr/bin/python3
# Copyright (c) 2016, 2025, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Exa PDB
# Database EXA PDB
#
# Author: Suruchi
# Oracle Consulting


import os, sys
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd() + "../")
from common.python.commonTools import *
import ocicloud.python.ociCommonTools as ociCommonTools


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_exa_pdb(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile
    sheetName = "EXA-PDBs"
    base_name = sheetName.lower()
    auto_tfvars_filename = f"_{base_name}.auto.tfvars"

    outfile = {}
    oname = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('exa-pdb-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    #Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    regions_done_count = []

    # Iterate over rows
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break

        if region.lower() == 'nan':
            continue

        region=region.strip().lower()

        # If some invalid region is specified in a row which is not part of VCN Info Tab
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        mandatory_base_fields = [
            'Region',
            'Compartment Name',
            'Exadata Infra Display Name',
            'VM Cluster Display Name',
            'DB Home Name'
        ]

        mandatory_cdb_fields = [
            'CDB Name',
            'PDB Name'
        ]

        skip_row = False

        for field in mandatory_base_fields + mandatory_cdb_fields:
            if field not in dfcolumns or str(df.loc[i, field]).strip().lower() in ['nan', '']:
                print(
                    f"\nWARNING!!! Skipping row {i + 3} in sheet '{sheetName}' "
                    f"because mandatory field '{field}' is missing or empty."
                )
                skip_row = True
                break

        if skip_row:
            continue

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {columnname: columnvalue}
                exa_infra_comp = columnvalue

            # Process Defined and Freeform Tags
            if columnname.lower() in ociCommonTools.tagColumns:
                tempdict = ociCommonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Exadata Infra Display Name":
                exa_infa_raw = columnvalue.strip()

                if "@" in exa_infa_raw:
                    comp_for_infra, exa_infra_name = exa_infa_raw.split("@", 1)
                    compartmentVarName = str(commonTools.check_tf_variable(comp_for_infra))
                    tempdict = {
                        "exadata_infra_display_name": exa_infra_name,
                        "exadata_infra_comp_id": compartmentVarName,
                    }

                else:

                    tempdict = {
                        "exadata_infra_display_name": exa_infa_raw,
                        "exadata_infra_comp_id": exa_infra_comp,
                    }

            if columnname == "VM Cluster Display Name":
                display_tf_name = columnvalue.strip()
                tempdict = {'vm_cluster_display_tf_name': display_tf_name}


            if columnname == "DB Home Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'db_home_display_tf_name': display_tf_name}

            if columnname == "DB Home Name":
                db_home_display_name = columnvalue.strip()
                tempdict = {"db_home_display_name": db_home_display_name}


            if columnname == "CDB Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'cdb_name_tf_name': display_tf_name}

            if columnname == "PDB Name":
                display_tf_name = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(display_tf_name)
                tempdict = {'pdb_name_tf_name': display_tf_name}

            if columnname == "PDB Admin Password":
                display_tf_name = columnvalue.strip()
                if display_tf_name.startswith("ocid1.vaultsecret."):
                    tempdict = { 'pdb_admin_password' : None,
                                 'pdb_admin_password_secret_id' : display_tf_name }
                else:
                    tempdict = { 'pdb_admin_password' : display_tf_name,
                                 'pdb_admin_password_secret_id' : None }

            if columnname == "TDE Wallet Password":
                display_tf_name = columnvalue.strip()
                if display_tf_name.startswith("ocid1.vaultsecret."):
                    tempdict = {
                        'tde_wallet_password': None,
                        'tde_wallet_secret_id': display_tf_name
                    }
                else:
                    tempdict = {
                        'tde_wallet_password': display_tf_name,
                        'tde_wallet_secret_id': None
                    }

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        """
        if (region not in regions_done_count):
            tempdict = {"count": 0}
            regions_done_count.append(region)
        else:
            tempdict = {"count": i}
        tempStr.update(tempdict)
        """
        #marker addition
        if region not in regions_done_count:
            regions_done_count.append(region)

        tempStr.update({"count": 1})


        # Write all info to TF string
        #tfStr[region]=tfStr[region][:-1] + template.render(tempStr)
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" + prefix + auto_tfvars_filename


        if (tfStr[reg] != ''):
            header = template.render(count=0, region=reg)
            marker = f"##Add New PDBs for {reg.lower()} here##"
            tfStr[reg] = header.replace(marker, tfStr[reg].rstrip() + "\n    " + marker)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()

            print(outfile[reg] + " for EXA PDBs has been created for region " + reg)
