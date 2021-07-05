#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# NSG
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import argparse
import pandas as pd
import os
import datetime
sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######

# If input is CD3 excel file
def main():

    # Read the input arguments
    parser = argparse.ArgumentParser(description="Attaches back up policy to Boot Volumes")
    parser.add_argument("file", help="Full Path of CD3 excel file containing instance info eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf file ")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.file
    outdir = args.outdir
    endnames = ['<end>', '<END>', '<End>']


    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Instances")
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    Region = ''
    nsg_ids = ''

    for i in df.index:
        for j in df.keys():
            if(str(df[j][i]) in endnames):
                exit()
            if (str(df[j][i]) == 'nan'):
                continue

            elif (j == 'Region'):
                Region = df['Region'][i].strip().lower()

            elif (j == 'Hostname'):
                Host_name = df['Hostname'][i]
                NSG_col = df['NSGs'][i]
                nsg_exist=0
                if str(NSG_col)!='nan':
                    nsg_exist = 1
                    nsg_ids="nsg_ids=""[ "
                    NSGs=NSG_col.split(",")
                    i=0
                    while i<len(NSGs):
                        nsg_ids=nsg_ids+"oci_core_network_security_group."+commonTools.check_tf_variable(NSGs[i].strip())+".id"
                        if(i!=len(NSGs)-1):
                            nsg_ids=nsg_ids+","
                        else:
                            nsg_ids=nsg_ids+" ]"
                        i+=1
                textToSearch1 = "##NSGs##"
                textToSearch2 = "nsg_ids="

                if(nsg_exist==1):
                    x = datetime.datetime.now()
                    date = x.strftime("%S").strip()

                    os.rename(outdir+"/"+Region+"/"+Host_name+"_instance.tf",outdir+"/"+Region+"/"+Host_name+"_instance.tf_beforeNSG"+date)
                    file_r= open(outdir+"/"+Region+"/"+Host_name+"_instance.tf_beforeNSG"+date, 'r')
                    file_w = open(outdir + "/" + Region + "/" + Host_name + "_instance.tf", 'w')

                    for line in file_r:
                        if(textToSearch1 in line):
                            line=line.replace(textToSearch1,nsg_ids)
                        elif (textToSearch2 in line):
                            line="\t\t\t\t"+nsg_ids+"\n"
                        file_w.write(line)
                    file_w.close()
                    file_r.close()
                    print("\nNSG info updated in "+outdir + "/" + Region + "/" + Host_name + "_instance.tf")


if __name__ == '__main__':

    # Execution of the code begins here
    main()