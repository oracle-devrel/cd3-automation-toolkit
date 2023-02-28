#!/usr/bin/python3
# Author: Tharun Karam
# Exporting Filesystems into cd3
# Oracle Consulting.

import argparse
import oci
import os
from oci.config import DEFAULT_LOCATION
from commonTools import *


def add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes, files, fs_name,
                    einfo_path, sourceCIDR, Access, GID, UID, IDSquash, require_ps_port, fsinfo, values_for_column_fss,
                    mnt_info1, nsg_n):

    for col_header in values_for_column_fss.keys():
        if (col_header == "Region"):
            values_for_column_fss[col_header].append(reg.capitalize())
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
            importCommands[reg].write("\nterraform import \"module.mts[\\\"" + tf_name + "\\\"].oci_file_storage_mount_target.mount_target\" " + str(mnt_id))
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

            for ips in private_ip_ids:
                private_address = vnc_info.get_private_ip(ips)
                mnt_p_ip = private_address.data.ip_address  # Private IP
                mnt_p_hostname = private_address.data.hostname_label
            export_set_info = file_system.get_export_set(export_set_id=export_set_id)

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
                        "\nterraform import \"module.fss[\\\"" + tf_name + "\\\"].oci_file_storage_file_system.file_system\" " + str(fs_id))
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
                importCommands[reg].write("\nterraform import \"module.fss-export-options[\\\"" + tf_name + "\\\"].oci_file_storage_export.export\" " + str(einfo.id))  # exports import
    except Exception as e:
        pass


def parse_args():
    parser = argparse.ArgumentParser(description="Export FSS Details on OCI to CD3")
    parser.add_argument("inputfile", help="path of CD3 excel file to export FileSystem objects to")
    parser.add_argument("outdir", help="path to out directory containing script for TF import commands")
    parser.add_argument("--config", default=DEFAULT_LOCATION, help="Config file name")
    parser.add_argument("--export-compartments", nargs='*', required=False, help="comma seperated Compartments for which to export FileSystem Objects")
    parser.add_argument("--export-regions", nargs='*', help="comma seperated Regions for which to export Networking Objects",
                        required=False)
    return parser.parse_args()


def export_fss(inputfile, outdir, service_dir, ct, config=DEFAULT_LOCATION, export_compartments=[], export_regions=[]):
    input_compartment_names = export_compartments
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "FSS"
    configFileName = config
    config = oci.config.from_file(file_location=configFileName)

    global file_system, vnc_info, importCommands, rows,  all_ads, input_compartment_list, AD, df, values_for_column_fss, sheet_dict_instances

    file_system = oci.file_storage.FileStorageClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    if ct==None:
        ct = commonTools()
        ct.get_subscribedregions(configFileName)
        ct.get_network_compartment_ids(config['tenancy'], "root", configFileName)

    vnc_info = oci.core.VirtualNetworkClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
    importCommands = {}
    rows = []
    all_ads = []
    
    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs FSS will be overwritten during this export process!!!\n")

    AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else (
        "AD2" if ("AD-2" in ad or "ad-2" in ad) else ("AD3" if ("AD-3" in ad or "ad-3" in ad) else "NULL"))  # Get shortend AD

    df, values_for_column_fss = commonTools.read_cd3(cd3file, sheetName)
    sheet_dict_instances = ct.sheet_dict[sheetName]

    # Fetch all ADs in all Subscribed Regions
    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        ads = oci.identity.IdentityClient(config,retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
        for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
            all_ads.append(aval.name)

    # backup of .sh file
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir + "/", resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        for ntk_compartment_name in export_compartments:
            ads = oci.identity.IdentityClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY)
            for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
                __get_mount_info(ntk_compartment_name, ct.ntk_compartment_ids[ntk_compartment_name], reg, aval.name, config)


    commonTools.write_to_cd3(values_for_column_fss, cd3file, sheetName)
    print("FSS objects exported to CD3.\n")

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')

if __name__ == "__main__":
    args = parse_args()
    export_fss(args.inputfile, args.outdir, args.config, args.export_compartments, args.export_regions)

