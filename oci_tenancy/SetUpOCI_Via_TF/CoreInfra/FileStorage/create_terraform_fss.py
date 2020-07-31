#!/usr/bin/python3
# Author: Suruchi
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
import shutil
import datetime

sys.path.append(os.getcwd() + "/../..")
from commonTools import *

parser = argparse.ArgumentParser(description="Creates TF files for FSS")
parser.add_argument("inputfile",help="Full Path to the CSV file for creating fss or CD3 excel file. eg fss.csv or CD3-template.xlsx in example folder")
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
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

x = datetime.datetime.now()
date = x.strftime("%f").strip()

ADS = ["AD1", "AD2", "AD3"]
tempStr = {}
FSS_names = {}
MT_names = {}

global value


# fss_multi export logic
def fss_exports(i, df, sourceCIDR, access, gid, uid, idsquash, require_ps_port, path):
    global value
    i = i + 1
    try:
        if (str(df.iat[i, 10]) == path and str(df.iat[i, 0]) == "nan"):
            sourcecidr_1 = df.iat[i, 11]
            access_1 = df.iat[i, 12]
            gid_1 = df.iat[i, 13]
            uid_1 = df.iat[i, 14]
            idsquash_1 = df.iat[i, 15]
            require_ps_port_1 = str(str(df.iat[i, 16]))
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
            elif str(require_ps_port_1).lower() == "true" or require_ps_port_1 == "TRUE" or df.iat[i, 16] == 1.0:
                require_ps_port_1 = "true"
            else:
                require_ps_port_1 = "false"
            sourceCIDR.append(sourcecidr_1)
            access.append(access_1)
            gid.append(gid_1)
            uid.append(uid_1)
            idsquash.append(idsquash_1)
            require_ps_port.append(require_ps_port_1)
            fss_exports(i, df, sourceCIDR, access, gid, uid, idsquash, require_ps_port, path)
            value = i
        else:
            return "null"
    except Exception as e:
        print(e)


# If input is csv file; convert to excel
if ('.csv' in filename):
    df = pd.read_csv(filename)
    excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
    df.to_excel(excel_writer, 'FSS')
    excel_writer.save()
    filename = 'tmp_to_excel.xlsx'

df = pd.read_excel(filename, sheet_name='FSS', skiprows=1)
df = df.dropna(how='all')
df = df.reset_index(drop=True)

endNames = {'<END>', '<end>', '<End>'}
NaNstr = 'NaN'

for r in ct.all_regions:
    tempStr[r] = ""
    MT_names[r] = []
    FSS_names[r] = []

for i in df.index:
    region = df.iat[i, 0]
    if region in endNames:
        break
    region = str(region).lower().strip()
    if region == "nan":
        continue
    if region not in ct.all_regions:
        print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
        continue
    compartment_name = df.iat[i, 1]
    AD = df.iat[i, 2]
    mount_target_name = df.iat[i, 3]
    mount_target_subnet = df.iat[i, 4]
    mount_target_ip = df.iat[i, 5]
    mount_target_hostname = df.iat[i, 6]
    fss_capacity = df.iat[i, 7]
    fss_size = df.iat[i, 8]
    fss_name = df.iat[i, 9]
    path = df.iat[i, 10]
    exports = []
    sourceCIDR = []
    access = []
    gid = []
    uid = []
    idsquash = []
    require_ps_port = []
    if (str(compartment_name).lower() == NaNstr.lower() or str(AD).lower() == NaNstr.lower() or str(
            mount_target_name).lower() == NaNstr.lower()
            or str(mount_target_subnet).lower() == NaNstr.lower() or str(fss_name).lower() == NaNstr.lower() or str(
                path).lower() == NaNstr.lower()):
        print("Columns Compartment Name, Availability Domain, MountTarget Name, MountTarget Subnet, Max FSS Capacity, Max FSS Inodes, FSS Name and path cannot be left blank..exiting...")
        exit(1)

    mount_target_subnet = commonTools.check_tf_variable(mount_target_subnet.strip())
    AD = str(AD).strip().upper()
    ad = ADS.index(AD)

    if (str(df.iat[i, 11]).lower() == NaNstr.lower()):
        sourceCIDR.append("0.0.0.0/0")
    else:
        sourceCIDR.append(str(df.iat[i, 11]))

    if str(df.iat[i, 12]).lower() == NaNstr.lower() or str(df.iat[i, 12]).strip() == "READ_ONLY":
        access.append("READ_ONLY")
    elif str(df.iat[i, 12]).strip() == "READ_WRITE":
        access.append("READ_WRITE")

    if str(df.iat[i, 13]).lower() == NaNstr.lower():
        gid.append(str("65534"))
    else:
        gid.append(int(df.iat[i, 13]))

    if str(df.iat[i, 14]).lower() == NaNstr.lower():
        uid.append(str("65534"))
    else:
        uid.append(int(df.iat[i, 14]))

    if str(df.iat[i, 15]).lower() == NaNstr.lower() or (str(df.iat[i, 15]).strip() != "ALL" and str(df.iat[i, 15]).strip() != "ROOT"):
        idsquash.append("NONE")
    else:
        idsquash.append(str(df.iat[i, 15]))
    if (str(df.iat[i, 16]).lower() == NaNstr.lower()):
        require_ps_port.append("false")
    elif (str(df.iat[i, 16]).lower() == "true" or df.iat[i, 16] == "TRUE" or df.iat[i, 16] == 1.0):
        require_ps_port.append("true")
    else:
        require_ps_port.append("false")

    fss_exports(i, df, sourceCIDR, access, gid, uid, idsquash, require_ps_port, path)
    export_set_info = ""
    for j in range(0, len(sourceCIDR)):
        export_set_info += """
        export_options {
                        source = \"""" + str(sourceCIDR[j]).strip() + """"
                        access = \"""" + access[j].strip() + """"
                        anonymous_gid = \"""" + str(gid[j]) + """"
                        anonymous_uid = \"""" + str(uid[j]) + """"
                        identity_squash = \"""" + idsquash[j].strip() + """"
                        require_privileged_source_port = \"""" + str(require_ps_port[j]).strip().lower() + """"
                        } """

    compartment_name = compartment_name.strip()
    compartment_name = commonTools.check_tf_variable(compartment_name)

    if (mount_target_name.strip() not in MT_names[region]):
        MT_names[region].append(mount_target_name.strip())
        mount_target_tf_name = commonTools.check_tf_variable(mount_target_name.strip())
        data_mt = """
            resource "oci_file_storage_mount_target" \"""" + mount_target_tf_name + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name + """}"
            subnet_id = "${oci_core_subnet.""" + mount_target_subnet + """.id}"
            display_name = \"""" + mount_target_name.strip() + """"
            """
        if (str(mount_target_ip).lower() != NaNstr.lower()):
            data_mt = data_mt + """
            ip_address = \"""" + mount_target_ip.strip() + """"
            """
        if (str(mount_target_hostname).lower() != NaNstr.lower()):
            data_mt = data_mt + """
            hostname_label = \"""" + mount_target_hostname.strip() + """"
            """

        data_mt = data_mt + """
        }
        """
        tempStr[region] = tempStr[region] + data_mt

    if (fss_name.strip() not in FSS_names[region]):
        FSS_names[region].append(fss_name.strip())
        fss_tf_name = commonTools.check_tf_variable(fss_name.strip())
        data_fs = """
        resource "oci_file_storage_file_system" \"""" + fss_tf_name + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name + """}"
            display_name = \"""" + fss_name.strip() + """"
        }"""

        tempStr[region] = tempStr[region] + data_fs

    path_tf = path
    if path[-1] == '/':
        path_tf = path[:-1]
    FSE_tf_name = "FSE-" + mount_target_tf_name + "-" + fss_tf_name + "-" + path_tf[1:]
    FSE_tf_name = commonTools.check_tf_variable(FSE_tf_name)

    # FSE_tf_name=commonTools.check_tf_variable(FSE_name)
    data_fs_es = """
            resource "oci_file_storage_export" \"""" + FSE_tf_name + """" {
                export_set_id = "${oci_file_storage_mount_target.""" + mount_target_tf_name + """.export_set_id}"
                file_system_id = "${oci_file_storage_file_system.""" + fss_tf_name + """.id}"
                path = \"""" + path + """"
                """ + export_set_info + """ 
                }
               """
    tempStr[region] = tempStr[region] + data_fs_es

for r in ct.all_regions:
    if (tempStr[r] != ""):
        outfile = outdir + "/" + r + "/FSS.tf"
        if (os.path.exists(outfile)):
            shutil.copy(outfile, outfile + "_backUp" + date)
        oname = open(outfile, "w")
        print("Writing " + outfile)
        oname.write(tempStr[r])
        oname.close()

# Remove temporary file created
if ('tmp_to_excel.xlsx' in filename):
    os.remove(filename)