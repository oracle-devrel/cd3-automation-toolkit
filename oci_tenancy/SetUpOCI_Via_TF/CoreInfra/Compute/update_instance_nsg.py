#!/usr/bin/python3
# Author: Suruchi
import sys
import argparse
import pandas as pd
import os
import datetime


x = datetime.datetime.now()
date = x.strftime("%S").strip()

parser = argparse.ArgumentParser(description="Attaches back up policy to Boot Volumes")
parser.add_argument("file", help="Full Path of CD3 excel file or CSV containing instance info eg CD3-template.xlsx or instace-csv-example.csv in example folder")
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
endnames= ['<end>','<END>','<End>']

if('.csv' in filename):
    df = pd.read_csv(filename)
    excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
    df.to_excel(excel_writer, 'Instances')
    excel_writer.save()
    filename='tmp_to_excel.xlsx'

if ('.xls' in filename):

    df = pd.read_excel(filename, sheet_name='Instances',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

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
                        nsg_ids=nsg_ids+""""${oci_core_network_security_group."""+commonTools.check_tf_variable(NSGs[i].strip())+""".id}" """
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

                    os.rename(outdir+"/"+Region+"/"+Host_name+".tf",outdir+"/"+Region+"/"+Host_name+".tf_beforeNSG"+date)
                    file_r= open(outdir+"/"+Region+"/"+Host_name+".tf_beforeNSG"+date, 'r')
                    file_w = open(outdir + "/" + Region + "/" + Host_name + ".tf", 'w')

                    for line in file_r:
                        if(textToSearch1 in line):
                            line=line.replace(textToSearch1,nsg_ids)
                        elif (textToSearch2 in line):
                            line="\t\t\t\t"+nsg_ids+"\n"
                        file_w.write(line)
                    file_w.close()
                    file_r.close()
                    print("NSG info updated in "+outdir + "/" + Region + "/" + Host_name + ".tf")

if('tmp_' in filename):
    os.remove(filename)