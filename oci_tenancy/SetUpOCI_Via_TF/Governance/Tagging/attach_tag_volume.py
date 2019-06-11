#!/bin/bash
# Create Tag Namespace from CD3 file
import sys
import argparse
import csv
import re

def skipCommentedLine(lines):
    for line in lines:
        comment_pattern = re.compile(r'\s*#.*$')
        line = re.sub(comment_pattern, '', line).strip()
        if line:
            yield line

parser = argparse.ArgumentParser(description="Create vars files for the each row in csv file.")
parser.add_argument("file", help="Full Path of CSV file.Ex:tag_server.csv in example folder")
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


#If input is a csv file
if('.csv' in filename):
    with open(filename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
            volume = row['VolumeName']
            string = ""
            for column in columns:
                if column == 'VolumeName':
                    continue
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
            terrafile = outdir + "/" + volume + ".tf"

            with open(terrafile, 'r+') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace(testToSearch, tmpstr)

            # Write the file out again
            with open(terrafile, 'w+') as file:
                file.write(filedata)
else:
    print("Invalid input file format; Acceptable formats: .csv")
    exit()
