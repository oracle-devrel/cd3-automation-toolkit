#!/usr/bin/python3
# Author: Tharun Karam
# Exporting Filesystems into cd3
# Updated by: Mukesh Patel
# Oracle Consulting.

import oci
import os
import re
from oci.config import DEFAULT_LOCATION
from commonTools import *
import subprocess as sp

fs_source_snapshots = {}
fss_all_dict = {}
def add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes, files, fs_name,
                    einfo_path, fs_source_snapshot_id, fs_snapshot_policy_id, fss_replication, is_ldap_groups_enabled,
                    sourceCIDR, Access, GID, UID, IDSquash, require_ps_port, allowed_auth, is_anonymous_access_allowed,
                    fsinfo, values_for_column_fss,
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
        elif (col_header == "Network Details"):
            values_for_column_fss[col_header].append(vplussubnet)
        elif (col_header == "MountTarget IP"):
            values_for_column_fss[col_header].append(mnt_p_ip)
        elif (col_header == "MountTarget Hostname"):
            values_for_column_fss[col_header].append(mnt_p_hostname)
        elif (col_header == "FSS Name"):
            values_for_column_fss[col_header].append(fs_name)
        elif (col_header == "Source Snapshot"):
            if fs_source_snapshot_id != None:
                values_for_column_fss[col_header].append(fs_source_snapshot_id)
            else:
                values_for_column_fss[col_header].append('')
        elif (col_header == "Snapshot Policy"):
            if fs_snapshot_policy_id != '':
                values_for_column_fss[col_header].append(fs_snapshot_policy_id)
            else:
                values_for_column_fss[col_header].append('')
        elif (col_header == "Replication Information"):
            if fss_replication != '':
                values_for_column_fss[col_header].append(fss_replication)
            else:
                values_for_column_fss[col_header].append('')
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
        elif (commonTools.check_column_headers(col_header) == "is_anonymous_access_allowed"):
            values_for_column_fss[col_header].append(is_anonymous_access_allowed)
        elif (commonTools.check_column_headers(col_header) == "is_idmap_groups_for_sys_auth"):
            values_for_column_fss[col_header].append(is_ldap_groups_enabled)
        elif (col_header == "Allowed Auth"):
            if len(allowed_auth) == 1:
                allowed_auth = allowed_auth[0].strip()
                values_for_column_fss[col_header].append(allowed_auth)
            elif len(allowed_auth) > 1:
                tmp_auth = ""
                for auth in allowed_auth:
                    tmp_auth = tmp_auth + auth.strip() + ','
                tmp_auth = tmp_auth.removesuffix(',')
                values_for_column_fss[col_header].append(tmp_auth)
            else:
                values_for_column_fss[col_header].append('')
        elif str(col_header).lower() in commonTools.tagColumns:
            values_for_column_fss = commonTools.export_tags(fsinfo.data, col_header, values_for_column_fss)
        else:
            oci_objs = [fsinfo.data, mnt_info1,einfo_path]
            values_for_column_fss = commonTools.export_extra_columns(oci_objs, col_header, sheet_dict_instances,
                                                                     values_for_column_fss)


def __get_mount_info(cname, ntk_compartment_ids, compartment_id, reg, availability_domain_name, signer,state):
    file_system = oci.file_storage.FileStorageClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                     signer=signer)
    network = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
    vnc_info = oci.core.VirtualNetworkClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
    global exports_ids
    AD_name = AD(availability_domain_name)

    try:
        mount_info = oci.pagination.list_call_get_all_results(file_system.list_mount_targets,
                                                              compartment_id=compartment_id,
                                                              availability_domain=availability_domain_name,sort_by="TIMECREATED")
        list_replications = oci.pagination.list_call_get_all_results(file_system.list_replications,
                                                                     compartment_id=compartment_id,
                                                                     availability_domain=availability_domain_name,sort_by="timeCreated")
        list_fss = oci.pagination.list_call_get_all_results(file_system.list_file_systems,
                                                            compartment_id=compartment_id,availability_domain=availability_domain_name,sort_by="TIMECREATED")
        for fss in list_fss.data:
            fss_all_dict[fss.id] = fss.display_name
        replications_dict = {}
        for rep_data in list_replications.data:
            rep_info = file_system.get_replication(replication_id=rep_data.id)
            tmp_dict = {}
            tmp_dict[rep_info.data.id] = {'sourceid': rep_info.data.source_id, 'targetid': rep_info.data.target_id,
                                          'interval': rep_info.data.replication_interval,
                                          'displayname': rep_info.data.display_name}
            replications_dict.update(tmp_dict)
        fss = []
        mnt_fss_ids = []
        rep_ids = []
        mnt_info_dict = {}
        mnt_with_export = []
        for mnt in mount_info.data:
            mnt_id = str(mnt.id)
            export_set_id = mnt.export_set_id  # Export Set Id
            mt_display_name = mnt.display_name  # Mount Target Name
            tf_name = commonTools.check_tf_variable(mt_display_name)
            tf_resource = f'module.mts[\\"{tf_name}\\"].oci_file_storage_mount_target.mount_target'
            if tf_resource not in state["resources"]:
                importCommands[reg]+=f'\n{tf_or_tofu} import "{tf_resource}" {mnt_id}'
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
            ntk_compartment_id = vnc_info.get_vcn(subnet_info.data.vcn_id).data.compartment_id # compartment-id
            network_compartment_name=cname
            for comp_name, comp_id in ntk_compartment_ids.items():
                if comp_id == ntk_compartment_id:
                    network_compartment_name = comp_name


            vplussubnet = network_compartment_name+"@"+vnc_name + "::" + mnt_sub_name

            for ips in private_ip_ids:
                private_address = vnc_info.get_private_ip(ips)
                mnt_p_ip = private_address.data.ip_address  # Private IP
                mnt_p_hostname = private_address.data.hostname_label
            export_set_info = file_system.get_export_set(export_set_id=export_set_id)

            mnt_info_dict[mnt_id] = {'name': mt_display_name, 'nsg': nsg_names, 'network': vplussubnet, 'ip': mnt_p_ip, 'hostname': mnt_p_hostname}
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
                mnt_fss_ids.append(fs_id)
                if mnt_id not in mnt_with_export:
                    mnt_with_export.append(mnt_id)
                file_system_info = file_system.get_file_system(file_system_id=fs_id)
                fs_name = file_system_info.data.display_name  # FileSystemName
                snapshot_id = file_system_info.data.source_details.source_snapshot_id
                if snapshot_id == '':
                    fs_source_snapshot_id = ''
                else:
                    tmp_source = reg + "--" + fs_name + "--" + snapshot_id
                    fs_source_snapshots[tmp_source] = snapshot_id
                    fs_source_snapshot_id = fs_name
                fs_snapshot_policy_id = file_system_info.data.filesystem_snapshot_policy_id
                if fs_snapshot_policy_id != '':
                    policy_comp_name=cname
                    snapshot_policy_info = file_system.get_filesystem_snapshot_policy(filesystem_snapshot_policy_id=fs_snapshot_policy_id)
                    policy_name = snapshot_policy_info.data.display_name
                    policy_comp_id = snapshot_policy_info.data.compartment_id
                    for comp_name, comp_id in ntk_compartment_ids.items():
                        if comp_id == policy_comp_id:
                            policy_comp_name = comp_name
                    fs_snapshot_policy_id = policy_comp_name + "@" + policy_name
                is_ldap_groups_enabled = einfo.is_idmap_groups_for_sys_auth
                fss_replication = ""
                if len(replications_dict) > 0:
                    for k, v in replications_dict.items():
                        if v['sourceid'] == fs_id:
                            targetid = v['targetid']
                            for id,name in fss_all_dict.items():
                                if id == v['targetid']:
                                    targetid = name
                                else:
                                    targetid = v['targetid']

                            rep_format = targetid + "::" + str(v['interval']) + "::" + v['displayname']
                            fss_replication = fss_replication + rep_format + '\n'
                tf_name = commonTools.check_tf_variable(fs_name)
                if (str(fs_id) not in fss):
                    # print(mt_display_name,"-",str(fs_name))
                    tf_name = commonTools.check_tf_variable(fs_name)
                    tf_resource = f'module.fss[\\"{tf_name}\\"].oci_file_storage_file_system.file_system'
                    if tf_resource not in state["resources"]:
                        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {fs_id}'

                    fss.append(str(fs_id))
                if len(replications_dict) > 0:
                    for k, v in replications_dict.items():
                        if v['sourceid'] == fs_id:
                            if (str(k) not in rep_ids):
                                tf_rep_name = commonTools.check_tf_variable(v['displayname'].strip())
                                tf_resource = f'module.fss-replication[\\"{tf_rep_name}\\"].oci_file_storage_replication.file_system_replication'
                                if tf_resource not in state["resources"]:
                                    importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {str(k)}'
                                rep_ids.append(str(k))

                elen = (len(einfo_export_data.export_options))
                if (elen == 0):
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,fs_name,einfo_path,"","","","","","")
                    add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes,
                                    files, fs_name, einfo_path, fs_source_snapshot_id, fs_snapshot_policy_id,
                                    fss_replication, is_ldap_groups_enabled, sourceCIDR="", Access="", GID="", UID="",
                                    IDSquash="",
                                    require_ps_port="", allowed_auth="", is_anonymous_access_allowed="",
                                    fsinfo=file_system_info,
                                    values_for_column_fss=values_for_column_fss, mnt_info1=mnt, nsg_n=nsg_names)
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,bytes,files,fs_name,einfo_path,"","","","","","")
                    # rows.append(new_row)
                if (elen == 1 or elen > 1):
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,fs_name,einfo_path,einfo_export_data.export_options[0].source,einfo_export_data.export_options[0].access,einfo_export_data.export_options[0].anonymous_gid,einfo_export_data.export_options[0].anonymous_uid,einfo_export_data.export_options[0].identity_squash,einfo_export_data.export_options[0].require_privileged_source_port)
                    add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, bytes,
                                    files, fs_name, einfo_path, fs_source_snapshot_id, fs_snapshot_policy_id,
                                    fss_replication, is_ldap_groups_enabled, einfo_export_data.export_options[0].source,
                                    einfo_export_data.export_options[0].access,
                                    einfo_export_data.export_options[0].anonymous_gid,
                                    einfo_export_data.export_options[0].anonymous_uid,
                                    einfo_export_data.export_options[0].identity_squash,
                                    einfo_export_data.export_options[0].require_privileged_source_port,
                                    einfo_export_data.export_options[0].allowed_auth,
                                    einfo_export_data.export_options[0].is_anonymous_access_allowed,
                                    fsinfo=file_system_info, values_for_column_fss=values_for_column_fss, mnt_info1=mnt,
                                    nsg_n=nsg_names)
                    # new_row=(reg,cname,AD_name,mt_display_name,vplussubnet,mnt_p_ip,mnt_p_hostname,bytes,files,fs_name,einfo_path,einfo_export_data.export_options[0].source,einfo_export_data.export_options[0].access,einfo_export_data.export_options[0].anonymous_gid,einfo_export_data.export_options[0].anonymous_uid,einfo_export_data.export_options[0].identity_squash,einfo_export_data.export_options[0].require_privileged_source_port)
                    # rows.append(new_row)
                if (elen > 1):
                    for rw in range(1, elen):
                        add_column_data("", "", "", "", "", "", "", "", "", "", einfo_path, "", "", "", "",
                                        einfo_export_data.export_options[rw].source,
                                        einfo_export_data.export_options[rw].access,
                                        einfo_export_data.export_options[rw].anonymous_gid,
                                        einfo_export_data.export_options[rw].anonymous_uid,
                                        einfo_export_data.export_options[rw].identity_squash,
                                        einfo_export_data.export_options[rw].require_privileged_source_port,
                                        einfo_export_data.export_options[rw].allowed_auth,
                                        einfo_export_data.export_options[rw].is_anonymous_access_allowed,
                                        fsinfo=file_system_info, values_for_column_fss=values_for_column_fss,
                                        mnt_info1=mnt, nsg_n=nsg_names)
                        # new_row=("","","","","","","","","","",einfo_path,einfo_export_data.export_options[rw].source,einfo_export_data.export_options[rw].access,einfo_export_data.export_options[rw].anonymous_gid,einfo_export_data.export_options[rw].anonymous_uid,einfo_export_data.export_options[rw].identity_squash,einfo_export_data.export_options[rw].require_privileged_source_port)
                        # rows.append(new_row)
                tf_name = commonTools.check_tf_variable(
                    "FSE-" + commonTools.check_tf_variable(mt_display_name) + "-" + commonTools.check_tf_variable(
                        fs_name) + "-" + einfo_path[1:])
                tf_resource = f'module.fss-export-options[\\"{tf_name}\\"].oci_file_storage_export.export'
                if tf_resource not in state["resources"]:
                    importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {str(einfo.id)}'


        ###### code to fetch FSS without any exports #####
        fss_all_ids = []
        for fss_all in list_fss.data:
            if fss_all.id not in fss_all_ids:
                fss_all_ids.append(fss_all.id)
        if len(mnt_fss_ids) > 0:
            for mnt_fss_id in mnt_fss_ids:
                if mnt_fss_id in fss_all_ids:
                    fss_all_ids.remove(mnt_fss_id)
        if len(fss_all_ids) > 0:
            for fss_id in fss_all_ids:
                file_system_info_1 = file_system.get_file_system(file_system_id=fss_id)
                fs_name = file_system_info_1.data.display_name
                snapshot_id = file_system_info_1.data.source_details.source_snapshot_id
                if snapshot_id == '':
                    fs_source_snapshot_id = ''
                else:
                    tmp_source = reg + "--" + fs_name + "--" + snapshot_id
                    fs_source_snapshots[tmp_source] = snapshot_id
                    fs_source_snapshot_id = fs_name
                fs_snapshot_policy_id = file_system_info_1.data.filesystem_snapshot_policy_id
                if fs_snapshot_policy_id != '':
                    snapshot_policy_info = file_system.get_filesystem_snapshot_policy(filesystem_snapshot_policy_id=fs_snapshot_policy_id)
                    policy_name = snapshot_policy_info.data.display_name
                    policy_comp_id = snapshot_policy_info.data.compartment_id
                    policy_comp_name=cname
                    for comp_name, comp_id in ntk_compartment_ids.items():
                        if comp_id == policy_comp_id:
                            policy_comp_name = comp_name
                    fs_snapshot_policy_id = policy_comp_name + "@" + policy_name
                fss_replication = ""
                if len(replications_dict) > 0:
                    for k, v in replications_dict.items():
                        if v['sourceid'] == fss_id:
                            targetid = v['targetid']
                            for id, name in fss_all_dict.items():
                                if id == v['targetid']:
                                    targetid = name
                                else:
                                    targetid = v['targetid']
                            rep_format = targetid + "::" + str(v['interval']) + "::" + v['displayname']
                            fss_replication = fss_replication + rep_format + '\n'

                add_column_data(reg, cname, AD_name, "", "", "", "", "",
                                "", fs_name, "", fs_source_snapshot_id, fs_snapshot_policy_id, fss_replication,
                                "", "", "", "", "", "",
                                "", "", "",
                                fsinfo=file_system_info_1,
                                values_for_column_fss=values_for_column_fss, mnt_info1=None, nsg_n="")
                if (str(fss_id) not in fss):
                    # print(mt_display_name,"-",str(fs_name))
                    tf_name = commonTools.check_tf_variable(fs_name)
                    tf_resource = f'module.fss[\\"{tf_name}\\"].oci_file_storage_file_system.file_system'
                    if tf_resource not in state["resources"]:
                        importCommands[reg] += f'\n{tf_or_tofu} import "{tf_resource}" {str(fss_id)}'
                    fss.append(str(fss_id))

        ###### code to fetch MT without any exports #####
        mnt_all_ids = []
        for mnt_all in mount_info.data:
            mnt_all_ids.append(mnt_all.id)
        if len(mnt_all_ids) > 0:
            for mnt_id in mnt_with_export:
                if mnt_id in mnt_all_ids:
                    mnt_all_ids.remove(mnt_id)
        if len(mnt_all_ids) > 0:
            for k,v in mnt_info_dict.items():
                for mnt_id in mnt_all_ids:
                    if k == mnt_id:
                        mt_display_name = v['name']
                        vplussubnet = v['network']
                        mnt_p_ip = v['ip']
                        mnt_p_hostname = v['hostname']
                        nsg_names = v['nsg']
                        add_column_data(reg, cname, AD_name, mt_display_name, vplussubnet, mnt_p_ip, mnt_p_hostname, "","", "", "", "", "", "","", "", "", "", "", "","", "", "", fsinfo=file_system_info_1, values_for_column_fss=values_for_column_fss, mnt_info1=None, nsg_n=nsg_names)

    except Exception as e:
        pass


# Execution of the code begins here
def export_fss(inputfile, outdir, service_dir, config1, signer1, ct, export_compartments=[], export_regions=[],export_tags=[]):
    global tf_or_tofu
    tf_or_tofu = ct.tf_or_tofu
    tf_state_list = [tf_or_tofu, "state", "list"]
    input_compartment_names = export_compartments
    cd3file = inputfile

    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    sheetName = "FSS"

    global file_system, vnc_info, importCommands, rows, all_ads, input_compartment_list, AD, df, values_for_column_fss, sheet_dict_instances, config, signer
    config = config1
    signer = signer1
    file_system = oci.file_storage.FileStorageClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                     signer=signer)

    vnc_info = oci.core.VirtualNetworkClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                             signer=signer)

    importCommands = {}
    rows = []
    all_ads = []

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs FSS will be overwritten during this export process!!!\n")

    AD = lambda ad: "AD1" if ("AD-1" in ad or "ad-1" in ad) else (
        "AD2" if ("AD-2" in ad or "ad-2" in ad) else (
            "AD3" if ("AD-3" in ad or "ad-3" in ad) else "NULL"))  # Get shortend AD

    df, values_for_column_fss = commonTools.read_cd3(cd3file, sheetName)
    sheet_dict_instances = ct.sheet_dict[sheetName]

    # Fetch all ADs in all Subscribed Regions
    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        ads = oci.identity.IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
            all_ads.append(aval.name)

    # backup of .sh file
    resource = 'import_' + sheetName.lower()
    file_name = 'import_commands_' + sheetName.lower() + '.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir + "/", resource, file_name)
        importCommands[reg] =''
    for reg in export_regions:
        config.__setitem__("region", ct.region_dict[reg])
        state = {'path': f'{outdir}/{reg}/{service_dir}', 'resources': []}
        try:
            byteOutput = sp.check_output(tf_state_list, cwd=state["path"],stderr=sp.DEVNULL)
            output = byteOutput.decode('UTF-8').rstrip()
            for item in output.split('\n'):
                state["resources"].append(item.replace("\"", "\\\""))
        except Exception as e:
            pass
        for ntk_compartment_name in export_compartments:
            ads = oci.identity.IdentityClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                              signer=signer)
            for aval in ads.list_availability_domains(compartment_id=config['tenancy']).data:
                __get_mount_info(ntk_compartment_name, ct.ntk_compartment_ids, ct.ntk_compartment_ids[ntk_compartment_name], reg, aval.name,
                                 signer,state)

    # writing volume source into variables file
    var_data = {}
    for reg in export_regions:
        file = f'{outdir}/{reg}/{service_dir}/variables_{reg}.tf'
        # Read variables file data
        with open(file, 'r') as f:
            var_data[reg] = f.read()

        tempStrOcids = ""
        for k, v in fs_source_snapshots.items():
            if k.split("--")[0].lower() == reg:
                k = k.split("--")[1]
                v = "\"" + v + "\""
                tempStrOcids = "\t" + k + " = " + v + "\n" + tempStrOcids
        tempStrOcids = "\n" + tempStrOcids
        tempStrOcids = "#START_fss_source_snapshot_ocids#" + tempStrOcids + "\t#fss_source_snapshot_ocids_END#"
        var_data[reg] = re.sub('#START_fss_source_snapshot_ocids#.*?#fss_source_snapshot_ocids_END#', tempStrOcids, var_data[reg], flags=re.DOTALL)
        # Write variables file data
        with open(file, "w") as f:
            f.write(var_data[reg])
        f.close()

    commonTools.write_to_cd3(values_for_column_fss, cd3file, sheetName)
    print("{0} FSS objects exported into CD3.\n".format(len(values_for_column_fss["Region"])))

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        init_commands = f'\n######### Writing import for File Storage #########\n\n#!/bin/bash\n{tf_or_tofu} init'
        if importCommands[reg] != "":
            importCommands[reg] += f'\n{tf_or_tofu} plan\n'
            with open(script_file, 'a') as importCommandsfile:
                importCommandsfile.write(init_commands + importCommands[reg])
