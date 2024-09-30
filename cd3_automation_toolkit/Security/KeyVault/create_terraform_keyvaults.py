#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Security components
# Key/Vault
#
# Author: Lasya Vadavalli
# Oracle Consulting


from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import math
from oci.config import DEFAULT_LOCATION
from commonTools import *


######
# Required Inputs- input Excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_keyvaults(inputfile, outdir, service_dir, prefix, ct):
    vaultStr = {}
    keyStr = {}
    prev_keyStr = {}
    tempStr_vault = {}
    tempStr_keys = {}
    filename = inputfile
    outfile = {}
    oname = {}
    sheetName = "KMS"
    prev_vault = ""
    prev_vault_type = ""
    prev_region = ""

    flag = 0
    prev_flag = 0

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
        prev_keyStr[eachregion] = ''

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        elif (region == 'nan'):
            pass
        elif region != 'nan' and region not in ct.all_regions:
            print("\nROW "+str(i+3)+": ERROR!!! Invalid Region; It should be a valid region..Exiting!")
            exit(1)
        region = region if region != 'nan' else prev_region
        prev_region = region

        # temporary dictionaries
        tempdict_vault = {}
        tempdict_keys = {}


        #For empty vault rows, assign the previous vault details
        current_vault = str(df.loc[i, 'Vault Display Name'])
        vault_name = current_vault if current_vault != 'nan' else prev_vault
        prev_vault = vault_name
        vault_tf_name = commonTools.check_tf_variable(vault_name)

        current_vault_type = str(df.loc[i, 'Vault type'])
        if current_vault_type != 'nan':
            vault_type = current_vault_type
            if vault_type.lower() in ["default", "virtual_private"]:
                if vault_type.lower() == "virtual_private":
                    flag = 1
                    prev_flag = flag
                if vault_type.lower() == "default":
                    flag = 0
                    prev_flag = flag
            else:
                print("ROW "+str(i+3)+": Invalid Vault_type!!. Vault type should be either 'DEFAULT or 'VIRTUAL_PRIVATE'. Try Again.  Exiting... ")
                exit(1)
            prev_vault_type = vault_type

        else:
            vault_type = prev_vault_type
            flag = prev_flag

        if ((df.loc[i, 'Vault Compartment Name'])!= 'nan' and str(df.loc[i, 'Vault type'])!= 'nan' and str(df.loc[i, 'Vault Display Name']) != 'nan' ):
            # Fetch data from Excel; Loop through columns
            for columnname in dfcolumns:
                # Column value
                columnvalue = str(df[columnname][i]).strip()

                # Check for boolean/null in column values
                columnvalue = commonTools.check_columnvalue(columnvalue)

                # Check for multivalued columns
                tempdict_vault = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict_vault)

                # Process Defined and Freeform Tags
                if str(columnname).lower() in ["vault defined tags", "vault freeform tags"]:
                    tempdict_vault = commonTools.split_tag_values(columnname, columnvalue, tempdict_vault)

                elif columnname == "Vault Compartment Name":
                    vault_compartment_var_name = columnvalue.strip()
                    vault_compartment_var_name = commonTools.check_tf_variable(vault_compartment_var_name)
                    tempdict_vault = {'vault_compartment_tf_name': vault_compartment_var_name}

                elif columnname == "Vault Display Name":
                    tempdict_vault = {'vault_display_tf_name': vault_tf_name,'vault_display_name':columnvalue}

                elif columnname == "Vault type":
                    if columnvalue != '' and columnvalue.lower() != 'nan':
                        tempdict_vault = {'vault_type': vault_type.upper()}


                elif columnname == "Replica Region":
                    if columnvalue != '' and columnvalue.lower() != 'nan':
                        columnvalue = columnvalue.strip().lower()
                        if columnvalue != region:
                            if columnvalue in commonTools.endNames:
                                break
                            if columnvalue not in ct.all_regions:
                                print(
                                    "ROW "+str(i+3)+": Invalid Replica Region!! Tenancy is not subscribed to this region. Please try again")
                                exit(1)
                            tempdict_vault = {'replica_region': ct.region_dict[columnvalue]}
                        else:
                            print(
                                "ROW "+str(i+3)+": Error!! Replica region can't be same as the primary vault's region. Try with a different region. Exiting...")
                            exit(1)
                    else:
                        tempdict_vault = {'replica_region': ''}

                else:
                    columnname = commonTools.check_column_headers(columnname)
                    tempStr_vault[columnname] = str(columnvalue).strip()

                tempStr_vault.update(tempdict_vault)
            # Write all vaults info to TF string
            vaultStr[region] += vault_template.render(tempStr_vault)


        if (str(df.loc[i, 'Key Display Name']).lower() != 'nan'):

            for columnname in dfcolumns:
                # Fetch data from Excel; Loop through columns
                columnvalue = str(df[columnname][i]).strip()
                if columnname in ['Key Compartment Name', 'Protection mode', 'Algorithm', 'Length in bits'] and columnvalue =='nan':
                    print("ROW "+str(i+3)+": Error!! Key Display Name, Algorithm and Length are mandatory fields to create Keys. Enter these values and try again. Exiting...")
                    exit(1)
                else:
                    # Process Defined and Freeform Tags for keys
                    if str(columnname).lower() in ["key defined tags", "key freeform tags"]:
                        tempdict_keys = commonTools.split_tag_values(columnname, columnvalue, tempdict_keys)

                    elif columnname == "Key Compartment Name":
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            columnvalue = columnvalue.strip()
                            key_compartment_var_name = commonTools.check_tf_variable(columnvalue)
                            tempdict_keys = {'key_compartment_tf_name': key_compartment_var_name,
                                             'vault_name': vault_tf_name}

                    elif columnname == "Key Display Name":
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            columnvalue = columnvalue.strip()
                            key_display_tf_name = commonTools.check_tf_variable(columnvalue)
                            tempdict_keys = {'key_display_tf_name': key_display_tf_name,'key_display_name' : columnvalue}
                            if (str(df.loc[i, 'Key Compartment Name']).lower() == 'nan' or str(
                                    df.loc[i, 'Algorithm']).lower() == 'nan' or str(
                                df.loc[i, 'Length in bits']).lower() == 'nan'):
                                print(
                                    "ROW "+str(i+3)+": Error!! Key Compartment Name, Key Display Name, Algorithm and Length are mandatory fields to create Keys. Enter these values and try again. Exiting...")
                                exit(1)
                            else:
                                pass

                    elif columnname == "Protection mode":
                        columnvalue = columnvalue.strip().lower()
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            if columnvalue in ['hsm', 'software']:
                                tempdict_keys = {'protection_mode': columnvalue.upper()}
                            else:
                                print(
                                    "ROW "+str(i+3)+": Error!! Invalid Protection mode. Value should either be 'hsm' or 'software'. Try Again. Exiting...")
                                exit(1)

                    elif columnname == "Algorithm":
                        columnvalue = columnvalue.strip().lower()
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            if columnvalue in ["aes", "rsa", "ecdsa"]:
                                tempdict_keys = {'algorithm': columnvalue.upper()}
                                algorithm = tempdict_keys.get('algorithm')
                            else:
                                print(
                                    "ROW "+str(i+3)+": Error!! Algorithm is not valid. Only 'AES', 'RSA', 'ECDSA' algorithms are supported. Exiting...")
                                exit(1)

                    elif columnname == "Length in bits":
                        columnvalue = columnvalue.strip()
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            if algorithm.lower() == "aes" and columnvalue in ["128", "192", "256"]:
                                tempdict_keys = {'length': int(int(columnvalue) / 8)}
                            elif algorithm.lower() == "rsa" and columnvalue in ["2048", "3072", "4096"]:
                                tempdict_keys = {'length': int(int(columnvalue) / 8)}
                            elif algorithm.lower() == "ecdsa" and columnvalue in ["256", "384", "521"]:
                                tempdict_keys = {'length': int(math.ceil(int(columnvalue) / 8))}
                            else:
                                print(f"ROW {i + 3}: Error!! Invalid length for {algorithm.upper()} algorithm. Exiting...")
                                exit(1)

                    elif columnname == "Curve Id":
                        columnvalue = columnvalue.strip()
                        if columnvalue != '' and columnvalue.lower() != 'nan':
                            if algorithm.lower() == "ecdsa":
                                tempdict_keys = {'curve_id': columnvalue}
                            elif algorithm.lower() == "aes" or algorithm.lower() == "rsa":
                                tempdict_keys = {'curve_id': ''}
                        else:
                            tempdict_keys = {'curve_id': ''}

                    elif columnname == "Auto rotation":
                        columnvalue = columnvalue.strip().lower()

                        if columnvalue.lower() == "true":
                            auto_rotation_enabled = True
                            if flag == 1:
                                tempdict_keys = {'auto_rotation': "true"}

                            else:
                                print("ROW "+str(i+3)+": Error!! Auto rotation is only possible for Virtual Private Vaults. Exiting...")
                                exit(1)
                        elif columnvalue == "false" or columnvalue.lower() == 'nan' or columnvalue == '':
                            tempdict_keys = {'auto_rotation': None}
                            auto_rotation_enabled = False

                        else:
                            print("ROW "+str(i+3)+": Auto rotation values should be either 'true'/'false'. Try Again. Exiting...")
                            exit(1)


                    elif columnname == "Rotation interval in days":
                        columnvalue = columnvalue.strip()
                        if columnvalue != 'nan':
                            if flag == 1:
                                if auto_rotation_enabled:
                                    if 60 <= int(columnvalue) <= 365:
                                        tempdict_keys = {'rotation_interval': int(columnvalue)}
                                    else:
                                        print("ROW "+str(i+3)+": Error!! Rotation interval should be between 60 - 365 days. Exiting!!")
                                        exit(1)
                                else:
                                    tempdict_keys = {'rotation_interval': None}
                            else:
                                print("ROW "+str(i+3)+": Error!! Rotation interval can only be setup for keys in Virtual Private Vaults. Exiting...")
                                exit(1)
                        else:
                            tempdict_keys = {'rotation_interval': None}

                    else:
                        columnname = commonTools.check_column_headers(columnname)
                        tempStr_keys[columnname] = str(columnvalue).strip()


                    tempStr_keys.update(tempdict_keys)
            # Write all keys info to TF string
            keyStr[region] += key_template.render(tempStr_keys)
            prev_keyStr[region] = keyStr[region]

        else:
            keyStr[region] = prev_keyStr[region]


    # Write TF string to the file in respective region directories
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir + "/"
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if vaultStr[reg] != '':
            outfile = outdir + "/" + reg + "/" + service_dir + "/" + auto_tfvars_filename

            vault_str = "##Add New Vaults for " + reg.lower() + " here##"
            key_str = "##Add New Keys for " + reg.lower() + " here##"

            vaultStr[reg] = vault_template.render(count=0, region=reg).replace(vault_str, vaultStr[reg] + "\n" + vault_str)
            vaultStr[reg] += key_template.render(count=0, region=reg).replace(key_str, keyStr[reg] + "\n" + key_str)
            vaultStr[reg] = "".join([s for s in vaultStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            oname = open(outfile, "w+")
            oname.write(vaultStr[reg])
            oname.close()
            print(outfile + " for keys and vaults has been created for region " + reg)

