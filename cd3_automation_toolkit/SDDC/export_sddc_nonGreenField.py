#!/usr/bin/python3
# This script will export all SDDC details into cd3
# Author: Suruchi
# Oracle Consulting.

import re
import sys
import oci
import json
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.core.blockstorage_client import BlockstorageClient
import os
sys.path.append(os.getcwd() + "/..")
from commonTools import *


def get_volume_data(bvol, volume_id, ct):
    volume_data = bvol.get_volume(volume_id).data
    vol_name = volume_data.display_name
    comp_list = list(ct.ntk_compartment_ids.values())
    vol_comp = list(ct.ntk_compartment_ids.keys())[comp_list.index(volume_data.compartment_id)]
    return vol_comp+'@'+vol_name

# Execution of the code begins here
def export_sddc(inputfile, outdir, service_dir,config,signer, ct, export_compartments=[], export_regions=[]):
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    global importCommands, values_for_column_sddc, df, sheet_dict_sddc  # declaring global variables

    sheetName= "SDDCs"
    sheetNameNetwork = "SDDCs-Network"
    importCommands = {}

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
        sddc_client = oci.ocvp.SddcClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        vnc = VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        bvol = BlockstorageClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)

        region = reg.capitalize()
        sddc_keys = {}
        for ntk_compartment_name in export_compartments:
            sddcs = oci.pagination.list_call_get_all_results(sddc_client.list_sddcs,
                                                                    compartment_id=ct.ntk_compartment_ids[
                                                                        ntk_compartment_name],lifecycle_state="ACTIVE")

            for sddc in sddcs.data:
                mgmt_vols = []
                wkld_vols = []
                sddc = sddc_client.get_sddc(sddc_id=sddc.id).data
                sddc_init_config1 = sddc.initial_configuration.initial_cluster_configurations
                sddc_init_config=sddc_init_config1[0]
                sddc_network=sddc_init_config.network_configuration
                sddc_datastores=  sddc_init_config.datastores

                if sddc.lifecycle_state=='DELETED':
                    continue
                tf_name = commonTools.check_tf_variable(sddc.display_name)

                # Get ssh keys for sddc
                key_name = commonTools.check_tf_variable(sddc.display_name)
                ssh_key = sddc.ssh_authorized_keys
                ssh_key = json.dumps(ssh_key)
                sddc_keys[key_name] = ssh_key
                importCommands[reg].write("\nterraform import \"module.sddcs[\\\"" + tf_name + "\\\"].oci_ocvp_sddc.sddc\" " + sddc.id)
                if 'Standard' in sddc_init_config.initial_host_shape_name:
                    for item in sddc_datastores:
                        if item.datastore_type == "MANAGEMENT":
                            mgmt_vols = item.block_volume_ids
                        if item.datastore_type == "WORKLOAD":
                            wkld_vols = item.block_volume_ids

                for col_header in values_for_column_sddc.keys():
                    if (col_header == "Region"):
                        values_for_column_sddc[col_header].append(region)
                    elif (col_header == "Compartment Name"):
                        values_for_column_sddc[col_header].append(ntk_compartment_name)
                    elif ("Availability Domain" in col_header):
                        value = sddc_init_config.__getattribute__(sheet_dict_sddc[col_header])
                        ad = ""
                        if ("AD-1" in value or "ad-1" in value):
                            ad = "AD1"
                        elif ("AD-2" in value or "ad-2" in value):
                            ad = "AD2"
                        elif ("AD-3" in value or "ad-3" in value):
                            ad = "AD3"
                        values_for_column_sddc[col_header].append(ad)
                    elif col_header == 'Management Block Volumes':
                        mgmt_vol_data = ""
                        for vol_id in mgmt_vols:
                            mgmt_vol_data = mgmt_vol_data+","+get_volume_data(bvol, volume_id=vol_id, ct=ct)
                        values_for_column_sddc[col_header].append(mgmt_vol_data[1:])
                    elif col_header == 'Workload Block Volumes':
                        wkld_vol_data = ""
                        for vol_id in wkld_vols:
                            wkld_vol_data = wkld_vol_data+","+get_volume_data(bvol, volume_id=vol_id, ct=ct)
                        values_for_column_sddc[col_header].append(wkld_vol_data[1:])

                    elif col_header == 'SSH Key Var Name':
                        values_for_column_sddc[col_header].append(key_name)
                    elif (col_header == "Provisioning Subnet"):
                        subnet_id = sddc_network.provisioning_subnet_id
                        subnet_info = vnc.get_subnet(subnet_id)
                        sub_name = subnet_info.data.display_name  # Subnet-Name
                        vcn_name = vnc.get_vcn(subnet_info.data.vcn_id).data.display_name  # vcn-Name
                        values_for_column_sddc[col_header].append(vcn_name+"_"+sub_name)
                    elif(col_header == "NSX Edge Uplink1 VLAN"):
                        vlan_id = sddc_network.nsx_edge_uplink1_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge Uplink1 VLAN"):
                        vlan_id = sddc_network.nsx_edge_uplink1_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge Uplink2 VLAN"):
                        vlan_id = sddc_network.nsx_edge_uplink2_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX Edge VTEP VLAN"):
                        vlan_id = sddc_network.nsx_edge_v_tep_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "NSX VTEP VLAN"):
                        vlan_id = sddc_network.nsx_v_tep_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vMotion VLAN"):
                        vlan_id = sddc_network.vmotion_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vSAN VLAN"):
                        vlan_id = sddc_network.vsan_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "vSphere VLAN"):
                        vlan_id = sddc_network.vsphere_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "HCX VLAN"):
                        vlan_id = sddc_network.hcx_vlan_id
                        if vlan_id == None:
                            values_for_column_sddc[col_header].append("")
                        else:
                            values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "Replication Net VLAN"):
                        vlan_id = sddc_network.replication_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif (col_header == "Provisioning Net VLAN"):
                        vlan_id = sddc_network.provisioning_vlan_id
                        values_for_column_sddc[col_header].append(vnc.get_vlan(vlan_id).data.display_name)
                    elif col_header.lower() in commonTools.tagColumns:
                        values_for_column_sddc = commonTools.export_tags(sddc, col_header,
                                                                           values_for_column_sddc)
                    else:
                        oci_objs = [sddc,sddc_init_config,sddc_network,sddc_datastores]
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
