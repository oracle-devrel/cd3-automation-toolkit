#!/usr/bin/python3
#Author: Suruchi
#Oracle Consulting
#suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


parser = argparse.ArgumentParser(description="Creates TF files for LBR")
parser.add_argument("inputfile",help="Full Path to the CSV file for creating lbr or CD3 excel file. eg lbr.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv)<2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

#If input is csv file; convert to excel
if('.csv' in filename):
        df = pd.read_csv(filename)
        excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
        df.to_excel(excel_writer, 'LBR')
        excel_writer.save()
        filename='tmp_to_excel.xlsx'

df = pd.read_excel(filename, sheet_name='LBR',skiprows=1)
df = df.dropna(how='all')
df = df.reset_index(drop=True)

endNames = {'<END>', '<end>','<End>'}
NaNstr = 'NaN'
lbr_names=[]

for i in df.index:
    region=df.iat[i,0]
    region=region.strip().lower()
    if region in endNames:
        break

    if region not in ct.all_regions:
        print("Invalid Region; It should be one of the regions tenancy is subscribed to")
        continue
    compartment_name = df.iat[i, 1]
    lbr_name = df.iat[i, 2]
    lbr_shape = df.iat[i, 3]
    lbr_subnets= df.iat[i,4].strip()
    lbr_is_private = df.iat[i, 5]
    lbr_listener_name=df.iat[i, 6]
    lbr_be_servers = df.iat[i, 7]
    lbr_be_policy = df.iat[i, 8]
    lbr_be_hc_protocol = df.iat[i, 9]
    lbr_be_hc_port = df.iat[i, 10]
    lbr_be_hc_url = df.iat[i,11]
    lbr_listner_protocol = df.iat[i,12]
    lbr_listner_port = df.iat[i, 13]
    lbr_hostnames = df.iat[i, 14]
    lbr_use_ssl = df.iat[i,15]

    if(str(lbr_use_ssl).lower()==NaNstr.lower()):
        lbr_use_ssl='n'

    lbr_public_cert_file = df.iat[i,16]
    lbr_ca_cert_file = df.iat[i, 17]
    lbr_private_key_file = df.iat[i, 18]
    lbr_passphrase = df.iat[i,19]

    if (str(lbr_use_ssl).lower() == 'y'):
        if (str(lbr_private_key_file).lower() == NaNstr.lower() or str(lbr_public_cert_file).lower() == NaNstr.lower()):
            print("\nERROR!!! if use SSL is y then Public Cert and Private Key fields are manadatory..Exiting")
            exit(1)
    if (str(lbr_ca_cert_file).lower() == NaNstr.lower()):
        lbr_ca_cert_file = lbr_public_cert_file

    if ("HTTP" in str(lbr_be_hc_protocol.upper().strip())):
        if (str(lbr_be_hc_url).lower() == NaNstr.lower()):
            print("Health Check URL Path cannot be null for Health Check Protocol HTTP..exiting...")
            exit(1)

    if (str(compartment_name).lower() == NaNstr.lower() or str(lbr_name).lower() == NaNstr.lower() or str(lbr_shape).lower() == NaNstr.lower()
        or str(lbr_subnets).lower() == NaNstr.lower() or str(lbr_is_private).lower() == NaNstr.lower() or str(lbr_listener_name).lower() ==NaNstr.lower() or str(
        lbr_be_servers).lower() == NaNstr.lower() or str(lbr_be_policy).lower() == NaNstr.lower() or str(lbr_be_hc_protocol).lower() == NaNstr.lower() or str(lbr_be_hc_port).lower() == NaNstr.lower()
        or str(lbr_listner_port).lower() == NaNstr.lower() or str(lbr_listner_protocol).lower() == NaNstr.lower()):
        print("All columns except LBR Hostname, Cert Details are mandatory..exiting...")
        exit(1)


    lbr_be_servers=lbr_be_servers.strip().split(",")

    lbr_subnets = lbr_subnets.strip().split(",")
    subnet_ids = ""
    if (len(lbr_subnets) == 1):
        subnet_ids = "\"${oci_core_subnet." + commonTools.check_tf_variable(lbr_subnets[0].strip()) + ".id}\""
    elif (len(lbr_subnets) == 2):
        subnet_ids = "\"${oci_core_subnet." + commonTools.check_tf_variable(lbr_subnets[0].strip()) + ".id}\",\"${oci_core_subnet." + commonTools.check_tf_variable(lbr_subnets[1].strip()) + ".id}\""


    compartment_name = compartment_name.strip()
    lbr_name = lbr_name.strip()
    compartment_name = commonTools.check_tf_variable(compartment_name)
    lbr_tf_name = commonTools.check_tf_variable(lbr_name)
    lbr_listener_tf_name = commonTools.check_tf_variable(lbr_listener_name)
    lbr_bs_tf_name = lbr_listener_tf_name + "_bs"
    lbr_bs_name= lbr_listener_name+"_bs"

    if(lbr_is_private==0.0):
        lbr_is_private="false"
    elif(lbr_is_private==1.0):
        lbr_is_private="true"

    tempStr=""
    append_listenr=0
    if(lbr_name not in lbr_names):
        lbr_names.append(lbr_name)
        tempStr= """
    #Create LBR
    resource "oci_load_balancer_load_balancer" \"""" + lbr_tf_name + """" {
    #Required
    compartment_id = "${var.""" + compartment_name + """}" 
    display_name = \"""" + lbr_name + """" 
    shape = \"""" + lbr_shape.strip() + """" 
    subnet_ids = [ """ + subnet_ids + """ ]
    is_private = """+ str(lbr_is_private).lower().strip() + """ 
    }
    """
    else:
        append_listenr=1
    tempStr=tempStr+"""

    #Create Backend Set
    resource "oci_load_balancer_backend_set"  \"""" + lbr_bs_tf_name.strip() + """" {
    #Required
    health_checker {
        #Required
        protocol =  \"""" + lbr_be_hc_protocol.upper().strip() + """" 
        #Optional
        port =  \"""" + str(lbr_be_hc_port).strip() + """" 
    """
    if(lbr_be_hc_protocol.upper().strip()=="HTTP"):
        tempStr=tempStr+"""
        url_path = \"""" + lbr_be_hc_url.strip() + """"
    """
    tempStr=tempStr+"""
    }
    load_balancer_id = "${oci_load_balancer_load_balancer."""+lbr_tf_name+""".id}"
    name = \"""" + lbr_bs_name.strip() + """"
    policy = \"""" + lbr_be_policy.upper().strip() + """"
    }
    """
    tempStr_be_server = ""
    cnt=0
    for lbr_be_server in lbr_be_servers:
        if(lbr_be_server!=""):
            cnt=cnt+1
            serverinfo=lbr_be_server.strip().split(":")
            servername=serverinfo[0].strip()
            serverport=serverinfo[1].strip()
            e = servername.count(".")
            if(e==3):
                be_server_ip_address=servername
            else:
                be_server_ip_address="${oci_core_instance."+servername+".private_ip}"

            lbr_be_server_res_name=lbr_listener_tf_name+"_bes_"+str(cnt)

            tempStr_be_server=tempStr_be_server+"""
    #Create Backend Server
    resource "oci_load_balancer_backend" \"""" + lbr_be_server_res_name.strip() + """"  {
    #Required
    backendset_name = "${oci_load_balancer_backend_set."""+lbr_bs_tf_name.strip()+""".name}"
    ip_address = \"""" + be_server_ip_address + """" 
    load_balancer_id = "${oci_load_balancer_load_balancer."""+lbr_tf_name+""".id}"
    port = \"""" + serverport.strip() + """" 
}"""
    tempStr=tempStr+tempStr_be_server
    configure_hostname=0
    if (str(lbr_hostnames).lower() != NaNstr.lower()):
        lbr_hostnames=lbr_hostnames.strip().split(",")
        configure_hostname=1
        tempStr_hostname = """
    hostname_names = ["""
        c = 0
        for lbr_hostname in lbr_hostnames:
            if(lbr_hostname!=""):
                lbr_hostname=lbr_hostname.strip()
                c = c + 1
                lbr_host_tf_name = lbr_listener_tf_name + "_hostname_"+str(c)
                lbr_host_display_name=lbr_listener_name + "_hostname_"+str(c)
                tempStr = tempStr + """
    #Create LBR hostname
    resource "oci_load_balancer_hostname" \"""" + lbr_host_tf_name.strip() + """"  {
    #Required
    hostname = \"""" + lbr_hostname.strip() + """" 
    load_balancer_id = "${oci_load_balancer_load_balancer.""" + lbr_tf_name + """.id}"
    name = \"""" + lbr_host_display_name.strip() + """" 
}
    """
                if(c<len(lbr_hostnames)):
                    tempStr_hostname=tempStr_hostname+"""\"${oci_load_balancer_hostname."""+lbr_host_tf_name.strip()+""".name}", """
                else:
                    tempStr_hostname=tempStr_hostname+"""\"${oci_load_balancer_hostname."""+lbr_host_tf_name.strip()+""".name}"]"""


    if (lbr_use_ssl.lower() == 'y'):
        lbr_cert_tf_name = lbr_listener_tf_name + "_cert"
        lbr_cert_name=lbr_listener_name + "_cert"

        tempStr = tempStr + """
    resource "oci_load_balancer_certificate" \"""" + lbr_cert_tf_name.strip() + """"  {
    # Required
    certificate_name = \"""" + lbr_cert_name.strip() + """" 
    load_balancer_id = "${oci_load_balancer_load_balancer.""" + lbr_tf_name + """.id}"
    # Optional
"""
        if(str(lbr_ca_cert_file).lower()!=NaNstr.lower()):
            tempStr=tempStr+"""
    ca_certificate = "${file(\""""+lbr_ca_cert_file+"""")}"
"""
        if(str(lbr_passphrase).lower()!=NaNstr.lower()):
            tempStr=tempStr+"""
    passphrase = \"""" + lbr_passphrase + """"
"""
        if(str(lbr_private_key_file).lower()!=NaNstr.lower()):
            tempStr=tempStr+"""
    private_key = "${file(\""""+lbr_private_key_file+"""")}"
"""
        if(str(lbr_public_cert_file).lower()!=NaNstr.lower()):
            tempStr=tempStr+"""
    public_certificate = "${file(\""""+lbr_public_cert_file+"""")}"
"""
        tempStr=tempStr+"""
    lifecycle {
        create_before_destroy = true
    }
}
"""

    tempStr=tempStr+"""
    #Create LBR listener
    resource "oci_load_balancer_listener" \"""" + lbr_listener_tf_name.strip() + """"   {
    #Required
    default_backend_set_name = "${oci_load_balancer_backend_set."""+lbr_bs_tf_name.strip()+""".name}"
    load_balancer_id = "${oci_load_balancer_load_balancer."""+lbr_tf_name+""".id}"
    name = \"""" + lbr_listener_name.strip() + """"
    port = \"""" + str(lbr_listner_port).strip() + """"
    protocol = \"""" + lbr_listner_protocol.upper().strip() + """"
"""
    if (configure_hostname == 1):
            tempStr=tempStr+tempStr_hostname

    if (lbr_use_ssl.lower()=='y'):
        tempStr = tempStr + """
    ssl_configuration {
        certificate_name = "${oci_load_balancer_certificate."""+lbr_cert_tf_name.strip()+""".certificate_name}"
    }
"""
    tempStr=tempStr+"""
}
"""

    outfile = outdir + "/" + region + "/" + lbr_tf_name + "_lbr.tf"
    if(append_listenr==0):
        oname = open(outfile, "w")
        print("Writing " + outfile)

    else:
        oname = open(outfile, "a")
        print("Appending " + outfile)
    oname.write(tempStr)
    oname.close()

#Remove temporary file created
if('tmp_to_excel.xlsx' in filename):
    os.remove(filename)

