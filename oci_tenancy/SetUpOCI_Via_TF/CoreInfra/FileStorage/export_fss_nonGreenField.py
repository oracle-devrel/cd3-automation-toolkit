#!/usr/bin/python3
# Author: Tharun Karam
# Exporting Filesystems into cd3
# Oracle Consulting.

import argparse
import sys
import oci
import re
import os
from oci.identity import IdentityClient
from oci.config import DEFAULT_LOCATION
from commonTools import *


def add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes, files, fs_name,
                    einfo_path, sourceCIDR, Access, GID, UID, IDSquash, require_ps_port, fsinfo, values_for_column_fss,
                    mnt_info1, nsg_n):

    for col_header in values_for_column_fss.keys():
        if (col_header == "Region"):
            values_for_column_fss[col_header].append(reg)
        elif (col_header == "Compartment Name"):
            values_for_column_fss[col_header].append(cname)
        elif (col_header == "Availability Domain(AD1|AD2|AD3)"):
            values_for_column_fss[col_header].append(AD_name)
        elif (col_header == "MountTarget Name"):
            values_for_column_fss[col_header].append(mt_display_name)
        elif (col_header == "MountTarget SubnetName"):
            values_for_column_fss[col_header].append(vplussubnet)
        elif (col_header == "MountTarget IP"):
            values_for_column_fss[col_header].append(mnt_p_ip)
        elif (col_header == "MountTarget Hostname"):
            values_for_column_fss[col_header].append(mnt_p_hostname)
        elif (col_header == "FSS Name"):
            values_for_column_fss[col_header].append(fs_name)
        elif (col_header == "Path"):
            values_for_column_fss[col_header].append(einfo_path)
        elif (col_header == "Source CIDR"):
            values_for_column_fss[col_header].append(sourceCIDR)
        elif (col_header == "Access (READ_ONLY|READ_WRITE)"):
            values_for_column_fss[col_header].append(Access)
        elif (col_header == "GID"):
            values_for_column_fss[col_header].append(GID)
        elif (col_header == "NSGs"):
            values_for_column_fss[col_header].append(nsg_n)
        elif (col_header == "UID"):
            values_for_column_fss[col_header].append(UID)
        elif (col_header == "IDSquash (NONE|ALL|ROOT)"):
            values_for_column_fss[col_header].append(IDSquash)
        elif (col_header == "Require PS Port (true|false)"):
            values_for_column_fss[col_header].append(require_ps_port)
        elif str(col_header).lower() in commonTools.tagColumns:
            values_for_column_fss = commonTools.export_tags(fsinfo.data, col_header, values_for_column_fss)
        else:
            oci_objs = [fsinfo.data, mnt_info1]
            values_for_column_fss = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_instances,
                                                                     values_for_column_fss)


def __get_mount_info(cname, compartment_id, reg, availability_domain_name, config):
    file_system = oci.file_storage.FileStorageClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    network = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    vnc_info = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    global exports_ids
    AD_name = AD(availability_domain_name)
    try:
        mount_info = oci.pagination.list_call_get_all_results(file_system.list_mount_targets,
                                                              compartment_id=compartment_id,
                                                              availability_domain=availability_domain_name)
        fss = []
        for mnt in mount_info.data:
            mnt_id = mnt.id
            export_set_id = mnt.export_set_id  # Export Set Id
            mt_display_name = mnt.display_name  # Mount Target Name
            tf_name = commonTools.check_tf_variable(mt_display_name)
            importCommands[reg].write("\nterraform import oci_file_storage_mount_target." + tf_name + " " + str(mnt_id))
            subnet_id = mnt.subnet_id
            private_ip_ids = mnt.private_ip_ids
            nsg_id = mnt.nsg_ids
            nsg_names = ""
            if (len(nsg_id)):
                for j in nsg_id:
                    nsg_info = network.get_network_security_group(j)
                    nsg_names = nsg_names + "," + nsg_info.data.display_name
                nsg_names = nsg_names[1:]
            subnet_info = vnc_info.get_subnet(subnet_id)
            mnt_sub_name = subnet_info.data.display_name  # Subnet-Name
            vnc_name = vnc_info.get_vcn(subnet_info.data.vcn_id).data.display_name  # vcn-Name
            vplussubnet = vnc_name + "_" + mnt_sub_name
            vplussubnet =  commonTools.check_tf_variable(vplussubnet)
            for ips in private_ip_ids:
                private_address = vnc_info.get_private_ip(ips)
                mnt_p_ip = private_address.data.ip_address  # Private IP
                mnt_p_hostname = private_address.data.hostname_label
            export_set_info = file_system.get_export_set(export_set_id=export_set_id)
            # tf_name = commonTools.check_tf_variable(mt_display_name+"-"+"ES")
            # importCommands[reg].write("\nterraform import oci_file_storage_export_set." + tf_name + " " + str(export_set_id))
            es_details = file_system.get_export_set(export_set_id=export_set_id)
            bytes = (str(es_details.data.max_fs_stat_bytes))
            files = (str(es_details.data.max_fs_stat_files))
            export_info = oci.pagination.list_call_get_all_results(file_system.list_exports,
                                                                   export_set_id=export_set_id)
            file_system_info = ""
            for einfo in export_info.data:
                einfo_path = einfo.path  # Export Path Name
                einfo_id = einfo.id
                einfo_export = file_system.get_export(export_id=einfo.id)
                einfo_export_data = einfo_export.data  # exports info
                # print("Export_Path:",einfo_path)
                fs_id = einfo.file_system_id
                file_system_info = file_system.get_file_system(file_system_id=fs_id)
                # print(file_system_info.data)
                fs_name = file_system_info.data.display_name  # FileSystemName
                tf_name = commonTools.check_tf_variable(fs_name)
                if (str(fs_id) not in fss):
                    # print(mt_display_name,"-",str(fs_name))
                    tf_name = commonTools.check_tf_variable(fs_name)
                    importCommands[reg].write(
                        "\nterraform import oci_file_storage_file_system." + tf_name + " " + str(fs_id))
                    fss.append(str(fs_id))
                elen = (len(einfo_export_data.export_options))
                if (elen == 0):
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,fs_name,einfo_path,"","","","","","")
                    add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes,
                                    files, fs_name, einfo_path, sourceCIDR="", Access="", GID="", UID="", IDSquash="",
                                    require_ps_port="", fsinfo=file_system_info,
                                    values_for_column_fss=values_for_column_fss, mnt_info1=mnt, nsg_n=nsg_names)
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,bytes,files,fs_name,einfo_path,"","","","","","")
                    # rows.append(new_row)
                if (elen == 1 or elen > 1):
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,fs_name,einfo_path,einfo_export_data.export_options[0].source,einfo_export_data.export_options[0].access,einfo_export_data.export_options[0].anonymous_gid,einfo_export_data.export_options[0].anonymous_uid,einfo_export_data.export_options[0].identity_squash,einfo_export_data.export_options[0].require_privileged_source_port)
                    add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes,
                                    files, fs_name, einfo_path, einfo_export_data.export_options[0].source,
                                    einfo_export_data.export_options[0].access,
                                    einfo_export_data.export_options[0].anonymous_gid,
                                    einfo_export_data.export_options[0].anonymous_uid,
                                    einfo_export_data.export_options[0].identity_squash,
                                    einfo_export_data.export_options[0].require_privileged_source_port,
                                    fsinfo=file_system_info, values_for_column_fss=values_for_column_fss, mnt_info1=mnt,
                                    nsg_n=nsg_names)
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,bytes,files,fs_name,einfo_path,einfo_export_data.export_options[0].source,einfo_export_data.export_options[0].access,einfo_export_data.export_options[0].anonymous_gid,einfo_export_data.export_options[0].anonymous_uid,einfo_export_data.export_options[0].identity_squash,einfo_export_data.export_options[0].require_privileged_source_port)
                    # rows.append(new_row)
                if (elen > 1):
                    for rw in range(1, elen):
                        add_column_data("", "", "", "", "", "", "", "", "", "", einfo_path,
                                        einfo_export_data.export_options[rw].source,
                                        einfo_export_data.export_options[rw].access,
                                        einfo_export_data.export_options[rw].anonymous_gid,
                                        einfo_export_data.export_options[rw].anonymous_uid,
                                        einfo_export_data.export_options[rw].identity_squash,
                                        einfo_export_data.export_options[rw].require_privileged_source_port,
                                        fsinfo=file_system_info, values_for_column_fss=values_for_column_fss,
                                        mnt_info1=mnt, nsg_n=nsg_names)
                        # new_row=("","","","","","","","","","",einfo_path,einfo_export_data.export_options[rw].source,einfo_export_data.export_options[rw].access,einfo_export_data.export_options[rw].anonymous_gid,einfo_export_data.export_options[rw].anonymous_uid,einfo_export_data.export_options[rw].identity_squash,einfo_export_data.export_options[rw].require_privileged_source_port)
                        # rows.append(new_row)
                tf_name = commonTools.check_tf_variable("FSE-" + commonTools.check_tf_variable(mt_display_name) + "-" + commonTools.check_tf_variable(fs_name) + "-" + einfo_path[1:])
                importCommands[reg].write(
                    "\nterraform import oci_file_storage_export." + tf_name + " " + str(einfo.id))  # exports import
    except Exception as e:
        pass


def parse_args():
    parser = argparse.ArgumentParser(description="Export FSS Details on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export FileSystem objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--network-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export FileSystem Objects")
    return parser.parse_args()


def export_fss(inputfile, outdir, network_compartments=[], config=DEFAULT_LOCATION):
    input_compartment_names = network_compartments
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    configFileName = config
    config = oci.config.from_file(file_location=configFileName)

    global idc, compute, file_system, ct, vnc_info, importCommands, rows, all_regions, all_ads, all_compartments, input_compartment_list, AD, df, values_for_column_fss, sheet_dict_instances

    idc = IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    compute = oci.core.ComputeClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    file_system = oci.file_storage.FileStorageClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    ct = commonTools()
    vnc_info = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    importCommands = {}
    rows = []
    all_regions = []
    all_ads = []
    all_compartments = []
    input_compartment_list = network_compartments
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs FSS will be overwritten during this export process!!!\n")

    AD = lambda ad: "AD1" if ("AD-1" in ad) else (
        "AD2" if ("AD-2" in ad) else ("AD3" if ("AD-3" in ad) else "NULL"))  # Get shortend AD

    df, values_for_column_fss = commonTools.read_cd3(cd3file, "FSS")
    sheet_dict_instances = ct.sheet_dict["FSS"]

    # Fetch Regions
    regionsubscriptions = idc.list_region_subscriptions(tenancy_id=config['tenancy'])
    for rs in regionsubscriptions.data:
        for k, v in ct.region_dict.items():
            if (rs.region_name == v):
                all_regions.append(k)

    # Fetch all ADs in all Subscribed Regions
    for reg in all_regions:
        config.__setitem__("region", ct.region_dict[reg])
        ads = oci.identity.IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
            all_ads.append(aval.name)

    # backup of .sh file
    for reg in all_regions:
        resource = ' tf_import_fss'
        srcdir = outdir + "/" + reg + "/"
        if (os.path.exists(outdir + "/" + reg + "/tf_import_commands_fss_nonGF.sh")):
            commonTools.backup_file(srcdir, resource, "tf_import_commands_fss_nonGF.sh")
        importCommands[reg] = open(outdir + "/" + reg + "/tf_import_commands_fss_nonGF.sh", "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Check Compartments
    remove_comps = []
    if (input_compartment_names is not None):
        for x in range(0, len(input_compartment_names)):
            if (input_compartment_names[x] not in ct.ntk_compartment_ids.keys()):
                print("Input compartment: " + input_compartment_names[x] + " doesn't exist in OCI")
                remove_comps.append(input_compartment_names[x])

        input_compartment_names = [x for x in input_compartment_names if x not in remove_comps]
        if (len(input_compartment_names) == 0):
            print("None of the input compartments specified exist in OCI..Exiting!!!")
            exit(1)
        else:
            print("Fetching for Compartments... " + str(input_compartment_names))
            for compartment_name in input_compartment_names:
                for reg in all_regions:
                  config.__setitem__("region", ct.region_dict[reg])
                  ads=oci.identity.IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
                  for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
                    __get_mount_info(compartment_name,ct.ntk_compartment_ids[compartment_name],reg,aval.name,config)
    else:
        print("Fetching for all Compartments...")
        comp_ocid_done=[]
        for ntk_compartment_name in ct.ntk_compartment_ids:
            if ct.ntk_compartment_ids[ntk_compartment_name] not in comp_ocid_done:
                if (input_compartment_names is not None and ntk_compartment_name not in input_compartment_names):
                    continue
                comp_ocid_done.append(ct.ntk_compartment_ids[ntk_compartment_name])
        uc={}                                   #compartment names with hierarchy
        for cid in comp_ocid_done:
            for cname,cocid in ct.ntk_compartment_ids.items():
               if cocid == cid and "::" in cname:
                  uc[cname]=cocid
                  continue
               if cocid == cid:
                 if cocid not in uc.values():
                    uc[cname]=cocid
        for comp_name,comp_ocid in uc.items():
            for reg in all_regions:
               config.__setitem__("region", ct.region_dict[reg])
               ads=oci.identity.IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
               for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
                 __get_mount_info(comp_name,comp_ocid,reg,aval.name,config)


    commonTools.write_to_cd3(values_for_column_fss, cd3file, "FSS")
    print("FSS objects exported to CD3.\n")

    # writing data
    for reg in all_regions:
        script_file = f'{outdir}/{reg}/tf_import_commands_fss_nonGF.sh'
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
        if "linux" in sys.platform:
            os.chmod(script_file, 0o755)


if __name__ == "__main__":
    args = parse_args()
    export_fss(args.inputfile, args.outdir, args.network_compartments, args.config)
