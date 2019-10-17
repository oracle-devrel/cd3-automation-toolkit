#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os


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

ADS = ["AD1", "AD2", "AD3"]

#If input is csv file; convert to excel
if('.csv' in filename):
        df = pd.read_csv(filename)
        excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
        df.to_excel(excel_writer, 'FSS')
        excel_writer.save()
        filename='tmp_to_excel.xlsx'

df = pd.read_excel(filename, sheet_name='FSS',skiprows=1)
df.dropna(how='all')

endNames = {'<END>', '<end>'}
NaNstr = 'NaN'
for i in df.index:
    region=df.iat[i,0]
    region=region.strip().lower()
    if region in endNames:
        break

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

    if str(uid).lower() == NaNstr.lower():
        uid = "65534"

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

    tempstr = """
        resource "oci_file_storage_mount_target" \"""" + mount_target_name.strip() + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name.strip() + """}"
            subnet_id = "${oci_core_subnet.""" + mount_target_subnet.strip() + """.id}"
            display_name = \"""" + mount_target_name.strip() + """"
            """
    if(str(mount_target_ip).lower()!=NaNstr.lower()):
        tempstr = tempstr + """
            ip_address = \"""" + mount_target_ip.strip() + """"
            """
    if(str(mount_target_hostname).lower()!=NaNstr.lower()):
        tempstr = tempstr+"""
            hostname_label = \"""" + mount_target_hostname.strip() + """"
            """
    tempstr = tempstr + """
        }
        
        resource "oci_file_storage_export_set" \"""" + mount_target_name.strip() + "-ES1" """" {
            mount_target_id = "${oci_file_storage_mount_target.""" + mount_target_name.strip() + """.id}"
            display_name = \"""" + mount_target_name.strip() + "-ES1" """"
            """
    if(str(fss_capacity).lower()!=NaNstr.lower()):
        fss_capacity=int(fss_capacity)
        tempstr = tempstr +"""
            max_fs_stat_bytes = \"""" + str(fss_capacity)+ """"
            """
    if(str(fss_size).lower()!=NaNstr.lower()):
        fss_size=int(fss_size)
        tempstr = tempstr + """
            max_fs_stat_files = \"""" + str(fss_size) + """"
            """
    tempstr = tempstr +"""
        }
        """
    tempstr = tempstr +"""
        resource "oci_file_storage_file_system" \"""" + fss_name.strip() + """" {
            availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
            compartment_id = "${var.""" + compartment_name.strip() + """}"
            display_name = \"""" + fss_name.strip() + """"
        }

        resource "oci_file_storage_export" \"""" + fss_name.strip() + "-FS1" """" {
            export_set_id = "${oci_file_storage_export_set.""" + mount_target_name.strip() + """-ES1.id}"
            file_system_id = "${oci_file_storage_file_system.""" + fss_name.strip() + """.id}"
            path = \"""" + path + """"
            export_options {
                source = \"""" +str(sourceCIDR).strip() + """"
                access = \"""" + access.strip() + """"
                anonymous_gid = \"""" + str(gid).strip() + """"
                anonymous_uid = \"""" + str(uid).strip() + """"
                identity_squash = \"""" + idsquash.strip() + """"
                require_privileged_source_port = \"""" + str(require_ps_port).strip().lower() + """"
                }
        }
        """
    outfile = outdir + "/" + region + "/" + fss_name.strip() + "_fss.tf"
    oname = open(outfile, "w")
    print("Writing " + outfile)
    oname.write(tempstr)
    oname.close()

#Remove temporary file created
if('tmp_to_excel.xlsx' in filename):
    os.remove(filename)