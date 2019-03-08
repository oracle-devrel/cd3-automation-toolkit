#!/bin/python

import sys
import argparse
import csv
import re
import in_place

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

def appendRulesTotempfile(tempFile,template):
        f1 = open(template)
        s = f1.read()
        #print ('template ::: '+s)
        f1.close()
        f2 = open(tempFile, 'a+')
        f2.write(s)
        f2.close()

def replaceAllplaceholders(fileToSearch,textToSearch,textToReplace):
        tempString = ""
        #textToReplace = textToReplace.replace(".","-")

        print('fileToSearch '+fileToSearch)
        print('textToSearch '+textToSearch)
        print('textToReplace '+textToReplace)
        with in_place.InPlace(fileToSearch) as fp:
            for line in fp:
                #print('line ::::::::: '+line)
                if line.strip().startswith('#'):
                    continue
                #fp.write(line.replace(textToSearch, textToReplace))
                updatedline = re.sub(textToSearch, textToReplace, line, flags=re.IGNORECASE)
                #print(" updated line ##### "+ updatedline)
                fp.write(updatedline)
                #tempString = tempString + updatedline
        fp.close()


def replaceSecRules(secrulesfile, seclistfile,textToReplace):
    contents=""
    try:
        with open (secrulesfile, 'rt') as in_file:
            contents = in_file.read()
    except IOError:
        print("File not Found : ")

    with in_place.InPlace(seclistfile, 'rw') as fp:
        for line in fp:
            fp.write(line.replace(textToReplace, contents))
    fp.close()



parser = argparse.ArgumentParser(description="Takes in a list of subnet names with format \"prod-mt03-129.147.5.0/26\".  It will then create a terraform sec list resource with name \"prod-mt03-129.147.5.0/26.\"  and subnet of \"129.147.5.0/26\" ")
parser.add_argument("--seclistfile",help="Full Path to terraform file for Security List of a given subnet")
parser.add_argument("--secrulesfile",help="csv file with secrules for Security List of a given subnet")
#parser.add_argument("outfile",help="Output Filename")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()


seclistfilename = args.seclistfile
secrulesfilename = args.secrulesfile
totalRowCount = sum(1 for row in csv.DictReader(skipCommentedLine(open(secrulesfilename))))
subnetName = ""

with open(secrulesfilename) as secrulesfile:
        reader = csv.DictReader(skipCommentedLine(secrulesfile))
        columns = reader.fieldnames
        print(totalRowCount)
        rowCount = 0
        maxRulesPerFile = 4
        for row in reader:
                print(row)
                protocol = row['Protocol']
                ruleType = row['RuleType']
                subnetName = row['SubnetName']
                print(protocol + " ...... "+ruleType)
                templatefilename = 'ruletemplate/'+protocol+'_'+ruleType+'_secrule_template.txt'
                print('$$$$$$$  ' + str(rowCount))
                #if rowCount <= totalRowCount:
                tempFileNumber = str(rowCount/maxRulesPerFile + 1 )
                print('file number ::: '+ tempFileNumber )
                tempfilename = 'temp/'+subnetName+ tempFileNumber +'_secrules.txt'
                #print(templatefilename)
                appendRulesTotempfile(tempfilename,templatefilename)
                for column in columns:
                        # print(column)
                        replaceAllplaceholders(tempfilename,'##'+column+'##',row[column])
                rowCount += 1
                #print("################################### "+str(rowCount))


for x in range(1, 5):
        secrulesfile = 'temp/'+subnetName+ str(x) +'_secrules.txt'
        replaceSecRules(secrulesfile,seclistfilename,'###security_rules'+str(x)+'###')
