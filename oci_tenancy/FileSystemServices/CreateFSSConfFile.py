#!/bin/python
import csv
import os
import sys
import argparse
import re
#from backports import configparser
# Entry for 2.x
import ConfigParser

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

parser = argparse.ArgumentParser(description="FSS Input File in CSV Format")
parser.add_argument("--properties",help="Properties File to use. Must have a [FSS] section")
parser.add_argument("--csvfilename",help="FSS CSV file with required details with following columns:Name,AD[1,2,3],path,sourceCIDR,access[READ_ONLY,READ_WRITE],GID,UID,IDSquash[NONE,ALL,ROOT],require_ps_port[true,false]")
parser.add_argument("--fss",help="From Properties File, which Mount Target to use when creating FSS")


if len(sys.argv) != 7:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
csvfilename = args.csvfilename
properties = args.properties
fss = args.fss


if not os.path.exists(properties):
    print("Cant find the properties file in working directory.\nMake sure to create the file and try again.")
    exit(-1)

#Entry for 2.x
config = ConfigParser.RawConfigParser()
#config = configparser.ConfigParser()
config.read(properties)

compartment_ocid = config.get(fss,'mt_comp_var')
mt = config.get(fss,'mt_name')
outputdir = config.get(fss,'mt_outdir')

# Check to see if outfile exists already
if not os.path.exists(outputdir):
    print("FSS Terraform File directory DOES NOT exist.\nPlease create and rerun.")
    exit(-1)


with open(csvfilename) as csvfile:
    reader = csv.reader(skipCommentedLine(csvfile), delimiter=',')
    for row in reader:
        Name = row[0]
        ad = row[1]
        AD = int(ad) - 1
        path = row[2]
        sourceCIDR = row[3]
        access = row[4]
        if access != "READ_WRITE":
            access = "READ_ONLY"
        elif access != "READ_WRITE":
            access = "READ_ONLY"
        elif access == "":
            access = "READ_ONLY"
        gid = row[5]
        if gid == "":
            gid = "65534"
        uid = row[6]
        if uid == "":
            uid = "65534"
        IDSquash = row[7]
        if IDSquash != "":
            IDSquash = "NONE"
        elif IDSquash != "ALL":
            IDSquash = "NONE"
        elif IDSquash != "ROOT":
            IDSquash = "NONE"
        require_ps_port = row[8]
        if require_ps_port != "true":
            require_ps_port = "false"
        elif require_ps_port != "false":
            require_ps_port = "false"

        ofile=open(outputdir +"/" + Name + "_FSS.tf",'w')

        fss_body = """
        resource "oci_file_storage_file_system" \"""" + Name + """" {
            availability_domain = "${lookup(data.oci_identity_availability_domains.ADs.availability_domains[""" + str(AD) + """],"name")}"
            compartment_id = "${""" + compartment_ocid + """}"
            display_name = \""""  + Name + """"
        }

        resource "oci_file_storage_export" \"""" + Name + "-FS1" """" {
            export_set_id = "${oci_file_storage_export_set.""" + mt + """-ES1".id}"
            file_system_id = "${oci_file_storage_file_system.""" + Name + """.id}"
            path = \"""" + path + """"
            export_options = [
                {
                source = \"""" +sourceCIDR + """"
                access = \"""" + access + """"
                anonymous_gid = \"""" + gid + """"
                anonymous_uid = \"""" + uid + """"
                identity_squash = \"""" + IDSquash + """"
                require_privileged_source_port = \"""" + require_ps_port + """"
                }
            ]
        }
        """
        ofile.write(fss_body)
        ofile.close()