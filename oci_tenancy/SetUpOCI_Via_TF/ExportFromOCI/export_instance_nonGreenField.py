#!/usr/bin/python3
# This script will export all oci instances details into cd3
# Author: Tharun Karam
# Oracle Consulting

import oci
import argparse
import sys
import oci
import re
import os

sys.path.append(os.getcwd() + "/..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


def adding_columns_values(region, hostname, ad, fd, vs, publicip, privateip, os, shape, key_name, c_name,
                          bkp_policy_name, nsgs, d_host, instance_data, values_for_column_instances, bc_info):
    for col_header in values_for_column_instances.keys():
        if (col_header == "Region"):
            values_for_column_instances[col_header].append(region)
        elif (col_header == "Hostname"):
            values_for_column_instances[col_header].append(hostname)
        elif (col_header == "Availability Domain(AD1|AD2|AD3)"):
            values_for_column_instances[col_header].append(ad)
        elif (col_header == "Fault Domain"):
            values_for_column_instances[col_header].append(fd)
        elif (col_header == "Subnet Name"):
            values_for_column_instances[col_header].append(vs)
        elif (col_header == "Pub Address"):
            values_for_column_instances[col_header].append(publicip)
        elif (col_header == "IP Address"):
            values_for_column_instances[col_header].append(privateip)
        elif (col_header == "OS"):
            values_for_column_instances[col_header].append(os)
        elif (col_header == "Shape"):
            values_for_column_instances[col_header].append(shape)
        elif (col_header == "SSH Key Var Name"):
            values_for_column_instances[col_header].append(key_name)
        elif (col_header == "Compartment Name"):
            values_for_column_instances[col_header].append(c_name)
        elif (col_header == "Backup Policy"):
            values_for_column_instances[col_header].append(bkp_policy_name)
        elif (col_header == "NSGs"):
            values_for_column_instances[col_header].append(nsgs)
        elif (col_header == "Dedicated VM Host"):
            values_for_column_instances[col_header].append(d_host)
        elif str(col_header).lower() in commonTools.tagColumns:
            values_for_column_instances = commonTools.export_tags(instance_data, col_header,
                                                                  values_for_column_instances)
        else:
            oci_objs = [instance_data, bc_info[0]]
            values_for_column_instances = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_instances,
                                                                           values_for_column_instances)


def find_boot(ins_ad, ins_id, config):
    compute = oci.core.ComputeClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    for comp in all_compartments:
        bl = compute.list_boot_volume_attachments(availability_domain=ins_ad, compartment_id=comp, instance_id=ins_id)
        if (len(bl.data)):
            return bl


def find_vnic(ins_id, config):
    network = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    compute = oci.core.ComputeClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    for comp in all_compartments:
        net = oci.pagination.list_call_get_all_results(compute.list_vnic_attachments, compartment_id=comp,
                                                       instance_id=ins_id)
        if (len(net.data)):
            return net


def __get_instances_info(compartment_name, compartment_id, reg_name, config):
    config.__setitem__("region", ct.region_dict[reg_name])
    compute = oci.core.ComputeClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    network = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    bc = oci.core.BlockstorageClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    idc = IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    instance_info = oci.pagination.list_call_get_all_results(compute.list_instances, compartment_id=compartment_id)
    # print(instance_info.data)
    for ins in instance_info.data:
        ins_details = compute.get_instance(instance_id=ins.id)
        # print(ins_details.data)
        if (ins.lifecycle_state != 'TERMINATED'):
            # print(ins)
            ins_dname = ins.display_name  # instance display name
            ins_ad = ins.availability_domain  # avalibility domain
            AD_name = AD(ins_ad)
            ins_fd = ins.fault_domain  # FD
            ins_id = ins.id
            tf_name = commonTools.check_tf_variable(ins_dname)
            importCommands[reg_name].write(
                "\nterraform import oci_core_instance." + tf_name + " " + str(ins.id))  # writing into tf file
            ins_shape = ins.shape  # Shape
            if ('Flex' in ins_shape):
                ocpu = ins.shape_config
                ocpus_n = str(ocpu.ocpus)
                ocpu = ocpus_n.split(".")[0]
                ins_shape = ins_shape + "::" + ocpu
                # print(ins_shape)
            region_code = ins.region
            dedicated_host = ins.dedicated_vm_host_id  # dedicated host_name
            if (dedicated_host == None):
                dedicated_host = ""
                # print("Dedi=",dedicated_host)
            # print(ins_dname,ins_ad,ins_fd,ins_shape)
            ins_vnic = find_vnic(ins_id, config)
            # print(ins_vnic.data)
            boot_check = find_boot(ins_ad, ins_id, config)
            boot_id = boot_check.data[0].boot_volume_id
            source_image_id = ins.source_details.image_id
            # print("Source_image=",source_image_id)
            os = compute.get_image(image_id=source_image_id)
            # print("OS",os.data)                                   #Operating system
            os_dname = os.data.display_name  # Source os name
            os_dname = commonTools.check_tf_variable(os_dname)
            tf_name = commonTools.check_tf_variable(reg_name + "-" + os_dname)
            os_keys[tf_name] = source_image_id
            # sdet=bc.get_volume(volume_id=source_image_id)
            bvp = bc.get_volume_backup_policy_asset_assignment(asset_id=boot_id)
            bvdetails = bc.get_boot_volume(boot_volume_id=boot_id)
            bkp_policy_name = ""
            if (len(bvp.data)):
                # print("Bvp Data:",bvp.data)
                bkp_pname = bc.get_volume_backup_policy(policy_id=bvp.data[0].policy_id)
                #print(bkp_pname)
                #print("BVP-DATA=",bvp.data)
                #print("bkp_data::",bkp_pname.data)
                bpolicy=ins_dname+"_bkupPolicy"
                bkp_policy_name = bkp_pname.data.display_name.title()  # backup policy name
                tf_name = commonTools.check_tf_variable(bpolicy)
                #print(bvp.data[0])
                importCommands[reg_name].write("\nterraform import oci_core_volume_backup_policy_assignment." + tf_name + " " + str(bvp.data[0].id))
            for lnic in ins_vnic.data:
                subnet_id = lnic.subnet_id
                vnic_id = lnic.vnic_id
                vnic_info = network.get_vnic(vnic_id=vnic_id)
                # print("Lnic",lnic)
                # print("Vnic_info",vnic_info.data)
                # print(vnic_id)
                subnet_info = network.get_subnet(subnet_id=subnet_id)
                subnet_name = subnet_info.data.display_name
                vcn_id = subnet_info.data.vcn_id
                vcn_info = network.get_vcn(vcn_id=vcn_id)
                vcn_name = vcn_info.data.display_name
                privateip = vnic_info.data.private_ip
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
                publicip = vnic_info.data.public_ip
                if (publicip == None):
                    publicip = "FALSE"
                else:
                    publicip = "TRUE"
                nsg_id = vnic_info.data.nsg_ids
                nsg_names = ""
                if (len(nsg_id)):
                    for j in nsg_id:
                        nsg_info = network.get_network_security_group(j)
                        nsg_names = nsg_names + "," + nsg_info.data.display_name
                    nsg_names = nsg_names[1:]
                vs = vcn_name + "_" + subnet_name  # VCN + Subnet Name
                adding_columns_values(reg_name.title(), ins_dname, AD_name, ins_fd, vs, publicip, privateip, os_dname,
                                      ins_shape, key_name, compartment_name, bkp_policy_name, nsg_names, dedicated_host,
                                      ins, values_for_column_instances, boot_check.data)
                # rows.append(new_row)


def main():
    parser = argparse.ArgumentParser(description="Export FSS Details on OCI to CD3")
    parser.add_argument("cd3file", help="path of CD3 excel file to export Instance objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--configFileName", help="Config file name")
    parser.add_argument("--networkCompartment",
                        help="comma seperated Compartments for which to export Instance Objects")

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    cd3file = args.cd3file
    outdir = args.outdir
    input_compartment_list = args.networkCompartment

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    if args.configFileName is not None:
        configFileName = args.configFileName
        config = oci.config.from_file(file_location=configFileName)
    else:
        config = oci.config.from_file()

    global instance_keys, os_keys, all_regions, ct, importCommands, idc, rows, all_compartments, AD, values_for_column_instances, df, sheet_dict_instances  # declaring global variables

    instance_keys = {}  # dict name
    os_keys = {}  # os_ocids
    all_regions = []
    ct = commonTools()
    importCommands = {}
    idc = IdentityClient(config)
    rows = []
    all_compartments = []

    AD = lambda ad: "AD1" if ("AD-1" in ad) else (
        "AD2" if ("AD-2" in ad) else ("AD3" if ("AD-3" in ad) else "NULL"))  # Get shortend AD

    df, values_for_column_instances = commonTools.read_cd3(cd3file, "Instances")
    sheet_dict_instances = ct.sheet_dict["Instances"]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs Instances will be overwritten during this export process!!!\n")

    # Load os_ocids template file
    file_loader = FileSystemLoader('../templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('variables-template')

    # Load ssh_metadata template file
    file_loader2 = FileSystemLoader('../templates')
    env2 = Environment(loader=file_loader2, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template2 = env.get_template('variables-template')

    # Fetch Regions
    regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])
    for rs in regionsubscriptions.data:
        for k, v in ct.region_dict.items():
            if (rs.region_name == v):
                all_regions.append(k)

    comps = oci.pagination.list_call_get_all_results(idc.list_compartments, compartment_id=config['tenancy'],
                                                     compartment_id_in_subtree=True)
    for comp_info in comps.data:
        if (comp_info.lifecycle_state == "ACTIVE"):
            all_compartments.append(comp_info.id)

    # Create of .sh file
    for reg in all_regions:
        resource = ' tf_import_instances'
        srcdir = outdir + "/" + reg + "/"
        if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_instances_nonGF.sh")):
            commonTools.backup_file(srcdir, resource, "tf_import_commands_instances_nonGF.sh")
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_instances_nonGF.sh", "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    if (input_compartment_list is not None):
        print("Fetching for Compartments... " + input_compartment_list)
        input_compartment_names = input_compartment_list.split(",")
        input_compartment_names = [x.strip() for x in input_compartment_names]
        comps = oci.pagination.list_call_get_all_results(idc.list_compartments, compartment_id=config['tenancy'],
                                                         compartment_id_in_subtree=True)
        for reg_name in all_regions:
            # importCommands[reg_name] = open(outdir + "/" + reg_name + "/tf_import_commands_instances_nonGF.sh", "w")
            config.__setitem__("region", ct.region_dict[reg_name])
            for comp in comps.data:
                if (comp.lifecycle_state == "ACTIVE"):
                    comp_info = comp
                    compartment_id = comp_info.id
                    compartment_name = comp.name
                    if (compartment_name in input_compartment_names):
                        # print("##Checking Instances in region "+str(reg_name)+ " - "+ compartment_name +" compartment_name ")
                        __get_instances_info(compartment_name, compartment_id, reg_name, config)

    else:
        print("Fetching for all Compartments...")
        input_compartment_names = None
        comps = oci.pagination.list_call_get_all_results(idc.list_compartments, compartment_id=config['tenancy'],
                                                         compartment_id_in_subtree=True)
        for reg_name in all_regions:
            # importCommands[reg_name] = open(outdir + "/" + reg_name + "/tf_import_commands_instances_nonGF.sh", "w")
            config.__setitem__("region", ct.region_dict[reg_name])
            for comp in comps.data:
                if (comp.lifecycle_state == "ACTIVE"):
                    comp_info = comp
                    compartment_id = comp_info.id
                    compartment_name = comp.name
                    __get_instances_info(compartment_name, compartment_id, reg_name, config)

    # writing ocids values into os_ocids.tf
    for reg in all_regions:
        myocids = {}
        for keys, values in os_keys.items():
            reg_name = keys.split("-")[0]
            if (reg == reg_name):
                os_name = keys[len(reg_name) + 1:]
                myocids[os_name] = values
        # print(myocids)
        f = open(outdir + "/" + reg + "/os_ocids.tf", "w")
        for keys, values in myocids.items():
            tempstr = {"var_tf_name": keys, "values": values}
            temp_str_test = template.render(tempstr)
            # str="variable \""+keys+"\" {\n type    = \"string\"\n default = \""+values+"\" \n }\n"
            f.write(temp_str_test)
        f.close()
    tempstr = {}
    # writing ssh_keys_metadata into ssh_metadata
    for reg in all_regions:
        myocids = {}
        for keys, values in instance_keys.items():
            reg_name = keys.split("-")[0]
            if (reg == reg_name):
                key_name = keys[len(reg_name) + 1:]
                myocids[key_name] = values
        # print(myocids)
        f = open(outdir + "/" + reg + "/ssh_metadata.tf", "w")
        for keys, values in myocids.items():
            tempstr = {"var_tf_name": keys, "values": values}
            # str="variable \""+keys+"\" {\n type    = \"string\"\n default = \""+values+"\" \n }\n"
            temp_str_test = template2.render(tempstr)
            f.write(temp_str_test)
        f.close()

    # write data into file
    for reg in all_regions:
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_instances_nonGF.sh", "a")
        importCommands[reg].write("\n\nterraform plan")
        importCommands[reg].write("\n")
        importCommands[reg].close()
        if ("linux" in sys.platform):
            dir = os.getcwd()
            os.chdir(outdir + "/" + reg)
            os.system("chmod +x tf_import_commands_instances_nonGF.sh")
            os.chdir(dir)

    commonTools.write_to_cd3(values_for_column_instances, cd3file, "Instances")
    print("{0} Instance Details exported into CD3.\n".format(len(values_for_column_instances["Region"])))


if __name__ == '__main__':
    # Execution of the code begins here
    main()
