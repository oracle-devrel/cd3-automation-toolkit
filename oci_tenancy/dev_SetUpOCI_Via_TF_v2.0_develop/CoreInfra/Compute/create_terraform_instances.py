#!/bin/python
import csv
import shutil
import sys
import argparse
import re
import pandas as pd


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


#If input is CD3 excel file
if('.xls' in filename):
    df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]

    df = pd.read_excel(filename, sheet_name='Instances',skiprows=1)
    for row in df.index:
        region=df['Region'][row]
        region=region.strip().lower()
        if region not in all_regions:
            print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
            exit(1)

    for row in df.index:
        copy_template_file(df['Hostname'][row], df['OS'][row],df['Region'][row])
    for i in df.keys():
        for j in df.index:
            if (re.match('Availability domain', i, flags=re.IGNORECASE)):
                if ('AD1' in df[i][j] or 'ad1' in df[i][j]):
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+'/'+df['Hostname'][j] + '.tf', '##' + i + '##', '0')
                    continue
                if ('AD2' in df[i][j] or 'ad2' in df[i][j]):
                    replaceAllplaceholders(outdir + '/' + df['Region'][j].strip().lower()+ '/'+df['Hostname'][j] + '.tf', '##' + i + '##', '1')
                    continue
                if ('AD3' in df[i][j] or 'ad3' in df[i][j]):
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
    with open(filename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
            copy_template_file(row['Hostname'], row['OS'],row['Region'])
            for column in columns:
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



