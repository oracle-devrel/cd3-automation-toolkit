#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# FSS
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import pandas as pd
import os
import shutil
import datetime

sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader


# If input is csv file; convert to excel
def main():
    # Read input arguments
    parser = argparse.ArgumentParser(description="Creates TF files for FSS")
    parser.add_argument("inputfile",
                        help="Full Path to the CSV file for creating fss or CD3 excel file. eg  CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.inputfile
    outdir = args.outdir
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    x = datetime.datetime.now()
    date = x.strftime("%f").strip()

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    export = env.get_template('export-options-template')
    mounttarget = env.get_template('mount-target-template')
    fss = env.get_template('fss-template')
    fses = env.get_template('export-resource-template')

    if ('.csv' in filename):
        df = pd.read_csv(filename)
        excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
        df.to_excel(excel_writer, 'FSS')
        excel_writer.save()
        filename = 'tmp_to_excel.xlsx'

    df = pd.read_excel(filename, sheet_name='FSS', skiprows=1, dtype=object)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    endNames = {'<END>', '<end>', '<End>'}
    NaNstr = 'NaN'

    ADS = ["AD1", "AD2", "AD3"]
    tempStr = {}
    tempStr_fss = {}
    FSS_names = {}
    MT_names = {}
    mount_target_tf_name = ''
    fss_name = ''
    tempdict = {}

    global value

    for r in ct.all_regions:
        tempStr_fss[r] = ''
        MT_names[r] = []
        FSS_names[r] = []

    # fss_multi export logic
    def fss_exports(i, df, tempStr):
        global value
        i = i + 1
        try:
            if (str(df.loc[i, 'Path']) == path and str(df.loc[i, 'Region']) == "nan"):
                sourcecidr_1 = df.loc[i, 'Source CIDR']
                access_1 = df.loc[i, 'Access (READ_ONLY|READ_WRITE)']
                gid_1 = df.loc[i, 'GID']
                uid_1 = df.loc[i, 'UID']
                idsquash_1 = df.loc[i, 'IDSquash (NONE|ALL|ROOT)']
                require_ps_port_1 = str(str(df.loc[i, 'Require PS Port (true|false)']))

                if (str(sourcecidr_1).lower() == NaNstr.lower()):
                    sourcecidr_1 = "0.0.0.0/0"
                if str(access_1).lower() == NaNstr.lower() or str(access_1).strip() == "READ_ONLY":
                    access_1 = "READ_ONLY"
                elif str(access_1).strip() == "READ_WRITE":
                    access_1 = "READ_WRITE"
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
                sourceCIDR.append(sourcecidr_1)
                access.append(access_1)
                gid.append(gid_1)
                uid.append(uid_1)
                idsquash.append(idsquash_1)
                require_ps_port.append(require_ps_port_1)
                tempStr1 = {'sourceCIDR': sourceCIDR, 'access': access, 'gid': gid, 'uid': uid, 'idsquash': idsquash,
                            'require_ps_port': require_ps_port}
                fss_exports(i, df, tempStr1)
                value = i
            else:
                return "null"
        except Exception as e:
            pass
            # print(e)

    uniquereg = df['Region'].unique()

    # Take backup of files
    for eachregion in uniquereg:
        eachregion = str(eachregion).strip().lower()
        reg_out_dir = outdir + "/" + eachregion

        if (eachregion in commonTools.endNames or eachregion == 'nan'):
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        srcdir = outdir + "/" + r + "/"
        resource = 'FSS'
        commonTools.backup_file(srcdir, resource, "FSS.tf")

    for i in df.index:

        sourceCIDR = []
        access = []
        gid = []
        uid = []
        idsquash = []
        require_ps_port = []
        path = ''
        fss_tf_name = ''
        nsg_id = ''

        region = str(df.loc[i, 'Region'])
        if region == "nan":
            continue

        if region in endNames:
            break
        region = str(region).lower().strip()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # Check if values are entered for mandatory fields - to create fss
        if (str(df.loc[i, 'Path']).lower() == 'nan' or str(
                df.loc[i, 'FSS Name']).lower() == 'nan'
                or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                    df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or str(
                    df.loc[i, 'MountTarget Name']).lower() == 'nan'):
            print(
                "\nColumns Compartment Name, Availability Domain, MountTarget Name, MountTarget SubnetName, FSS Name and path cannot be left blank..Exiting!")
            exit()

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

            if columnname == 'MountTarget SubnetName':
                columnvalue = commonTools.check_tf_variable(columnvalue.strip())

            if columnname == "Access (READ_ONLY|READ_WRITE)":
                columnname = "access"
                if str(columnvalue).lower() == "nan" or str(columnvalue) == "" or str(columnvalue) == "READ_ONLY":
                    columnvalue = "READ_ONLY"
                if str(columnvalue).strip() != "READ_WRITE":
                    columnvalue = "READ_ONLY"
                if str(columnvalue).strip() == "READ_WRITE":
                    columnvalue = "READ_WRITE"
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
                    lbr_nsgs = str(columnvalue).strip().split(",")
                    if len(lbr_nsgs) == 1:
                        for nsgs in lbr_nsgs:
                            nsg_id = "oci_core_network_security_group." + commonTools.check_tf_variable(str(nsgs)) + ".id"
                    elif len(lbr_nsgs) >= 2:
                        c = 1
                        for nsgs in lbr_nsgs:
                            if c == len(lbr_nsgs):
                                nsg_id = nsg_id + "oci_core_network_security_group." + commonTools.check_tf_variable(str(nsgs)) + ".id"
                            else:
                                nsg_id = nsg_id + "oci_core_network_security_group." + commonTools.check_tf_variable(str(nsgs))+ ".id,"
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
                if str(columnvalue).lower() == "true" or str(columnvalue) == 1.0:
                    columnvalue = "true"
                elif str(columnvalue).lower() == "nan" or str(columnvalue) == "" or str(columnvalue).lower() == "false":
                    columnvalue = "false"
                require_ps_port.append(columnvalue)
                tempdict = {'require_ps_port': columnvalue}

            if columnname == "MountTarget Name":
                if columnvalue != '':
                    mount_target_tf_name = commonTools.check_tf_variable(str(columnvalue).strip())
                tempdict = {'mount_target_tf_name': mount_target_tf_name}
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

            export_set_info = export_set_info + export.render(tempStr)

        tempdict = {'export_set_info': export_set_info}
        tempStr.update(tempdict)

        if (str(mount_target_tf_name).strip() not in MT_names[region]):
            MT_names[region].append(str(mount_target_tf_name).strip())
            tempStr_fss[region] = tempStr_fss[region] + mounttarget.render(tempStr)

        if (fss_name.strip() not in FSS_names[region]):
            FSS_names[region].append(fss_name.strip())
            tempStr_fss[region] = tempStr_fss[region] + fss.render(tempStr)

        path_tf = path
        if path[-1] == '/':
            path_tf = path[:-1]
        FSE_tf_name = "FSE-" + mount_target_tf_name + "-" + fss_tf_name + "-" + path_tf[1:]
        FSE_tf_name = commonTools.check_tf_variable(FSE_tf_name)

        tempStr['FSE_tf_name'] = FSE_tf_name
        tempStr.update(tempdict)

        # FSE_tf_name=commonTools.check_tf_variable(FSE_name)
        tempStr_fss[region] = tempStr_fss[region] + fses.render(tempStr)

    for r in ct.all_regions:
        if (tempStr_fss[r] != ""):
            outfile = outdir + "/" + r + "/FSS.tf"

            oname = open(outfile, "w")
            print("Writing to " + outfile)
            oname.write(tempStr_fss[r])
            oname.close()

    # Remove temporary file created
    if ('tmp_to_excel.xlsx' in filename):
        os.remove(filename)


if __name__ == '__main__':
    # Execution of the code begins here
    main()