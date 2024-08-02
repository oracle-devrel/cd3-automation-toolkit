#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# FSS
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian, Mukesh Patel
#

import sys
import os

from pathlib import Path
sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


# If input is csv file; convert to excel
# Execution of the code begins here
def create_terraform_fss(inputfile, outdir, service_dir, prefix,ct):
    filename = inputfile

    sheetName = "FSS"

    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    export = env.get_template('export-options-template')
    mounttarget = env.get_template('mount-target-template')
    fss = env.get_template('fss-template')
    fses = env.get_template('export-resource-template')
    fssreplication = env.get_template('fss-replication-template')

    try:
        df = pd.read_excel(filename, sheet_name=sheetName, skiprows=1, dtype=object)
    except Exception as e:
        if ("No sheet named" in str(e)):
            print("\nTab - \"FSS\" is missing in the CD3. Please make sure to use the right CD3 in properties file...Exiting!!")
            exit(1)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    NaNstr = 'NaN'

    ADS = ["AD1", "AD2", "AD3"]
    tempStr = {}
    tempStr_fss = {}
    FSS_names = {}
    FSS_Replication_names = {}
    MT_names = {}

    tempdict = {}
    tempStr_mt = {}
    tempStr_fse = {}
    tempStr_fss_replication = {}
    prevreg = ''
    global value

    for r in ct.all_regions:
        tempStr[r] = ''
        tempStr_fss[r] = ''
        tempStr_mt[r] = ''
        tempStr_fse[r] = ''
        MT_names[r] = []
        FSS_names[r] = []
        FSS_Replication_names[r] = []
        tempStr_fss_replication[r] = ''

    # fss_multi export logic
    def fss_exports(i, df, tempStr):
        global value
        i = i + 1
        try:
            if (str(df.loc[i, 'Path']).strip() == path and str(df.loc[i, 'Region']).strip().lower() == "nan"):
                sourcecidr_1 = df.loc[i, 'Source CIDR']
                access_1 = df.loc[i, 'Access (READ_ONLY|READ_WRITE)']
                gid_1 = df.loc[i, 'GID']
                uid_1 = df.loc[i, 'UID']
                idsquash_1 = df.loc[i, 'IDSquash (NONE|ALL|ROOT)']
                require_ps_port_1 = str(str(df.loc[i, 'Require PS Port (true|false)']))
                allowed_auth_1 = df.loc[i, 'Allowed Auth']
                is_anonymous_access_allowed_1 = df.loc[i, 'Is Anonymous Access Allowed']
                if (str(sourcecidr_1).lower() == NaNstr.lower()):
                    sourcecidr_1 = "0.0.0.0/0"
                if str(access_1).lower() == NaNstr.lower() or str(access_1).strip() == "READ_WRITE":
                    access_1 = "READ_WRITE"
                elif str(access_1).strip() == "READ_ONLY":
                    access_1 = "READ_ONLY"
                if str(gid_1).lower() == NaNstr.lower():
                    gid_1 = "65534"
                else:
                    gid_1 = int(gid_1)

                if str(uid_1).lower() == NaNstr.lower():
                    uid_1 = "65534"
                else:
                    uid_1 = int(uid_1)

                if str(idsquash_1).lower() == NaNstr.lower() or (
                        str(idsquash_1).strip() != "ALL" and str(idsquash_1).strip() != "ROOT"):
                    idsquash_1 = "NONE"
                if str(require_ps_port_1).lower() == NaNstr.lower():
                    require_ps_port_1 = "false"
                elif str(require_ps_port_1).lower() == "true" or require_ps_port_1 == "TRUE" or str(
                        df.loc[i, 'Require PS Port (true|false)']) == 1.0:
                    require_ps_port_1 = "true"
                else:
                    require_ps_port_1 = "false"

                if str(is_anonymous_access_allowed_1).lower() == NaNstr.lower():
                    is_anonymous_access_allowed_1 = "false"
                elif str(is_anonymous_access_allowed_1).lower() == "true" or is_anonymous_access_allowed_1 == "TRUE" or str(
                        df.loc[i, 'Is Anonymous Access Allowed']) == 1.0:
                    is_anonymous_access_allowed_1 = "true"
                else:
                    is_anonymous_access_allowed_1 = "false"

                if str(allowed_auth_1).lower() == NaNstr.lower():
                    allowed_auth_1 = "\"" + "SYS" + "\""
                else:
                    allowed_auth_1 = str(allowed_auth_1).strip().upper()
                    auth_lists = str(allowed_auth_1).strip().split(",")
                    auth_list = ""
                    if len(auth_lists) == 1:
                        for auth in auth_lists:
                            auth_list = "\"" + auth.strip() + "\""
                    elif len(auth_lists) >= 2:
                        c = 1
                        for auth in auth_lists:
                            data = "\"" + auth.strip() + "\""

                            if c == len(auth_lists):
                                auth_list = auth_list + data
                            else:
                                auth_list = auth_list + data + ","
                            c += 1
                    allowed_auth_1 = auth_list

                sourceCIDR.append(sourcecidr_1)
                access.append(access_1)
                gid.append(gid_1)
                uid.append(uid_1)
                idsquash.append(idsquash_1)
                require_ps_port.append(require_ps_port_1)
                is_anonymous_access_allowed.append(is_anonymous_access_allowed_1)
                allowed_auth.append(allowed_auth_1)
                tempStr1 = {'sourceCIDR': sourceCIDR, 'access': access, 'gid': gid, 'uid': uid, 'idsquash': idsquash,
                            'require_ps_port': require_ps_port,'is_anonymous_access_allowed': is_anonymous_access_allowed,'allowed_auth':allowed_auth}
                fss_exports(i, df, tempStr1)
                value = i
            else:
                return "null"
        except Exception as e:
            pass
            # print(e)


    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    #subnets = parseSubnets(filename)

    fss_tf_name = ''
    for i in df.index:
        sourceCIDR = []
        access = []
        gid = []
        uid = []
        idsquash = []
        require_ps_port = []
        allowed_auth = []
        is_anonymous_access_allowed = []
        path = ''
        nsg_id = ''
        mount_target_tf_name = ''
        fss_name = ''

        region = str(df.loc[i, 'Region']).strip()

        if region in commonTools.endNames:
            break

        if region.lower() == 'nan' and str(df.loc[i, 'Compartment Name']).strip().lower() == 'nan' and str(df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).strip().lower() == 'nan' and str(df.loc[i, 'MountTarget Name']).strip().lower() == 'nan' and str(df.loc[i, 'Network Details']).strip().lower() == 'nan':
            continue

        region = str(region).lower().strip()

        if region!='nan' and region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        if region != 'nan':
            prevreg=region

        # List of the column headers
        dfcolumns = df.columns.values.tolist()
        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()
            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)
            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined Tags and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                tempStr.update(tempdict)

            if columnname == 'Compartment Name':
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}
                tempStr.update(tempdict)

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                if columnvalue != '':
                    AD = columnvalue.upper()
                    ad = ADS.index(AD)
                    columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}
            subnet_id = ''
            network_compartment_id=''
            vcn_name=''
            if columnname == 'Network Details':
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id = "root"
                    vcn_name = ""
                    subnet_id = columnvalue
                elif columnvalue.lower()!='nan' and columnvalue.lower()!='':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name=vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'subnet_id': subnet_id}

            if columnname == "Access (READ_ONLY|READ_WRITE)":
                columnname = "access"
                if str(columnvalue).lower() == "nan" or str(columnvalue) == "" or str(columnvalue) == "READ_WRITE":
                    columnvalue = "READ_WRITE"
                if str(columnvalue).strip() != "READ_WRITE":
                    columnvalue = "READ_ONLY"
                if str(columnvalue).strip() == "READ_ONLY":
                    columnvalue = "READ_ONLY"
                access.append(columnvalue)
                tempdict = {'access': columnvalue}

            if columnname == "Source CIDR":
                columnname = commonTools.check_column_headers(columnname)
                if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                    columnvalue = "0.0.0.0/0"
                sourceCIDR.append(columnvalue)
                tempdict = {'source_cidr': columnvalue}
                tempStr.update(tempdict)

            if columnname == "GID":
                columnname = commonTools.check_column_headers(columnname)
                if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                    columnvalue = "65534"
                else:
                    columnvalue = int(columnvalue)
                gid.append(columnvalue)

            if columnname == "UID":
                columnname = commonTools.check_column_headers(columnname)
                if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                    columnvalue = "65534"
                else:
                    columnvalue = int(columnvalue)
                uid.append(columnvalue)

            if columnname == 'NSGs':
                if columnvalue != '':
                    fss_nsgs = str(columnvalue).strip().split(",")
                    if len(fss_nsgs) == 1:
                        for nsgs in fss_nsgs:
                            nsg_id = "\"" + nsgs.strip() + "\""

                    elif len(fss_nsgs) >= 2:
                        c = 1
                        for nsgs in fss_nsgs:
                            data = "\"" + nsgs.strip() + "\""

                            if c == len(fss_nsgs):
                                nsg_id = nsg_id + data
                            else:
                                nsg_id = nsg_id + data +","
                            c += 1
                columnvalue = nsg_id

            if columnname == "IDSquash (NONE|ALL|ROOT)":
                columnname = "idsquash"
                if (columnvalue).lower() == "all":
                    columnvalue = "ALL"
                elif (columnvalue).lower() == "root":
                    columnvalue = "ROOT"
                else:
                    columnvalue = "NONE"
                idsquash.append(columnvalue)
                tempdict = {'idsquash': columnvalue}

            if columnname == "Require PS Port (true|false)":
                columnname = "require_ps_port"
                if str(columnvalue).lower() == "false":
                    columnvalue = "false"
                elif str(columnvalue).lower() == "nan" or str(columnvalue) == "" or str(columnvalue).lower() == "false":
                    columnvalue = "true"
                require_ps_port.append(columnvalue)
                tempdict = {'require_ps_port': columnvalue}

            if columnname == "Is Anonymous Access Allowed":
                columnname = "Is Anonymous Access Allowed"
                if str(columnvalue).lower() == "true" or str(columnvalue) == 1.0:
                    columnvalue = "true"
                elif str(columnvalue).lower() == "nan" or str(columnvalue) == "" or str(columnvalue).lower() == "false":
                    columnvalue = "false"
                is_anonymous_access_allowed.append(columnvalue)
                tempdict = {'is_anonymous_access_allowed': columnvalue}
            if columnname == "Allowed Auth":
                if columnvalue != '':
                    columnvalue = columnvalue.upper()
                    auth_lists = str(columnvalue).strip().split(",")
                    auth_list = ""
                    if len(auth_lists) == 1:
                        for auth in auth_lists:
                            auth_list = "\"" + auth.strip() + "\""

                    elif len(auth_lists) >= 2:
                        c = 1
                        for auth in auth_lists:
                            data = "\"" + auth.strip() + "\""

                            if c == len(auth_lists):
                                auth_list = auth_list + data
                            else:
                                auth_list = auth_list + data + ","
                            c += 1
                    columnvalue = auth_list
                    allowed_auth.append(columnvalue)
                else:
                    columnvalue = "\"" + "SYS" + "\""
                    allowed_auth.append(columnvalue)
                tempdict = {'allowed_auth': columnvalue}

            if columnname == "MountTarget Name":
                if columnvalue != '':
                    mount_target_tf_name = commonTools.check_tf_variable(str(columnvalue).strip())
                tempdict = {'mount_target_tf_name': mount_target_tf_name}
                tempStr.update(tempdict)
            if columnname == "Snapshot Policy":
                if columnvalue != '':
                    if len(columnvalue.split("@")) == 2:
                            snapshot_policy_comp = columnvalue.split("@")[0].strip()
                            snapshot_policy_comp = commonTools.check_tf_variable(snapshot_policy_comp)
                            snapshot_policy_name = columnvalue.split("@")[1].strip()
                    else:
                        snapshot_policy_comp = commonTools.check_tf_variable(str(df.loc[i, 'Compartment Name']).strip())
                        snapshot_policy_name = columnvalue.strip()
                else:
                    snapshot_policy_comp = ''
                    snapshot_policy_name = ''
                tempdict = {'policy_compartment_id': snapshot_policy_comp, 'snapshot_policy': snapshot_policy_name}
                tempStr.update(tempdict)
            if columnname == "Replication Information":
                replication = {}
                target_id = ''
                interval = ''
                replication_name = ''
                if columnvalue != '':
                    if columnvalue.find('\n') > 0:
                        tmp_rep_list = columnvalue.split('\n')
                        for tmp_list in tmp_rep_list:
                            replication_parts = tmp_list.split("::")
                            if len(replication_parts) == 1:
                                target_id = replication_parts[0]
                                interval = 'null'
                                replication_name = fss_tf_name + "-replication"
                            elif len(replication_parts) == 2:
                                target_id = replication_parts[0]
                                interval = replication_parts[1]
                                replication_name = fss_tf_name + "-replication"
                            elif len(replication_parts) == 3:
                                target_id = replication_parts[0]
                                interval = replication_parts[1]
                                replication_name = replication_parts[2]
                            replication[target_id] = {'target_id': target_id, 'interval': interval, 'replication_name': replication_name, 'replication_tf_name': commonTools.check_tf_variable(replication_name)}

                    else:
                        replication_parts = columnvalue.split("::")
                        if len(replication_parts) == 1:
                            target_id = replication_parts[0]
                            interval = 'null'
                            replication_name = fss_tf_name + "-replication"
                        elif len(replication_parts) == 2:
                            target_id = replication_parts[0]
                            interval = replication_parts[1]
                            replication_name = fss_tf_name + "-replication"
                        elif len(replication_parts) == 3:
                            target_id = replication_parts[0]
                            interval = replication_parts[1]
                            replication_name = replication_parts[2]
                        replication[target_id] = {'target_id': target_id, 'interval': interval,
                                                  'replication_name': replication_name,
                                                  'replication_tf_name': commonTools.check_tf_variable(replication_name)}
                    tempdict = {'replication': replication}
                    tempStr.update(tempdict)
            if columnname == 'FSS Name':
                if columnvalue != '':
                    fss_name = str(columnvalue).strip()
                    fss_tf_name = commonTools.check_tf_variable(fss_name.strip())
                tempdict = {'fss_tf_name': fss_tf_name, 'fss_name': fss_name}
                tempStr.update(tempdict)
            path = str(df.loc[i, 'Path']).strip()
            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        fss_exports(i, df, tempStr)
        export_set_info = ""

        for j in range(0, len(sourceCIDR)):
            tempStr['source'] = str(sourceCIDR[j]).strip()
            tempStr['access'] = access[j].strip()
            tempStr['gid'] = str(gid[j])
            tempStr['uid'] = str(uid[j])
            tempStr['idsquash'] = idsquash[j].strip()
            tempStr['require_ps_port'] = str(require_ps_port[j]).strip().lower()
            tempStr['is_anonymous_access_allowed'] = is_anonymous_access_allowed[j].strip().lower()
            tempStr['allowed_auth'] = allowed_auth[j].strip().upper()
            export_set_info = export_set_info + export.render(tempStr)
        tempdict = {'export_set_info': export_set_info}
        tempStr.update(tempdict)
        if region!= 'nan' and str(mount_target_tf_name).strip()!='' and str(mount_target_tf_name).strip() not in MT_names[region]:
            MT_names[region].append(str(mount_target_tf_name).strip())
            tempStr_mt[region] = tempStr_mt[region] + mounttarget.render(tempStr)
        if (region!='nan' and fss_name.strip()!='' and fss_name.strip() not in FSS_names[region]):
            FSS_names[region].append(fss_name.strip())
            tempStr_fss[region] = tempStr_fss[region] + fss.render(tempStr)
        if region != 'nan' and replication != '' and replication_name.strip() not in FSS_Replication_names[region]:
            tmp_rep_dict = {}
            tmp_rep_dict['fss_tf_name'] = tempStr['fss_tf_name']
            tmp_rep_dict['compartment_tf_name'] = tempStr['compartment_tf_name']
            for k,v in replication.items():
                FSS_Replication_names[region].append(v['replication_name'].strip())
                tmp_rep_dict.update(v)
                tempStr_fss_replication[region] = tempStr_fss_replication[region] + fssreplication.render(tmp_rep_dict)


        path_tf = path
        if path[-1] == '/':
            path_tf = path[:-1]
        FSE_tf_name = "FSE-" + mount_target_tf_name + "-" + fss_tf_name + "-" + path_tf[1:]
        FSE_tf_name = commonTools.check_tf_variable(FSE_tf_name)

        tempStr['FSE_tf_name'] = FSE_tf_name
        tempStr.update(tempdict)
        if (path !='nan'):
            if(region!='nan'):
                tempStr_fse[region] = tempStr_fse[region] + fses.render(tempStr)
            else:
                tempStr_fse[prevreg] = tempStr_fse[prevreg] + fses.render(tempStr)

    for r in ct.all_regions:
        if (tempStr_fss[r] != ""):
            outfile = outdir + "/" + r + "/" + service_dir + "/"+auto_tfvars_filename
            fssSrcStr = "##Add New FSS for " + r.lower() + " here##"
            fseSrcStr = "##Add New NFS Export Options for " + r.lower() + " here##"
            mtSrcStr = "##Add New Mount Targets for " + r.lower() + " here##"
            fssrepSrcStr = "##Add New FSS Replication for " + r.lower() + " here##"
            tempStr_fss[r] = mounttarget.render(count=0, region=r).replace(mtSrcStr,tempStr_mt[r]) + fss.render(count=0, region=r).replace(fssSrcStr,tempStr_fss[r]) + fses.render(count=0, region=r).replace(fseSrcStr,tempStr_fse[r]) + fssreplication.render(count=0, region=r).replace(fssrepSrcStr,tempStr_fss_replication[r])
            tempStr_fss[r] = "".join([s for s in tempStr_fss[r].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            oname.write(tempStr_fss[r])
            oname.close()
            print(outfile + " for FSS has been created for region " + r)

