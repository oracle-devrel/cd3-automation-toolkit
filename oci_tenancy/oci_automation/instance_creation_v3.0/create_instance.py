#!/bin/python
import csv
import shutil
import sys
import argparse
import re
import pandas as pd


def print_by_field(row):
    print(row)



def copy_template_file(hostname, operatingsystem):
        print('Using template file - template/' + operatingsystem + 'template.tf')
        shutil.copyfile('template/' + operatingsystem + 'template.tf', outdir + '/' + hostname + '.tf')


def replaceAllplaceholders(fileToSearch, textToSearch, textToReplace):
    with open(fileToSearch, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = re.sub(textToSearch, textToReplace, filedata, flags=re.IGNORECASE)
    #filedata = filedata.replace(textToSearch, textToReplace)

    # Write the file out again
    with open(fileToSearch, 'w') as file:
        file.write(filedata)

def skipCommentedLine(lines):
    for line in lines:
        comment_pattern = re.compile(r'\s*#.*$')
        line = re.sub(comment_pattern, '', line).strip()
        if line:
            yield line


parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
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
if('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='Instances')
    for row in df.index:
        copy_template_file(df['Hostname'][row], df['OS'][row])
    for i in df.keys():
        for j in df.index:
            replaceAllplaceholders(outdir + '/' + df['Hostname'][j] + '.tf', '##' + i + '##', str(df[i][j]))

#If input is a csv file
if('.csv' in filename):
    with open(filename) as csvfile:
        #reader = csv.DictReader(skipCommentedLine(csvfile))
        reader = csv.DictReader()
        columns = reader.fieldnames
        for row in reader:
            copy_template_file(row['Hostname'], row['OS'])
            for column in columns:
                replaceAllplaceholders(outdir + '/' + row['Hostname'] + '.tf', '##' + column + '##', row[column])



