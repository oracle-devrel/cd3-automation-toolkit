#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Security components
# Key/Vault
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import math
from oci.config import DEFAULT_LOCATION
from commonTools import *


######
# Required Inputs- Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_keyvaults(inputfile, outdir, service_dir, prefix, ct):

    tfStr = {}
    vaultStr = {}
    keyStr = {}
    tempStr = {}
    filename = inputfile
    outfile = {}
    oname = {}
    sheetName = "KMS"


    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    vault_template = env.get_template('vaults-template')
    key_template = env.get_template('keys-template')


    # Read cd3 using pandas dataframe

    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers

    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
        vaultStr[eachregion] = ''
        keyStr[eachregion] = ''

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("Invalid Region!! Tenancy is not subscribed to this region. Please try again")
            exit(1)

        # temporary dictionary1 and dictionary2
        
        tempdict = {}


        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(
                df.loc[i, 'Vault Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'Vault Display Name']).lower() == 'nan' or str(df.loc[i, 'Vault type']).lower() == 'nan'):
            print("Error!! Empty column value(s) detected for mandatory fields Region, Vault Display Name, Vault Compartment Name, Vault type in KMS sheet. Enter all mandatory fields and try again. Exiting!! ")
            exit(1)

        # Fetch data; Loop through columns
        flag = 0
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Vault Compartment Name":
                vault_compartment_var_name = columnvalue.strip()
                vault_compartment_var_name = commonTools.check_tf_variable(vault_compartment_var_name)
                tempdict = {'vault_compartment_tf_name': vault_compartment_var_name}

            if columnname == "Vault Display Name":
                columnvalue = columnvalue.strip()
                vault_display_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'vault_display_tf_name': vault_display_tf_name, 'management_endpoint': vault_display_tf_name}


            if columnname == "Vault type":
                columnvalue = columnvalue.strip()
                if columnvalue.lower() in ["default", "virtual_private"]:
                    tempdict = {'vault_type': columnvalue.upper()}
                    if columnvalue.lower() == "virtual_private":
                        flag = 1
                else:
                    print("Invalid Vault_type!!. Vault type should be either 'DEFAULT or 'VIRTUAL_PRIVATE'. Try Again.  Exiting... ")
                    exit(1)

            if columnname == "Replica Region":
                columnvalue = columnvalue.strip().lower()
                if columnvalue != '':
                    if columnvalue != region:
                        if flag == 1:
                            if columnvalue in commonTools.endNames:
                                break
                            if columnvalue not in ct.all_regions:
                                print("Invalid Replica Region!! Tenancy is not subscribed to this region. Please try again")
                                exit(1)
                            tempdict = {'replica_region': ct.region_dict[columnvalue]}
                        else:
                            print("Error!! Replication can only be done for Virtual Private vaults. Remove the entry and try again. Exiting...")
                            exit(1)
                    else:
                        print(" Error!! Replica region can't be same as the primary vault's region. Try with a different region. Exiting...")
                        exit(1)

            if (str(df.loc[i, 'Key Compartment Name']).lower() != 'nan' or str(df.loc[i, 'Key Display Name']).lower() != 'nan' or str(df.loc[i, 'Protection mode']).lower() != 'nan' or  str(df.loc[i, 'Algorithm']).lower() != 'nan' or str(df.loc[i, 'Length in bits']).lower() != 'nan'):
                if (str(df.loc[i, 'Key Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Key Display Name']).lower() == 'nan' or str(df.loc[i, 'Protection mode']).lower() == 'nan' or str(
                        df.loc[i, 'Algorithm']).lower() == 'nan' or str(df.loc[i, 'Length in bits']).lower() == 'nan'):
                    print(
                        " Error!! Key Display Name, Algorithm and Length are mandatory fields to create Keys. Enter these values and try again. Exiting...")
                    exit(1)
                else:
                    if columnname == "Key Compartment Name":
                        if columnvalue != '':
                            columnvalue = columnvalue.strip()
                            key_compartment_var_name = commonTools.check_tf_variable(columnvalue)
                            tempdict = {'key_compartment_tf_name': key_compartment_var_name}

                            if (str(df.loc[i, 'Key Display Name']).lower() == 'nan' or str(
                                    df.loc[i, 'Algorithm']).lower() == 'nan' or str(
                                    df.loc[i, 'Length in bits']).lower() == 'nan'):
                                print(
                                    " Error!! Key Compartment Name, Key Display Name, Algorithm and Length are mandatory fields to create Keys. Enter these values and try again. Exiting...")
                                exit(1)
                            else:
                                pass
                        else:
                            pass

                    if columnname == "Key Display Name":
                        if columnvalue != '':
                            columnvalue = columnvalue.strip()
                            key_display_tf_name = commonTools.check_tf_variable(columnvalue)
                            tempdict = {'key_display_tf_name': key_display_tf_name}

                    if columnname == "Protection mode":
                        columnvalue = columnvalue.strip().lower()
                        if columnvalue != '':
                            if columnvalue in ['hsm', 'software']:
                                tempdict = {'protection_mode': columnvalue.upper()}
                            else:
                                print("Error!! Invalid Protection mode. Value should either be 'hsm' or 'software'. Try Again. Exiting...")
                                exit(1)


                    if columnname == "Algorithm":
                        columnvalue = columnvalue.strip().lower()
                        if columnvalue != '':
                            if columnvalue in ["aes", "rsa", "ecdsa"]:
                                tempdict = {'algorithm': columnvalue.upper()}
                            else:
                                print(
                                    "Error!! Algorithm is not valid. Only 'AES', 'RSA', 'ECDSA' algorithms are supported. Exiting...")
                                exit(1)

                    if columnname == "Length in bits":
                        columnvalue = columnvalue.strip()
                        if columnvalue != '':
                            algorithm = tempdict.get('algorithm')
                            if algorithm.lower() == "aes" and columnvalue in ["128", "192", "256"]:
                                tempdict = {'length': int(int(columnvalue) / 8)}
                            elif algorithm.lower() == "rsa" and columnvalue in ["2048", "3072", "4096"]:
                                tempdict = {'length': int(int(columnvalue) / 8)}
                            elif algorithm.lower() == "ecdsa" and columnvalue in ["256", "384", "521"]:
                                tempdict = {'length': int(math.ceil(int(columnvalue) / 8)), 'curve_id': "NIST_P" + str(columnvalue)}
                            else:
                                print(f"Error!! Invalid length for {algorithm.upper()} algorithm. Exiting...")
                                exit(1)
            else:
                pass


            if columnname == "Auto rotation":
                columnvalue = columnvalue.strip().lower()
                if columnvalue == "true":
                    if flag == 1:
                        tempdict = {'auto_rotation': columnvalue}
                    else:
                        print("Error!! Auto rotation is only possible for Virtual Private Vaults. Exiting...")
                        exit(1)
                elif columnvalue == "false":
                    tempdict = {'auto_rotation': columnvalue}
                else:
                    print("Auto rotation values should be either 'true'/'false'. Try Again. Exiting...")
                    exit(1)



            if columnname == "Rotation interval in days":
                columnvalue = columnvalue.strip()
                if columnvalue != '':
                    if flag == 1 and tempdict.get('auto_rotation') == "true":
                        if 60 <= int(columnvalue) <= 365:
                            tempdict = {'rotation_interval': int(columnvalue)}
                        else:
                            print("Error!! Rotation interval should be between 60 - 365 days. Exiting!!")
                            exit(1)
                    else:
                        print("Error!! Rotation interval can only be setup for keys in Virtual Private Vaults with auto rotation enabled. Exiting...")
                        exit(1)
                else:
                    pass

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

    #Write all info to TF string
        if vault_display_tf_name:
            vaultStr[region] = vaultStr[region] + vault_template.render(tempStr)
            #print(vaultStr[region])

        if str(df.loc[i, 'Key Display Name']).lower() != 'nan':
            keyStr[region] = keyStr[region] + key_template.render(tempStr)
            #print(keyStr[region])
        else:
            keyStr[region] = ''


    # Write TF string to the file in respective region directory

    # for reg in ct.all_regions:

    #     if vaultStr[reg] != '':
    #         # Generate Final String
    #         src = "##Add New Vaults for " + reg + " here##"
    #         vaultStr[reg] = vault_template.render(skeleton=True, count=0, region=reg).replace(src, vaultStr[reg] + "\n" + src)
    #         vaultStr[reg] = "".join([s for s in vaultStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
    #         #print(vaultStr[reg])

    # for reg in ct.all_regions:

    #     if keyStr[reg] != '':
    #         # Generate Final String
    #         src = "##Add New Keys for " + reg + " here##"
    #         keyStr[reg] = key_template.render(skeleton=True, count=0, region=reg).replace(src, keyStr[reg] + "\n" + src)
    #         keyStr[reg] = "".join([s for s in keyStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
    #         #print(keyStr[reg])


    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir +"/"
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if vaultStr[reg] != '':
            outfile = outdir + "/" + reg + "/" + service_dir + "/" + auto_tfvars_filename

            vault_str = "##Add New Vaults for " + reg.lower() + " here##"
            key_str = "##Add New Keys for " + reg.lower() + " here##"

            vaultStr[reg] = vault_template.render(count=0, region=reg).replace(vault_str,vaultStr[reg])
            vaultStr[reg] += key_template.render(count=0, region=reg).replace(key_str,keyStr[reg])
            vaultStr[reg] = "".join([s for s in vaultStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            resource=sheetName.lower()
            commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

            oname = open(outfile, "w+")
            oname.write(vaultStr[reg])
            oname.close()
            print(outfile + " for keys and vaults has been created for region " + reg)

