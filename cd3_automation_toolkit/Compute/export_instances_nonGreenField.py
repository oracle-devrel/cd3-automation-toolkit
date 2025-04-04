#!/usr/bin/python3
# This script will export all oci instances details into cd3
# Author: Tharun Karam
# Oracle Consulting.

import re
import sys
import oci
import os
import subprocess as sp
sys.path.append(os.getcwd() + "/..")
from commonTools import *


def adding_columns_values(region, ad, fd, vs, publicip, privateip, os_dname, shape, key_name, c_name,
                          bkp_policy_name, nsgs, d_host, instance_data, values_for_column_instances, bdet,
                          cpcn, shape_config, vnic_info, vnic_defined_tags, vnic_freeform_tags, launch_options,avail_config,ins_options,
                          platform_config, plugin_config):
    for col_header in values_for_column_instances.keys():
        if (col_header == "Region"):
            values_for_column_instances[col_header].append(region)
        elif (col_header == "Availability Domain(AD1|AD2|AD3)"):
            values_for_column_instances[col_header].append(ad)
        elif (col_header == "Fault Domain"):
            values_for_column_instances[col_header].append(fd)
        elif (col_header == "Network Details"):
            values_for_column_instances[col_header].append(vs)
        elif (col_header == "Pub Address"):
            values_for_column_instances[col_header].append(publicip)
        elif (col_header == "IP Address"):
            values_for_column_instances[col_header].append(privateip)
        elif (col_header == "Source Details"):
            values_for_column_instances[col_header].append(os_dname)
        elif (col_header == "Shape"):
            values_for_column_instances[col_header].append(shape)
        elif (col_header == "Boot Volume Size In GBs"):
            size = bdet.size_in_gbs
            if size < 50:
                size=""
            values_for_column_instances[col_header].append(size)
        elif (col_header == "SSH Key Var Name"):
            values_for_column_instances[col_header].append(key_name)
        elif (col_header == "Compartment Name"):
            values_for_column_instances[col_header].append(c_name)
        elif (col_header == "Backup Policy"):
            values_for_column_instances[col_header].append(bkp_policy_name)
        elif (col_header == "NSGs"):
            values_for_column_instances[col_header].append(nsgs)
        elif (col_header == "VNIC Defined Tags"):
            values_for_column_instances[col_header].append(vnic_defined_tags)
        elif (col_header == "VNIC Freeform Tags"):
            values_for_column_instances[col_header].append(vnic_freeform_tags)
        elif (col_header == "VNIC Display Name"):
            values_for_column_instances[col_header].append(vnic_info.display_name)

        elif(col_header.lower().startswith("plugin")):
            col_temp = col_header.lower().replace("plugin","")
            col_temp=col_temp.strip()
            col_temp=col_temp.strip("_")
            col_temp=col_temp.replace(" ","_")
            col_temp = col_temp.replace("-", "_")
            values_for_column_instances[col_header].append(plugin_config.get(col_temp))

        elif(col_header == "Dedicated VM Host"):
            if (d_host == None):
                values_for_column_instances[col_header].append('')
            else:
                values_for_column_instances[col_header].append(d_host.data.display_name)
        elif (col_header == "Custom Policy Compartment Name"):
            values_for_column_instances[col_header].append(cpcn)
        elif str(col_header).lower() in commonTools.tagColumns:
            values_for_column_instances = commonTools.export_tags(instance_data, col_header,
                                                                  values_for_column_instances)
        else:
            oci_objs = [instance_data, bdet, shape_config, vnic_info, d_host, launch_options, avail_config, ins_options, platform_config]
            values_for_column_instances = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_instances,
                                                                           values_for_column_instances)


def find_vnic(ins_id, compartment_id):
    compute = oci.core.ComputeClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    #for comp in all_compartments:
    net = oci.pagination.list_call_get_all_results(compute.list_vnic_attachments, compartment_id=compartment_id,
                                                       instance_id=ins_id)
    if (len(net.data)):
        return net


def __get_instances_info(compartment_name, compartment_id, reg_name, display_names, ad_names, export_tags, ct,state):
    config.__setitem__("region", ct.region_dict[reg_name])
    compute = oci.core.ComputeClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    network = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    bc = oci.core.BlockstorageClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
    instance_info = oci.pagination.list_call_get_all_results(compute.list_instances, compartment_id=compartment_id)
    # print(instance_info.data)

    for ins in instance_info.data:
        ins_details = compute.get_instance(instance_id=ins.id)
        # print(ins_details.data)
        if (ins.lifecycle_state != 'TERMINATED'):
            ins_dname = ins.display_name  # instance display name
            ins_ad = ins.availability_domain  # avalibility domain
            AD_name = AD(ins_ad)

            #Continue to next one if AD names donot match the filter
            if (ad_names is not None):
                if (not any(e in AD_name for e in ad_names)):
                    continue

            # Continue to next one if display names do not match the filter
            if (display_names is not None):
                if (not any(e in ins_dname for e in display_names)):
                    continue

            # Tags filter
            ins_defined_tags = ins.defined_tags
            tags_list=[]
            for tkey,tval in ins_defined_tags.items():
                for kk,vv in tval.items():
                    tag = tkey+"."+kk+"="+vv
                    tags_list.append(tag)

            if export_tags == []:
                check = True
            else:
                check = any(e in tags_list for e in export_tags)
            #None of Tags from export_tags exist on this instance; Dont export this instance
            if check == False:
                continue

            # Continue to next one if it's an OKE instance
            if 'oke-' in ins_dname:
                ins_defined_tags = ins.defined_tags
                if 'Oracle-Tags' in ins_defined_tags.keys():
                    if 'CreatedBy' in ins_defined_tags['Oracle-Tags'].keys():
                        created_by = ins_defined_tags['Oracle-Tags']['CreatedBy']
                        if ".nodepool." in created_by or created_by == 'oke':
                            continue

            ins_fd = ins.fault_domain  # FD
            ins_id = ins.id
            tf_name = commonTools.check_tf_variable(ins_dname)
            tf_resource = f'module.instances[\\"{tf_name}\\"].oci_core_instance.instance'
            if tf_resource not in state["resources"]:
                importCommands[reg_name] += f'\n{tf_or_tofu} import "{tf_resource}" {str(ins.id)}'

            # Shape Details
            ins_shape = ins.shape
            shape_config=None

            if ('.Flex' in ins_shape or ".Micro" in ins_shape):
                #ocpu = ins.shape_config
                shape_config = ins.shape_config
                ocpus_n = str(shape_config.ocpus)
                ocpu = ocpus_n.split(".")[0]
                ins_shape = ins_shape + "::" + ocpu

            #Dedicated VM Host Details
            dedicated_host=None
            dedicated_host_id = ins.dedicated_vm_host_id  # dedicated host_name
            if(dedicated_host_id is not None):
                dedicated_host=compute.get_dedicated_vm_host(dedicated_host_id)

            # Boot Volume and its BackUp Policy Details
            boot_check = compute.list_boot_volume_attachments(availability_domain=ins_ad,
                                                          compartment_id=compartment_id,
                                                          instance_id=ins_id)
            boot_id = boot_check.data[0].boot_volume_id
            try:
                bdet = bc.get_boot_volume(boot_volume_id=boot_id).data
                boot_details = bdet.image_id
                bvp = bc.get_volume_backup_policy_asset_assignment(asset_id=boot_id)
            except oci.exceptions.ServiceError as s:
                if 'Authorization failed or requested resource not found' in s.message:
                    bdet = None
                    boot_details = ''
                    bvp = []
                    print("Skipping instance "+ins_dname +" bacause of faulty Boot Volume")
                    continue

            bkp_policy_name = ""

            cpcn = ""
            if bvp != [] and (len(bvp.data)):
                bkp_pname = bc.get_volume_backup_policy(policy_id=bvp.data[0].policy_id)
                bkp_policy_name = bkp_pname.data.display_name.title()  # backup policy name
                tf_name = commonTools.check_tf_variable(ins_dname)
                # print(bvp.data[0])
                tf_resource = f'module.instances[\\"{tf_name}\\"].oci_core_volume_backup_policy_assignment.volume_backup_policy_assignment[0]'
                if tf_resource not in state["resources"]:
                    importCommands[reg_name] += f'\n{tf_or_tofu} import "{tf_resource}" {str(bvp.data[0].id)}'
                if (bkp_pname.data.display_name not in ["Gold", "Silver", "Bronze"]):
                    bkp_policy_name = bkp_pname.data.display_name
                    for comp_name, comp_id in ct.ntk_compartment_ids.items():
                        if (bkp_pname.data.compartment_id == comp_id):
                            # print(comp_name, comp_id)
                            cpcn = comp_name

            # VNIC Details
            ins_vnic = find_vnic(ins_id, compartment_id)
            vnic_info=None
            for lnic in ins_vnic.data:
                # print(lnic)
                subnet_id = lnic.subnet_id
                vnic_id = lnic.vnic_id
                vnic_info = network.get_vnic(vnic_id=vnic_id).data

                # print(vnic_info)
                vnic_defined_tags = ""
                vnic_freeform_tags = ""
                for namespace,tagkey in vnic_info.defined_tags.items():
                    for tag,value in tagkey.items():
                        vnic_defined_tags=vnic_defined_tags+";"+namespace+"."+tag+"="+value
                        vnic_defined_tags=vnic_defined_tags.lstrip(';')

                for tag,value in vnic_info.freeform_tags.items():
                    vnic_freeform_tags=vnic_freeform_tags+";"+tag+"="+value
                    vnic_freeform_tags=vnic_freeform_tags.lstrip(';')

                #Get only primary VNIC details
                if (vnic_info.is_primary == False):
                    continue
                subnet_info = network.get_subnet(subnet_id=subnet_id)
                subnet_name = subnet_info.data.display_name
                vcn_id = subnet_info.data.vcn_id
                vcn_info = network.get_vcn(vcn_id=vcn_id)
                vcn_name = vcn_info.data.display_name
                ntk_compartment_id = network.get_vcn(subnet_info.data.vcn_id).data.compartment_id  # compartment-id
                network_compartment_name = compartment_name
                for comp_name, comp_id in ct.ntk_compartment_ids.items():
                    if comp_id == ntk_compartment_id:
                        network_compartment_name = comp_name

                vs = network_compartment_name + "@" + vcn_name + "::" + subnet_name

                #vs = vcn_name + "_" + subnet_name  # VCN + Subnet Name
                #vs = commonTools.check_tf_variable(vs)

                privateip = vnic_info.private_ip

                publicip = vnic_info.public_ip
                if (publicip == None):
                    publicip = "FALSE"
                else:
                    publicip = "TRUE"
                # Get NSG Details
                nsg_id = vnic_info.nsg_ids
                nsg_names = ""
                if (len(nsg_id)):
                    for j in nsg_id:
                        nsg_info = network.get_network_security_group(j)
                        nsg_names = nsg_names + "," + nsg_info.data.display_name
                    nsg_names = nsg_names[1:]

            key_name = ins_dname + "_" + str(privateip)
            key_name = commonTools.check_tf_variable(key_name)
            if ('ssh_authorized_keys' in ins.metadata.keys()):
                key_name = reg_name + "-" + key_name
                tf_name = commonTools.check_tf_variable(key_name)
                instance_keys[tf_name] = repr(ins.metadata['ssh_authorized_keys'])[
                                         1:-1]  # print metadata of the instance

                key_name = ins_dname + "_" + str(privateip)
                key_name = commonTools.check_tf_variable(key_name)
            else:
                key_name = reg_name + "-" + key_name
                tf_name = commonTools.check_tf_variable(key_name)
                instance_keys[tf_name] = ""
                key_name = ins_dname + "_" + str(privateip)
                key_name = ""
            if (ins.source_details.source_type == "image"):
                os = compute.get_image(image_id=boot_details)
                os_dname = os.data.display_name  # Source os name
                os_dname = commonTools.check_tf_variable(os_dname)
                tf_name = commonTools.check_tf_variable(reg_name + "-" + os_dname)
                os_keys[tf_name] = ins.source_details.image_id
                os_dname = "image::" + os_dname
            elif (ins.source_details.source_type == "bootVolume"):
                os_dname = "Boot_" + ins_dname + "_" + str(privateip)
                os_dname = commonTools.check_tf_variable(os_dname)
                tf_name = commonTools.check_tf_variable(reg_name + "-" + os_dname)
                os_keys[tf_name] = ins.source_details.boot_volume_id
                os_dname = "bootVolume::" + os_dname

            launch_options = ins.launch_options
            avail_config = ins.availability_config
            ins_options = ins.instance_options
            platform_data = ins.platform_config
            plugins_config = getattr(ins.agent_config, 'plugins_config')
            plugin_config = {}
            if plugins_config is not None:
                for item in plugins_config:
                    plugin_config[getattr(item, 'name').lower().replace(" ","_").replace("-","_")] = getattr(item, 'desired_state')

            adding_columns_values(reg_name.title(), AD_name, ins_fd, vs, publicip, privateip, os_dname,
                                  ins_shape, key_name, compartment_name, bkp_policy_name, nsg_names, dedicated_host,
                                  ins, values_for_column_instances, bdet, cpcn, shape_config, vnic_info,
                                  vnic_defined_tags, vnic_freeform_tags, launch_options,avail_config,ins_options,
                                  platform_data, plugin_config)


# Execution of the code begins here
def export_instances(inputfile, outdir, service_dir,config1, signer1, ct, export_compartments=[], export_regions=[],export_tags=[],display_names=[],ad_names=[]):
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    global instance_keys, user_data_in, os_keys, importCommands, idc, rows, AD, values_for_column_instances, df, sheet_dict_instances, config, signer,tf_or_tofu # declaring global variables

    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    config=config1
    signer=signer1

    instance_keys = {}  # dict name
    os_keys = {}  # os_ocids
    user_data_in = {}  # user data for exports

    sheetName= "Instances"
    importCommands = {}
    rows = []

    AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else ("AD2" if ("AD-2" in ad or "ad-2" in ad) else ("AD3" if ("AD-3" in ad or "ad-3" in ad) else " NULL"))  # Get shortend AD

    df, values_for_column_instances = commonTools.read_cd3(cd3file, sheetName)
    sheet_dict_instances = ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- Instances will be overwritten during this export process!!!\n")

    # Create of .sh file
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'

    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg+"/"+service_dir, resource, file_name)
        importCommands[reg] = ''

    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"], stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        for ntk_compartment_name in export_compartments:
           __get_instances_info(ntk_compartment_name, ct.ntk_compartment_ids[ntk_compartment_name], reg, display_names, ad_names,export_tags,ct,state)

    # writing image ocids and SSH keys into variables file
    var_data = {}
    for reg in export_regions:
        myocids = {}
        for keys, values in os_keys.items():
            reg_name = keys.split("-")[0]
            if (reg == reg_name):
                os_name = keys[len(reg_name) + 1:]
                myocids[os_name] = values

        mykeys = {}
        for keys, values in instance_keys.items():
            reg_name = keys.split("-")[0]
            if (reg == reg_name):
                key_name = keys[len(reg_name) + 1:]
                mykeys[key_name] = values

        file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
        # Read variables file data
        with open(file, 'r') as f:
            var_data[reg] = f.read()

        tempStrOcids = ""
        for k, v in myocids.items():
            v = "\""+v+"\""
            tempStrOcids = "\t" + k + " = " + v + "\n" + tempStrOcids

        tempStrOcids = "\n" + tempStrOcids
        tempStrOcids = "#START_instance_source_ocids#" + tempStrOcids + "\t#instance_source_ocids_END#"
        var_data[reg] = re.sub('#START_instance_source_ocids#.*?#instance_source_ocids_END#', tempStrOcids, var_data[reg],
                               flags=re.DOTALL)

        tempStrKeys = ""
        for k, v in mykeys.items():
            v = "\"" + v + "\""
            tempStrKeys = "\t" + k + " = " + v + "\n" + tempStrKeys

        tempStrKeys = "\n" + tempStrKeys
        tempStrKeys = "#START_instance_ssh_keys#" + tempStrKeys + "\t#instance_ssh_keys_END#"
        if ("\\" in tempStrKeys):
            tempStrKeys = tempStrKeys.replace("\\", "\\\\")

        var_data[reg] = re.sub('#START_instance_ssh_keys#.*?#instance_ssh_keys_END#', tempStrKeys,
                               var_data[reg],flags=re.DOTALL)

        # Write variables file data
        with open(file, "w") as f:
            f.write(var_data[reg])
        f.close()

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name

        init_commands = f'\n######### Writing import for Instances #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])

    commonTools.write_to_cd3(values_for_column_instances, cd3file, "Instances")
    print("{0} Instance Details exported into CD3.\n".format(len(values_for_column_instances["Region"])))

