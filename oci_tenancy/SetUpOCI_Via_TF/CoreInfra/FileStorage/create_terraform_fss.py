#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
import shutil
import datetime

parser = argparse.ArgumentParser(description="Creates TF files for FSS")
parser.add_argument("inputfile",help="Full Path to the CSV file for creating fss or CD3 excel file. eg fss.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir",help="directory path for output tf files ")


if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
all_regions = os.listdir(outdir)

x = datetime.datetime.now()
date = x.strftime("%f").strip()

ADS = ["AD1", "AD2", "AD3"]
tempStr={}
FSS_names={}
MT_names={}

#If input is csv file; convert to excel
if('.csv' in filename):
        df = pd.read_csv(filename)
        excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
        df.to_excel(excel_writer, 'FSS')
        excel_writer.save()
        filename='tmp_to_excel.xlsx'

df = pd.read_excel(filename, sheet_name='FSS',skiprows=1)
df.dropna(how='all')

endNames = {'<END>', '<end>','<End>'}
NaNstr = 'NaN'

for r in all_regions:
    tempStr[r]=""
    MT_names[r]=[]
    FSS_names[r]=[]


for i in df.index:
    region=df.iat[i,0]
    if region in endNames:
        break
    region=region.strip().lower()

    if region not in all_regions:
        print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
        continue
    compartment_name = df.iat[i, 1]
    AD = df.iat[i, 2]
    mount_target_name = df.iat[i, 3]
    mount_target_subnet= df.iat[i,4]
    mount_target_ip = df.iat[i, 5]
    mount_target_hostname = df.iat[i, 6]
    fss_capacity = df.iat[i, 7]
    fss_size = df.iat[i, 8]
    fss_name = df.iat[i, 9]
    path = df.iat[i,10]

    sourceCIDR = df.iat[i,11]
    access = df.iat[i,12]
    gid = df.iat[i,13]
    uid = df.iat[i,14]
    idsquash = df.iat[i,15]
    require_ps_port = df.iat[i,16]

    if(str(compartment_name).lower()==NaNstr.lower() or str(AD).lower()==NaNstr.lower() or str(mount_target_name).lower()==NaNstr.lower()
            or str(mount_target_subnet).lower()==NaNstr.lower() or str(fss_name).lower()==NaNstr.lower() or str(path).lower()==NaNstr.lower()):
        print("Columns Compartment Name, Availability Domain, MountTarget Name, MountTarget Subnet, Max FSS Capacity, Max FSS Inodes, FSS Name and path cannot be left blank..exiting...")
        exit(1)

    AD = str(AD).strip().upper()
    ad = ADS.index(AD)
    if(str(sourceCIDR).lower()==NaNstr.lower()):
        sourceCIDR="0.0.0.0/0"

    if str(access).lower()==NaNstr.lower():
        access = "READ_ONLY"
    elif access.strip() != "READ_WRITE":
        access = "READ_ONLY"

    if str(gid).lower() == NaNstr.lower():
        gid = "65534"
    else:
        gid=int(gid)

    if str(uid).lower() == NaNstr.lower():
        uid = "65534"
    else:
        uid=int(uid)

    if str(idsquash).lower() == NaNstr.lower():
        idsquash = "NONE"
    elif idsquash != "ALL":
        idsquash = "NONE"
    elif idsquash != "ROOT":
        idsquash = "NONE"

    if str(require_ps_port).lower() == NaNstr.lower():
        require_ps_port = "false"
    elif str(require_ps_port).lower() != "true":
        require_ps_port = "false"

    if(mount_target_name.strip() not in MT_names[region]):
        MT_names[region].append(mount_target_name.strip())
        data_mt = """
        resource "oci_file_storage_mount_target" \"""" + mount_target_name.strip() + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name.strip() + """}"
            subnet_id = "${oci_core_subnet.""" + mount_target_subnet.strip() + """.id}"
            display_name = \"""" + mount_target_name.strip() + """"
            """
        if(str(mount_target_ip).lower()!=NaNstr.lower()):
            data_mt = data_mt + """
            ip_address = \"""" + mount_target_ip.strip() + """"
            """
        if(str(mount_target_hostname).lower()!=NaNstr.lower()):
            data_mt = data_mt+"""
            hostname_label = \"""" + mount_target_hostname.strip() + """"
            """
        data_mt = data_mt + """
        }
        resource "oci_file_storage_export_set" \"""" + mount_target_name.strip() + "-ES" """" {
            mount_target_id = "${oci_file_storage_mount_target.""" + mount_target_name.strip() + """.id}"
            display_name = \"""" + mount_target_name.strip() + "-ES1" """"
            """
        if(str(fss_capacity).lower()!=NaNstr.lower()):
            fss_capacity=int(fss_capacity)
            data_mt = data_mt +"""
            max_fs_stat_bytes = \"""" + str(fss_capacity)+ """"
            """
        if(str(fss_size).lower()!=NaNstr.lower()):
            fss_size=int(fss_size)
            data_mt = data_mt + """
            max_fs_stat_files = \"""" + str(fss_size) + """"
            """
        data_mt = data_mt +"""
        }
        """

        tempStr[region]=tempStr[region]+data_mt

    if(fss_name.strip() not in FSS_names[region]):
        FSS_names[region].append(fss_name.strip())
        data_fs = """
        resource "oci_file_storage_file_system" \"""" + fss_name.strip() + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name.strip() + """}"
            display_name = \"""" + fss_name.strip() + """"
        }"""


        tempStr[region]=tempStr[region]+data_fs

    FSE_name="FSE-"+mount_target_name.strip()+"-"+fss_name.strip()

    data_fs_es="""
        resource "oci_file_storage_export" \"""" + FSE_name+ """" {
            export_set_id = "${oci_file_storage_export_set.""" + mount_target_name.strip() + """-ES.id}"
            file_system_id = "${oci_file_storage_file_system.""" + fss_name.strip() + """.id}"
            path = \"""" + path + """"
            export_options {
                source = \"""" +str(sourceCIDR).strip() + """"
                access = \"""" + access.strip() + """"
                anonymous_gid = \"""" + str(gid) + """"
                anonymous_uid = \"""" + str(uid) + """"
                identity_squash = \"""" + idsquash.strip() + """"
                require_privileged_source_port = \"""" + str(require_ps_port).strip().lower() + """"
                }
        }
        """
    tempStr[region] = tempStr[region] + data_fs_es

for r in all_regions:
    if(tempStr[r]!=""):
        outfile = outdir + "/" + r + "/FSS.tf"
        if(os.path.exists(outfile)):
            shutil.copy(outfile, outfile + "_backUp" + date)
        oname = open(outfile, "w")
        print("Writing " + outfile)
        oname.write(tempStr[r])
        oname.close()

#Remove temporary file created
if('tmp_to_excel.xlsx' in filename):
    os.remove(filename)