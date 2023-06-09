#!/usr/bin/python3
# This script will export all SDDC details into cd3
# Author: Suruchi
# Oracle Consulting.

import re
import argparse
import sys
import oci
import json
from oci.core.virtual_network_client import VirtualNetworkClient
import os
from oci.config import DEFAULT_LOCATION
sys.path.append(os.getcwd() + "/..")
from commonTools import *


def parse_args():
    parser = argparse.ArgumentParser(description="Export SDDC in OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export SDDC objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("service_dir",help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export SDDC Objects")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                   required=False)

    return parser.parse_args()


def export_sddc(inputfile, outdir, service_dir,config,ct, export_compartments=[], export_regions=[],display_names=[],ad_names=[]):
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    configFileName = config
    config = oci.config.from_file(file_location=configFileName)

    global importCommands, values_for_column_sddc, df, sheet_dict_sddc  # declaring global variables

    sheetName= "SDDCs"
    sheetNameNetwork = "SDDCs-Network"
    importCommands = {}

    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)
    var_data = {}

    AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else ("AD2" if ("AD-2" in ad or "ad-2" in ad) else ("AD3" if ("AD-3" in ad or "ad-3" in ad) else " NULL"))  # Get shortend AD

    df, values_for_column_sddc = commonTools.read_cd3(cd3file, sheetName)
    df, values_for_column_b = commonTools.read_cd3(cd3file, sheetNameNetwork)

    for k, v in values_for_column_b.items():
        values_for_column_sddc[k] = v

    sheet_dict_sddc = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- SDDCs and SDDCs-Network will be overwritten during this export process!!!\n")

    # Create of .sh file
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg+"/"+service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    for reg in export_regions:
        var_data[reg] = ""
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        importCommands[reg].write("\n######### Writing import for VCNs #########\n")
        config.__setitem__("region", ct.region_dict[reg])
        sddc_client = oci.ocvp.SddcClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        vnc = VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)

        region = reg.capitalize()
        sddc_keys = {}
        for ntk_compartment_name in export_compartments:
            sddcs = oci.pagination.list_call_get_all_results(sddc_client.list_sddcs,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],lifecycle_state="ACTIVE")

            for sddc in sddcs.data:
                sddc = sddc_client.get_sddc(sddc_id=sddc.id).data
                if sddc.lifecycle_state=='DELETED':
                    continue
                tf_name = commonTools.check_tf_variable(sddc.display_name)

                # Get ssh keys for sddc
                key_name = commonTools.check_tf_variable(sddc.display_name)
                ssh_key = sddc.ssh_authorized_keys
                ssh_key = json.dumps(ssh_key)
                sddc_keys[key_name] = ssh_key
                importCommands[reg].write("\nterraform import \"module.sddcs[\\\"" + tf_name + "\\\"].oci_ocvp_sddc.sddc\" " + sddc.id)

                for col_header in values_for_column_sddc.keys():
                    if (col_header == "Region"):
                        values_for_column_sddc[col_header].append(region)
                    elif (col_header == "Compartment Name"):
                        values_for_column_sddc[col_header].append(ntk_compartment_name)
                    elif ("Availability Domain" in col_header):
                        value = sddc.__getattribute__(sheet_dict_sddc[col_header])
                        ad = ""
                        if ("AD-1" in value or "ad-1" in value):
                            ad = "AD1"
                        elif ("AD-2" in value or "ad-2" in value):
                            ad = "AD2"
                        elif ("AD-3" in value or "ad-3" in value):
                            ad = "AD3"
                        values_for_column_sddc[col_header].append(ad)
                    elif col_header == 'SSH Key Var Name':
                        values_for_column_sddc[col_header].append(key_name)
                    elif (col_header == "Provisioning Subnet"):
                        subnet_id = sddc.provisioning_subnet_id
                        subnet_info = vnc.get_subnet(subnet_id)
                        sub_name = subnet_info.data.display_name  # Subnet-Name
                        vcn_name = vnc.get_vcn(subnet_info.data.vcn_id).data.display_name  # vcn-Name
                        values_for_column_sddc[col_header].append(vcn_name+"_"+sub_name)
                    elif(col_header == "NSX Edge Uplink1 VLAN"):
                        vlan_id = sddc.nsx_edge_uplink1_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge Uplink1 VLAN"):
                        vlan_id = sddc.nsx_edge_uplink1_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge Uplink2 VLAN"):
                        vlan_id = sddc.nsx_edge_uplink2_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge VTEP VLAN"):
                        vlan_id = sddc.nsx_edge_v_tep_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX VTEP VLAN"):
                        vlan_id = sddc.nsx_v_tep_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vMotion VLAN"):
                        vlan_id = sddc.vmotion_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vSAN VLAN"):
                        vlan_id = sddc.vsan_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vSphere VLAN"):
                        vlan_id = sddc.vsphere_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "HCX VLAN"):
                        vlan_id = sddc.hcx_vlan_id
                        if vlan_id == None:
                            values_for_column_sddc[col_header].append("")
                        else:
                            values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "Replication Net VLAN"):
                        vlan_id = sddc.replication_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "Provisioning Net VLAN"):
                        vlan_id = sddc.provisioning_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_sddc = commonTools.export_tags(sddc, col_header,
                                                                           values_for_column_sddc)
                    else:
                        oci_objs = [sddc]
                        values_for_column_sddc = commonTools.export_extra_columns(oci_objs, col_header,
                                                                                    sheet_dict_sddc,
                                                                                    values_for_column_sddc)

        file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
        # Read variables file data
        with open(file, 'r') as f:
            var_data[reg] = f.read()

        tempStr = ""
        for k, v in sddc_keys.items():
            tempStr = "\t"+k + " = " + v + "\n" + tempStr

        tempStr = "\n" + tempStr
        tempStr = "#START_sddc_ssh_keys#" + tempStr + "\t#sddc_ssh_keys_END#"
        if ("\\n" in tempStr):
            tempStr = tempStr.replace("\\n", "\\\\n")

        var_data[reg] = re.sub('#START_sddc_ssh_keys#.*?#sddc_ssh_keys_END#', tempStr, var_data[reg],flags=re.DOTALL)

        # Write variables file data
        with open(file, "w") as f:
            f.write(var_data[reg])

        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')


    commonTools.write_to_cd3(values_for_column_sddc, cd3file, sheetName)
    commonTools.write_to_cd3(values_for_column_sddc, cd3file, sheetNameNetwork)
    print("{0} SDDC Details exported into CD3.\n".format(len(values_for_column_sddc["Region"])))


if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    export_sddc(args.inputfile, args.outdir, args.service_dir,args.config, args.export_compartments, args.export_regions)
