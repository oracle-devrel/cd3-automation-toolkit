#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI RPC for a given DRG between regions.
#
# Author: Ulaganathan N
# Oracle Consulting
#
import itertools
import shutil
from oci.identity import IdentityClient
import oci
import sys
import os
from pathlib import Path

sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

# Setting current working dir.
owd = os.getcwd()

def find_subscribed_regions(inputfile, outdir, service_dir, prefix, config,signer,auth_mechanism):
    subs_region_list = []
    new_subs_region_list = []
    subs_region_pairs = []

    idc = IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])

    for reg in regionsubscriptions.data:
        status = getattr(reg, 'status')
        if status == "READY":
            region_name = getattr(reg, 'region_name')
            subs_region_list.append(region_name)

    for item in subs_region_list:
        new_subs_region_list.append(item.split("-")[1])

    for item in list(itertools.permutations(new_subs_region_list, 2)):
        subs_region_pairs.append(item[0] + "##" + item[1])

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('rpc-root-terraform-template')
    output = template.render(subscribed_regions=subs_region_list)

    # Generate root file from template
    for region in new_subs_region_list:
        srcdir = Path(f"{outdir}/global")
        if not os.path.exists(Path(f"{srcdir}/modules/rpc")):
            os.makedirs(Path(f"{srcdir}/modules/rpc"))

        # to save the results
        shutil.copyfile(
            Path(f"{owd}/Network/Global/templates/rpc-module/rpc-variables-terraform-template"),
            Path(f"{srcdir}/modules/rpc/variables.tf"))
        os.chdir(Path(rf"{srcdir}/rpc/"))
        with open("rpc.tf", "w") as fh:
            fh.write(output)

        with open("rpc.tf", "r+") as provider_file:
            provider_file_data = provider_file.read().rstrip()
        if auth_mechanism == 'instance_principal':
            provider_file_data = provider_file_data.replace("provider \"oci\" {", "provider \"oci\" {\nauth = \"InstancePrincipal\"")
        if auth_mechanism == 'session_token':
            provider_file_data = provider_file_data.replace("provider \"oci\" {", "provider \"oci\" {\nauth = \"SecurityToken\"\nconfig_file_profile = \"DEFAULT\"")

        f = open("rpc.tf", "w+")
        f.write(provider_file_data)
        f.close()

        # For generating provider config
        file_loader_rpc = FileSystemLoader(f'{Path(__file__).parent}/templates/rpc-module')
        env_rpc = Environment(loader=file_loader_rpc, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
        provider_template = env_rpc.get_template('rpc-provider-terraform-template')
        provider_output = provider_template.render(subscribed_regions=subs_region_list)

        # to save the results
        os.chdir(Path(rf"{srcdir}/modules/rpc"))
        with open("providers.tf", "w") as provider:
            provider.write(provider_output)

        # For generating source-destination template
        file_loader_main = FileSystemLoader(f'{Path(__file__).parent}/templates/rpc-module')
        env_main = Environment(loader=file_loader_main, keep_trailing_newline=True, trim_blocks=True,
                               lstrip_blocks=True)
        source_dest_template = env_main.get_template('rpc-source-destination-terraform-template')
        source_dest_output = source_dest_template.render(subscribed_regions=subs_region_pairs)

        # to save the results
        os.chdir(Path(f"{srcdir}/modules/rpc"))
        with open("main.tf", "w") as main_file:
            main_file.write(source_dest_output)

    return True


# Execution of the code begins here
def create_rpc_resource(inputfile, outdir, service_dir, prefix, auth_mechanism, config_file,ct, non_gf_tenancy):
    # Call pre-req func
    rpc_safe_file = {}
    config, signer = ct.authenticate(auth_mechanism, config_file)
    find_subscribed_regions(inputfile, outdir, service_dir, prefix, config,signer,auth_mechanism)

    os.chdir(owd)

    tfStr = {}
    requester_drg_name = ''
    accepter_drg_rt_name = ''
    filename = inputfile

    sheetName = "DRGs"
    auto_tfvars_filename = prefix + '_' + "rpcs" + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('rpc-module-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # creating rpc.safe file
    rpc_file = f'{outdir}/global/rpc/' + "create_rpc.safe"
    # Used against all regions to avoid duplicate entry
    with open(f'{rpc_file}', 'w+') as file:
        file.write("rpc pair details:: \n")

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        tfStr["global"] = ''


    match_list = []
    for i in df.index:
        if str(df.loc[i, 'Attached To']).lower().startswith("rpc"):
            region = str(df.loc[i, 'Region'])
            region = region.strip().lower()

            if region in commonTools.endNames:
                break

            if region not in ct.all_regions:
                print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
                exit(1)

            # temporary dictionary1 and dictionary2
            tempStr = {}
            tempdict = {}

            # Check if values are entered for mandatory fields
            if (str(df.loc[i, 'Region']).lower() == 'nan' or str(
                    df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'Attached To']).lower() == 'nan' or str(
                df.loc[i, 'DRG Name']).lower() == 'nan' or str(
                df.loc[i, 'RPC Display Name']).lower() == 'nan'
            ):
                print(
                    "\nColumn Region, Compartment Name, DRG Name,"
                    "Attached To, RPC Display Name cannot be left empty in DRGs sheet of "
                    "CD3..exiting...")
                exit(1)

            requester_drg_name = str(df.loc[i, 'DRG Name']).strip()
            target_details = str(df.loc[i, 'Attached To'])
            attached_to = target_details.replace(target_details.split("::")[1], target_details.split("::")[1].lower())
            existing_line = f"{attached_to}::{requester_drg_name}"

            # match = re.findall(existing_line, fo)
            # if match:
            #     match_list.append(match[0])
            #
            # flatMatchList = [element for innerList in match_list for element in match_list]
            # flatMatchList = set(flatMatchList)
            # flatMatchList = list(flatMatchList)

            with open(f'{rpc_file}', encoding='utf8') as file:
                line_count = 0
                for line in file.readlines():
                    # print("line", line)
                    # print("existing_line", existing_line)
                    if line.strip() == existing_line.strip():
                        # print("data", line, existing_line)
                        line_count += 1

                # print("Current count", line_count)
                if line_count == 0:
                    # if existing_line not in fo:
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

                        if columnname == 'RPC Display Name':
                            columnvalue = columnvalue.strip()
                            display_tf_name = commonTools.check_tf_variable(columnvalue)
                            accepter_rpc_display_name = df.loc[i + 1, 'RPC Display Name']
                            accepter_compartment_name = df.loc[i + 1, 'Compartment Name']
                            accepter_compartment_name = str(accepter_compartment_name)
                            accepter_compartment_name = commonTools.check_tf_variable(accepter_compartment_name)
                            tempdict = {'rpc_tf_name': display_tf_name, 'rpc_name':columnvalue,
                                        'accepter_rpc_display_name': accepter_rpc_display_name,
                                        'accepter_compartment_name': accepter_compartment_name}

                        if columnname == 'Compartment Name':
                            compartment_var_name = columnvalue.strip()
                            compartment_var_name = str(compartment_var_name)
                            compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                            tempdict = {'requester_compartment_name': compartment_var_name}

                        if columnname == 'Attached To':
                            accepter_compartment_var_name = columnvalue.strip().split("::")
                            accepter_region = accepter_compartment_var_name[1]
                            accepter_drg_name = accepter_compartment_var_name[2]
                            tempdict = {'accepter_region': accepter_region.lower(),
                                        'accepter_drg_name': accepter_drg_name}

                        if columnname == 'Region':
                            requester_region = columnvalue.strip().lower()
                            tempdict = {'requester_region': requester_region}

                        if columnname == 'DRG Name':
                            requester_drg_name = columnvalue.strip()
                            tempdict = {'requester_drg_name': requester_drg_name}

                        if columnname == 'DRG RT Name':
                            requester_drg_rt_name = "null"
                            if columnvalue.strip() != '' and columnvalue.strip() != 'nan':
                                requester_drg_rt_name = columnvalue.strip()
                            if str(df.loc[i + 1, 'DRG RT Name']).lower().strip() == "nan":
                                accepter_drg_rt_name = "null"
                            else:
                                accepter_drg_rt_name = df.loc[i + 1, 'DRG RT Name']
                                # if df.loc[df['Region']] == accepter_region.capitalize() and df.loc[
                                #     df['Attached To'] == f"RPC::{region}::{requester_drg_name}", 'DRG RT Name'].any():
                                #     accepter_drg_rt_name = \
                                #         df.loc[df[
                                #                    'Attached To'] == f"RPC::{region}::{requester_drg_name}", 'DRG RT Name'].iloc[
                                #             0]

                            tempdict = {'requester_drg_rt_name': requester_drg_rt_name,
                                        'accepter_drg_rt_name': accepter_drg_rt_name}

                        columnname = commonTools.check_column_headers(columnname)
                        tempStr[columnname] = str(columnvalue).strip()
                        tempStr.update(tempdict)

                    # Write to create_rpc_safe file
                    with open(f'{rpc_file}', 'a') as f:
                        # print("ADDED LINE",
                        #      f"rpc::{requester_region.lower()}::{requester_drg_name.lower()}::{accepter_drg_name.lower()}")
                        f.write(
                            f"RPC::{requester_region}::{requester_drg_name}::{accepter_drg_name} \n")
                    # Write all info to TF string
                    tfStr["global"] = tfStr["global"] + template.render(tempStr)

    # Write TF string to the file in global directory

    reg_out_dir = f'{outdir}/global/rpc/'
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    resource = sheetName.lower()
    commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

    if tfStr["global"] != '':
        # Generate RPC String
        src = "##Add New RPC for global here##"
        tfStr["global"] = template.render(count=0).replace(src, tfStr["global"] + "\n" + src)
        tfStr["global"] = "".join([s for s in tfStr["global"].strip().splitlines(True) if s.strip("\r\n").strip()])

        # Write to TF file
        outfile = reg_out_dir + "/" + auto_tfvars_filename
        # tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
        oname = open(outfile, "w")
        print(outfile + " has been created inside Global dir")
        oname.write(tfStr["global"])
        oname.close()

