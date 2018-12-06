#!/bin/python

import csv
import sys
import argparse
import in_place
import re
import oci
from oci.core.compute_client import ComputeClient


def findQuotes(string, substring):
   return string.find(substring, string.find(substring) + 1)


def replaceAllplaceholders(fileToSearch,textToSearch,textToReplace):
        #print ('testto search : '+textToSearch)
        #print ( 'replace with : ' + textToReplace)
        #print(fileToSearch)
        if textToSearch == '##LBName##':
                textToReplace = textToReplace.replace(" ","_")
        textToReplace = textToReplace.replace(".","-")
        with in_place.InPlace(fileToSearch) as fp:
                for line in fp:
                        if line.strip().startswith('#'):
                                continue
                        #fp.write(line.replace(textToSearch, textToReplace))
                        fp.write(re.sub(textToSearch, textToReplace, line, flags=re.IGNORECASE))
        fp.close()


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


def appendBackendServerfile(fileToSearch,templateFile):
        f1 = open(templateFile)
        s = f1.read()
        #print ('template ::: '+s)
        f1.close()
        f2 = open(fileToSearch, 'a')
        f2.write(s)
        f2.close()



def getBackendServerList(namePattern):
        config = oci.config.from_file()
        compartment_id = config["compartment_id"]
        cc = ComputeClient(config)

        instance_list_response = oci.pagination.list_call_get_all_results(cc.list_instances, compartment_id=compartment_id)
        serverList = []
        base_list =  instance_list_response.data
        #print(len(base_list))
        for instance in base_list:
                instance_id = instance.id
                if re.search(namePattern,instance.display_name,re.IGNORECASE):
                       serverList.append(instance.display_name )


        return serverList

def parseExcludedServerList(excludedFileName):
        with open(excludedFileName) as excludedfile:
                myExcludedServerDict = dict(filter(None, csv.reader(excludedfile)))
                return myExcludedServerDict




parser = argparse.ArgumentParser(description="CSV file name ")
parser.add_argument("--lbbackendfile",help="CSV file with required details with following columns [LBName,LBSize,LBSubnet1,LBSubnet2,LB_BES_Name,LBURL,LBHostName,LBListener]")
parser.add_argument("--excludedServerList",help="CSV file with server to be execluded for each backendset",required=False)

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
cvsfilename = args.lbbackendfile

print (args.excludedServerList )
excludedServerDict = dict()
if args.excludedServerList is not None:
        #print ('args.excludedServerList is not none/ blank')
        excludedServerDict = parseExcludedServerList(args.excludedServerList)

with open(cvsfilename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
                lbname = row['LBName'].replace(" ","_")
                filename = 'terraformfiles/'+lbname+'_Sabre_LBBES_'+row['LB_BES_Name']+'.tf'
                serverList = getBackendServerList(row['BEServerpattren'])
                print(serverList)
                excludedList=list()
                if excludedServerDict.get(row['LB_BES_Name']) is not None:
                        excludedList = list(excludedServerDict.get(row['LB_BES_Name']).lower().split("|"))
                print(excludedList)
                serverList = [n for n in serverList if n not in excludedList]
                print(serverList)
                for server in serverList:
                        appendBackendServerfile( filename,'LBTemplate/lbbackendtemplate.tf')
                        replaceAllplaceholders(filename,'##serverName##',server)
                        for column in columns:
                                # print(column)
                                #filename = row['LBName'].replace(" ","_")
                                replaceAllplaceholders(filename,'##'+column+'##',row[column])
