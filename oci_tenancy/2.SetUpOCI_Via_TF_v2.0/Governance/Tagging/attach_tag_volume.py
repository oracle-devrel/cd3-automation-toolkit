#!/bin/bash
# Author: Shruthi Subramanian
# Attach the tag and key values to the Volumes
import sys
import argparse
import csv
import re
import pandas as pd
def skipCommentedLine(lines):
    for line in lines:
        comment_pattern = re.compile(r'\s*#.*$')
        line = re.sub(comment_pattern, '', line).strip()
        if line:
            yield line

parser = argparse.ArgumentParser(description="Updates tf file for block volumes to attach tag info")
parser.add_argument("file", help="Full Path of CSV file.Ex:tag_volume-csv-example.csv or CD3 in example folder")
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

args = parser.parse_args()

string = ""
new_string = ""

# If the input is CD3
if ('.xlsx' in filename):
    df = pd.read_excel(filename, sheet_name='TagVolume',skiprows=1)
    for i in df.index:
        string = ""
        new_string = ""
        for j in df.keys():
            if (str(df[j][i]) == 'nan'):
                continue
            elif (j == 'VolumeName'):
                Volume_name = df['VolumeName'][i]
            elif (j == 'Region'):
                Region = df['Region'][i].strip().lower()
            else:
                namespace = j
                key_value = df[j][i]
                if key_value == "":
                    key = ""
                    value = ""
                    dt = """ """
                else:
                    key_value_tmp = key_value.split("=")
                    key = key_value_tmp[0].strip()
                    value = key_value_tmp[1].strip()
                    dt = """\"""" + namespace + """.""" + key + """\"=\"""" + value + """\",\n
                                        """
                    string += dt
                    k = string.rfind(",")
                    new_string = string[:k] + " " + string[k + 1:]

        tmpstr = """
        defined_tags = {
        """+new_string+"""
        }
        ## Defined Tag Info ##
        """

        testToSearch = "## Defined Tag Info ##"
        terrafile = outdir + "/" + Region + "/" + Volume_name + ".tf"

        with open(terrafile, 'r+') as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(testToSearch, tmpstr)

        # Write the file out again
        with open(terrafile, 'w+') as file:
            file.write(filedata)

#If input is a csv file
elif('.csv' in filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:

            volume = row['VolumeName']
            string = ""
            for column in columns:
                if column == 'VolumeName':
                    continue
                elif column == 'Region':
                    Region = row[column].strip().lower()

                else:
                    namespace = column
                    tmp = row[column]
                    if tmp == "":
                        tag_key = ""
                        value = ""
                        dt = """ """
                    else:
                        tmp1 = row[column].split("=")
                        tag_key = tmp1[0].strip()
                        value = tmp1[1].strip()
                        dt = """\""""+namespace + """.""" + tag_key + """\"=\""""+value+"""\",\n
                    """
                        string += dt

                        k = string.rfind(",")
                        new_string = string[:k] + " " + string[k + 1:]

            tmpstr = """
            defined_tags = {
                   """+new_string+"""
            }
            ## Defined Tag Info ##
            """

            testToSearch = "## Defined Tag Info ##"
            terrafile = outdir + "/" + Region + "/" + volume + ".tf"

            with open(terrafile, 'r+') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace(testToSearch, tmpstr)

            # Write the file out again
            with open(terrafile, 'w+') as file:
                file.write(filedata)
else:
    print("Invalid input file format; Acceptable formats: .csv, CD3")
    exit()
