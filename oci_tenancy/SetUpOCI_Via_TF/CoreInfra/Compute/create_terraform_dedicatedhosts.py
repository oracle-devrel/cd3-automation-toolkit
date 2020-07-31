#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
import datetime
sys.path.append(os.getcwd()+"/../..")
from commonTools import *



parser = argparse.ArgumentParser(description="Create Dedicated VM Hosts terraform file")
parser.add_argument("inputfile", help="Full Path of input file. It could be either the csv file or CD3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir=args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

outfile={}
oname={}
tfStr={}

x = datetime.datetime.now()
date = x.strftime("%S").strip()


if('.xls' in args.inputfile):
    df = pd.read_excel(args.inputfile, sheet_name='DedicatedVMHosts',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    for reg in ct.all_regions:
        src = outdir + "/" + reg + "/dedicated_vm_hosts.tf"
        if (os.path.exists(src)):
            dst = outdir + "/" + reg + "/dedicated_vm_hosts_backup" + date
            os.rename(src, dst)

        tfStr[reg] = ''

    NaNstr = 'NaN'
    endNames = {'<END>', '<end>', '<End>'}

    for i in df.index:
        region = df.iat[i,0]

        if (region in endNames):
            break

        region=region.strip().lower()
        if region not in ct.all_regions:
            print("Invalid Region; It should be one of the regions tenancy is subscribed to")
            exit(1)
        compartment_name = df.iat[i, 1]
        dedicated_host_name = df.iat[i, 2]
        dedicated_host_ad = df.iat[i, 3]
        dedicated_host_fd = df.iat[i, 4]
        dedicated_host_shape = df.iat[i, 5]

        if(str(compartment_name).lower()==NaNstr.lower() or str(dedicated_host_name).lower()==NaNstr.lower() or
                str(dedicated_host_ad)==NaNstr.lower() or str(dedicated_host_shape).lower()==NaNstr.lower()):
            print("All Fields mandatory except Fault Domain. Exiting...")
            exit(1)

        if('ad1' in dedicated_host_ad.lower()):
            ad='0'
        if('ad2' in dedicated_host_ad.lower()):
            ad='1'
        if('ad3' in dedicated_host_ad.lower()):
            ad='2'

        dedicated_host_name = dedicated_host_name.strip()
        dedicated_host_name = commonTools.check_tf_variable(dedicated_host_name)

        compartment_name = compartment_name.strip()
        compartment_name = commonTools.check_tf_variable(compartment_name)

        tfStr[region] = tfStr[region] + """
        resource "oci_core_dedicated_vm_host" \"""" + dedicated_host_name + """" {
        	    compartment_id = "${var.""" + compartment_name + """}"
        	    availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains."""+ad+""".name}"
          	    dedicated_vm_host_shape = \"""" + dedicated_host_shape.strip() + """"
          	    display_name = \"""" + dedicated_host_name.strip() + """"
        """
        if(str(dedicated_host_fd).lower()!=NaNstr.lower()):
            tfStr[region]=tfStr[region]+"""
                fault_domain = \"""" + dedicated_host_fd.strip() + """"
            }
            """
        else:
            tfStr[region]=tfStr[region]+"""
        } """
#If input is a csv file
elif('.csv' in args.inputfile):
    all_regions = os.listdir(outdir)
    for reg in all_regions:
        src=outdir+"/"+reg+"/dedicated_vm_hosts.tf"
        if(os.path.exists(src)):
            dst = outdir + "/" + reg + "/dedicated_vm_hosts_backup" + date
            os.rename(src, dst)
        tfStr[reg] = ''
    dedicated_host_file_name = args.inputfile
    fname = open(dedicated_host_file_name, "r")

    endNames = {'<END>', '<end>', '<End>'}

    # Read compartment file
    for line in fname:
        if(line.strip() in endNames):
            break
        if not line.startswith('#') and line != '\n':
            [region,compartment_name, dedicated_host_name, dedicated_host_ad, dedicated_host_fd, dedicated_host_shape] = line.split(',')
            region=region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
            if ('ad1' in dedicated_host_ad.lower()):
                ad = '0'
            if ('ad2' in dedicated_host_ad.lower()):
                ad = '1'
            if ('ad3' in dedicated_host_ad.lower()):
                ad = '2'
            if (compartment_name=='' or dedicated_host_name=='' or
                    dedicated_host_ad==''or dedicated_host_shape==''):
                print("All Fields mandatory except Fault Domain. Exiting...")
                exit(1)

            tfStr[region] = tfStr[region] + """
                    resource "oci_core_dedicated_vm_host" \"""" + dedicated_host_name.strip() + """" {
                    	    compartment_id = "${var.""" + compartment_name.strip() + """}"
                    	    availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + ad + """.name}"
                      	    dedicated_vm_host_shape = \"""" + dedicated_host_shape.strip() + """"
                      	    display_name = \"""" + dedicated_host_name.strip() + """"
                    """
            if (str(dedicated_host_fd).lower() != ''):
                tfStr[region] = tfStr[region] + """
                            fault_domain = \"""" + dedicated_host_fd.strip() + """"
                        }
                        """
            else:
                tfStr[region] = tfStr[region] + """
                    } """
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()


for reg in ct.all_regions:
    reg_out_dir = outdir + "/" + reg
    outfile[reg] = reg_out_dir + "/dedicated_vm_hosts.tf"

    if(tfStr[reg]!=''):
        oname[reg]=open(outfile[reg],'w')
        oname[reg].write(tfStr[reg])
        oname[reg].close()
        print(outfile[reg] + " containing TF for dedicated vm hosts has been created for region "+reg)
