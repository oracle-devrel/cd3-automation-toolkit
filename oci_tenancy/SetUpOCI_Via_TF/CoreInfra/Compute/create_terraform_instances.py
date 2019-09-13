#!/usr/bin/python3
import csv
import shutil
import sys
import argparse
import re
import pandas as pd
import os


def copy_template_file(hostname, operatingsystem,region):
        region=region.strip().lower()
        print('Using template file - template/' + operatingsystem + 'template.tf')
        shutil.copyfile('template/' + operatingsystem + 'template.tf', outdir + '/'+region+'/' + hostname + '.tf')


def replaceAllplaceholders(fileToSearch, textToSearch, textToReplace):
    with open(fileToSearch, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = re.sub(textToSearch, textToReplace, filedata, flags=re.IGNORECASE)

    # Write the file out again
    with open(fileToSearch, 'w') as file:
        file.write(filedata)

def skipCommentedLine(lines):
    for line in lines:
        comment_pattern = re.compile(r'\s*#.*$')
        line = re.sub(comment_pattern, '', line).strip()
        if line:
            yield line


parser = argparse.ArgumentParser(description="Creates Instances TF file")
parser.add_argument("file", help="Full Path of csv file or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir
endNames = {'<END>', '<end>'}

#If input is CD3 excel file
if('.xls' in filename):
    #df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    #properties = df_info['Property']
    #values = df_info['Value']

    #all_regions = str(values[7]).strip()
    #all_regions = all_regions.split(",")
    #all_regions = [x.strip().lower() for x in all_regions]
    all_regions = os.listdir(outdir)

    df = pd.read_excel(filename, sheet_name='Instances',skiprows=1)
    for row in df.index:
        region=df['Region'][row]
        region=region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

    for row in df.index:
        copy_template_file(df['Hostname'][row], df['OS'][row],df['Region'][row])
    #for i in df.keys():
    #    for j in df.index:
    for j in df.index:
        for i in df.keys():
            if(str(df[i][j]) in endNames):
                exit()
            if (re.match('DedicatedVMHost', i, flags=re.IGNORECASE)):
                dedicated_host=str(df[i][j])
                if(dedicated_host!='nan'):
                    dedicated_host_str="""dedicated_vm_host_id = "${oci_core_dedicated_vm_host."""+dedicated_host+""".id}" """
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower() + '/' + df['Hostname'][j] + '.tf','##' + i + '##', dedicated_host_str)
                continue
            if (re.match('NSGs', i, flags=re.IGNORECASE)):
                NSG_col = str(df[i][j])
                if NSG_col != 'nan':
                    nsg_str = "nsg_ids=""[ "
                    NSGs = NSG_col.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg_str = nsg_str + """"${oci_core_network_security_group.""" + NSGs[k].strip() + """.id}" """
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        else:
                            nsg_str = nsg_str + " ]"
                        k += 1
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower() + '/' + df['Hostname'][j] + '.tf','##' + i + '##', nsg_str)
                continue

            if (re.match('Availability domain', i, flags=re.IGNORECASE)):
                if ('ad1' in str(df[i][j]).lower()):
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+'/'+df['Hostname'][j] + '.tf', '##' + i + '##', '0')
                    continue
                if ('ad2' in str(df[i][j]).lower()):
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', '1')
                    continue
                if ('ad3' in str(df[i][j]).lower()):
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', '2')
                    continue
            if (str(df[i][j]) == 'nan'):
                replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', "")
                continue
            if (str(df[i][j]) == 'True' or str(df[i][j]) == 'False'):
                replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', str(df[i][j]).lower())
                continue
            replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', str(df[i][j]))

#If input is a csv file
elif('.csv' in filename):
    all_regions = os.listdir(outdir)
    with open(filename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
            region = row['Region']
            region = region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
        for row in reader:
            copy_template_file(row['Hostname'], row['OS'],row['Region'])
            for column in columns:
                if (row['Region'] in endNames):
                    exit()

                if (re.match('DedicatedVMHost', column, flags=re.IGNORECASE)):
                    dedicated_host = row[column]
                    if (dedicated_host != 'nan'):
                        dedicated_host_str = """dedicated_vm_host_id = "${oci_core_dedicated_vm_host.""" + dedicated_host + """.id}" """
                        replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower() + '/' + row['Hostname'] + '.tf','##' + column + '##', dedicated_host_str)
                    continue

                if (re.match('NSGs', column, flags=re.IGNORECASE)):
                    NSG_col = row[column]
                    if NSG_col != '':
                        nsg_str = "nsg_ids=""[ "
                        NSGs = NSG_col.split(":")
                        k = 0
                        while k < len(NSGs):
                            nsg_str = nsg_str + """"${oci_core_network_security_group.""" + NSGs[
                                k].strip() + """.id}" """
                            if (k != len(NSGs) - 1):
                                nsg_str = nsg_str + ","
                            else:
                                nsg_str = nsg_str + " ]"
                            k += 1
                        replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower() + '/' + row['Hostname'] + '.tf','##' + column + '##', nsg_str)

                if(re.match('Availability domain',column,flags=re.IGNORECASE)):
                    if ('AD1' in row[column]):
                        row[column]='0'
                    if ('AD2' in row[column]):
                        row[column] = '1'
                    if ('AD3' in row[column]):
                        row[column] = '2'
                if(re.match('Pub Address',column,flags=re.IGNORECASE)):
                    if (row[column].lower() == "true"):
                        row[column] = 'true'
                    if (row[column].lower() == "false"):
                        row[column] = 'false'
                replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower()+'/'+row['Hostname'] + '.tf', '##' + column + '##', row[column])

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()



