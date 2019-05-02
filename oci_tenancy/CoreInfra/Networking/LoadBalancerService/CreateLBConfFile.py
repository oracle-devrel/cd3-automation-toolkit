#!/bin/python
import csv
import shutil
import sys
import argparse
import in_place
import re

def print_by_field(row):
    print(row)



def copy_template_file(LBName,LBHostName):
        filename = ('terraformfiles/'+LBName+'_Sabre_LB.tf').replace(" ","_")
        if LBHostName != 'IP Only':
                print('LBTemplate/publiclbtemplate.tf')
                shutil.copyfile('LBTemplate/publiclbtemplate.tf', filename)
        else:
                print('LBTemplate/publiclbtemplate.tf')
                shutil.copyfile('LBTemplate/privatelbtemplate.tf', filename)


def findQuotes(string, substring):
   return string.find(substring, string.find(substring) + 1)


def replaceAllplaceholders(fileToSearch,textToSearch,textToReplace):
        print ('testto search : '+textToSearch)
        print ( 'replace with : ' + textToReplace)
        if textToSearch == '##LBName##':
                textToReplace = textToReplace.replace(" ","_")
        textToReplace = textToReplace.replace(".","-")
        with in_place.InPlace(fileToSearch) as fp:
                for line in fp:
                        if line.strip().startswith('#'):
                                continue
                        #fp.write(line.replace(textToSearch, textToReplace))
                        fp.write(re.sub(textToSearch, textToReplace, line, flags=re.IGNORECASE))


def skipCommentedLine(lines):
        """
        A filter which skip/strip the comments and yield the
        rest of the lines
        :param lines: any object which we can iterate through such as a file
        object, list, tuple, or generator
        """
        for line in lines:
                comment_pattern = re.compile(r'\s*#.*$')
                line = re.sub(comment_pattern, '', line).strip()
                if line:
                        yield line



parser = argparse.ArgumentParser(description="CSV file name ")
parser.add_argument("cvsfilename",help="CSV file with required details with following columns [LBName,LBSize,LBSubnet1,LBSubnet2,LB_BES_Name,LBURL,LBHostName,LBListener]")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
cvsfilename = args.cvsfilename

with open(cvsfilename) as csvfile:
        #reader = csv.DictReader(csvfile)
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
                copy_template_file(row['LBName'],row['LBHostName'])
                for column in columns:
                        # print(column)
                        filename = row['LBName'].replace(" ","_")
                        replaceAllplaceholders('terraformfiles/'+ filename+'_Sabre_LB.tf','##'+column+'##',row[column])
