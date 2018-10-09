#!/bin/python
import csv  
import shutil
import sys
import argparse
import in_place
import re

def print_by_field(row):
    print(row)
	
def copy_template_file(hostname,operatingsystem):
	print('template/'+operatingsystem+'template.tf')
	shutil.copyfile('template/'+operatingsystem+'template.tf', '/root/dll-group/oci_tenancy/terraform_files/'+hostname+'.tf')  

#def readPublicKey(filename):
#	with open(filename, 'r') as f:
#		key = f.read()
#		#result = key.index('== ')
#		#key=key[0:result+2]
#		return (key.strip())

def findQuotes(string, substring):
   return string.find(substring, string.find(substring) + 1)
   
def readPublicKey(filename):
	with open(filename, 'r') as f:
		# read the pem file as string
		chromepem = f.readlines()
		# remove header/footer lines which say that this is a key
		chromepem = chromepem[1:-1]
		# And we need the output to be a string
		chromepem = ''.join(chromepem)
		# The newlines aren't necessary, so we'll remove them
		chromepem = chromepem.replace("\n","")
		# not sure why, but it looks like the first 40 characters aren't necessary.
		# removing them seems to create a consistent public key anyway...
		indexComma = findQuotes(chromepem,"\"")+1
		key = chromepem[indexComma:]
		return (key)
	
def replaceAllplaceholders(fileToSearch,textToSearch,textToReplace):
	#print ('testto search : '+textToSearch)
	#print ( 'replace with : ' + textToReplace)
#	if textToSearch=='##SSH-key-filepath##':
#		print ('trasform key : '+textToSearch)
#		textToReplace=readPublicKey(textToReplace)
#		print (textToReplace)
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
parser.add_argument("cvsfilename",help="CSV file with required details with following columns [Hostname,Availability Domain,subnet name,Pub Address,IP Address,OS,Shape,SSH-key-filepath]")

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
		copy_template_file(row['Hostname'],row['OS'])
		for column in columns:
			# print(column)
			replaceAllplaceholders('/path-to-terraform/'+row['Hostname']+'.tf','##'+column+'##',row[column])

		


