#!/usr/bin/python3
# Author: Suruchi Singla
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import configparser
import pandas as pd
import re
import os
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet and which component(SGW, NGW, IGW) is required for which subnet
# Outfile
######

parser = argparse.ArgumentParser(description="Creates route tables containing default routes for each subnet based on inputs given in vcn-info.properties.")
parser.add_argument("inputfile", help="Full Path of properties file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outdir", help="Output directory for creation of TF files")
parser.add_argument("--modify_network", help="Modify: true or false", required=False)
parser.add_argument("--nongf_tenancy", help="non greenfield tenancy: true or false", required=False)


if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
nongf_tenancy = args.nongf_tenancy
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"

outfile={}
oname={}
routetablefiles = {}
lisoffiles = []

ADS = ["AD1", "AD2", "AD3"]
fname = None
#Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING


def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." +  os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

def createLPGRouteRules(peering_dict):
    for left_vcn, value in peering_dict.items():
        right_vcns = value.split(",")
        left_vcn_tf_name = commonTools.tfname.sub("-", left_vcn)

        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            right_vcn = right_vcn.strip()
            right_vcn_tf_name = commonTools.tfname.sub("-", right_vcn)

            # Build rule for VCN on left
            #lpg_name = left_vcn + "_" + right_vcn + "_lpg"
            lpg_name = vcns.vcn_lpg_names1[left_vcn][0]
            lpg_name=left_vcn+"_"+lpg_name
            lpg_name_tf_name = commonTools.tfname.sub("-", lpg_name)

            vcns.vcn_lpg_names1[left_vcn].pop(0)
            ruleStr = """
                    route_rules { 
                        destination = "${oci_core_vcn.""" + right_vcn_tf_name + """.cidr_block}"
                        network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
            vcns.vcn_lpg_rules[left_vcn] = vcns.vcn_lpg_rules[left_vcn] + ruleStr

            # Build rule for VCNs on right
            #lpg_name = right_vcn + "_" + left_vcn + "_lpg"
            lpg_name=vcns.vcn_lpg_names1[right_vcn][0]
            lpg_name=right_vcn+"_"+lpg_name
            lpg_name_tf_name = commonTools.tfname.sub("-", lpg_name)

            vcns.vcn_lpg_names1[right_vcn].pop(0)

            ruleStr = """
                    route_rules { 
                        destination = "${oci_core_vcn.""" + left_vcn_tf_name + """.cidr_block}"
                        network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
            vcns.vcn_lpg_rules[right_vcn] = vcns.vcn_lpg_rules[right_vcn] + ruleStr


def createDRGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,region):
    if(vcns.vcn_drgs[hub_vcn_name]=='y'):
        #rt_tmp = hub_vcn_name+"_"+hub_vcn_name + "_drg_rt"
        drg_name = hub_vcn_name + "_drg"
    elif(vcns.vcn_drgs[hub_vcn_name]!='n'):
        #rt_tmp=hub_vcn_name+"_"+vcns.vcn_drgs[hub_vcn_name]+"_rt"
        drg_name=vcns.vcn_drgs[hub_vcn_name]
    elif(vcns.vcn_drgs[hub_vcn_name]=='n'):
        print("drg_required column for VCN "+hub_vcn_name +" marked as Hub should not be set to n!!\n")
        return

    drg_rt_name=""
    #if (nongf_tenancy == "true"):
    if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
        with open(outdir + "/" + region + "/obj_names.safe") as f:
            for line in f:
                if ("drginfo::::" + hub_vcn_name + "::::" + drg_name in line):
                    drg_rt_name = line.split("::::")[3].strip()

    if(drg_rt_name==""):
        #rt_var=rt_tmp
        rt_display="Route Table associated with DRG-""" + drg_name
        rt_var=hub_vcn_name+"_"+rt_display
    else:
        rt_var = hub_vcn_name + "_" + drg_rt_name
        rt_display=drg_rt_name

    rt_tf_name=commonTools.tfname.sub("-",rt_var)
    hub_vcn_tf_name=commonTools.tfname.sub("-",hub_vcn_name)

    outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")

    drgRuleStr=""
    for right_vcn in right_vcns:
        if (right_vcn == ""):
            continue
        if right_vcn in vcns.spoke_vcn_names:
            right_vcn_tf_name = commonTools.tfname.sub("-", right_vcn)
            # lpg_name = hub_vcn_name + "_" + right_vcn + "_lpg"
            lpg_name = vcns.vcn_lpg_names2[hub_vcn_name][0]
            lpg_name = hub_vcn_name + "_" + lpg_name
            lpg_tf_name = commonTools.tfname.sub("-", lpg_name)
            vcns.vcn_lpg_names2[hub_vcn_name].pop(0)
            tempstr ="""
        route_rules {
                destination ="${oci_core_vcn.""" + right_vcn_tf_name + """.cidr_block}"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_tf_name + """.id}"
                destination_type = "CIDR_BLOCK"
            }
            """
            if (os.path.exists(outfile)):
                filedata = open(outfile, "r").read()
                if tempstr not in filedata:
                    srcStr="##Add More rules for subnet " + rt_tf_name + "##"
                    tempstr = tempstr + srcStr
                    filedata=filedata.replace(srcStr,tempstr)
                    oname=open(outfile, "w")
                    oname.write(filedata)
                    oname.close()

            else:
                oname = open(outfile, "w")
                drgStr = """ 
        resource "oci_core_route_table" \"""" + rt_tf_name + """"{
                compartment_id = "${var.""" + compartment_var_name + """}"
                vcn_id = "${oci_core_vcn.""" + hub_vcn_tf_name + """.id}"
                display_name =\"""" + rt_display + """"
                
                ##Add More rules for subnet """ + rt_tf_name + """##
                """+tempstr+ """
        }"""
                oname.write(drgStr)
                oname.close()

    if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
        routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

def createLPGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,region):
    #Retain exported route tables associated with exported LPGs
    # if (nongf_tenancy == "true"):
    if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
        with open(outdir + "/" + region + "/obj_names.safe") as f:
            for line in f:
                if ("lpginfo::::" + hub_vcn_name in line):
                    lpg_rt_name = line.split("::::")[3].strip()
                    rt_var = hub_vcn_name + "_" + lpg_rt_name
                    rt_tf_name = commonTools.tfname.sub("-", rt_var)
                    if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                        routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

    #Create Rt table String for new spoke VCNs
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")
    for right_vcn in right_vcns:
        if (right_vcn == ""):
            continue
        if(right_vcn in vcns.spoke_vcn_names):
            lpg_name = vcns.vcn_lpg_names3[hub_vcn_name][0]
            vcns.vcn_lpg_names3[hub_vcn_name].pop(0)
            #rt_var = hub_vcn_name + "_" + lpg_name + "_rt"
            rt_display = "Route Table associated with LPG-""" + lpg_name
            rt_var=hub_vcn_name+"_"+rt_display
            rt_tf_name = commonTools.tfname.sub("-", rt_var)
            hub_vcn_tf_name = commonTools.tfname.sub("-", hub_vcn_name)

            outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"
            oname = open(outfile, "w")
            lpgStr = """ 
            resource "oci_core_route_table" \"""" + rt_tf_name + """"{
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    vcn_id = "${oci_core_vcn.""" + hub_vcn_tf_name + """.id}"
                    display_name =\"""" + rt_display + """"
                    
                    ##Add More rules for subnet """ + rt_tf_name + """##
                """
            drg_name=""
            if (vcns.vcn_drgs[hub_vcn_name] == 'y'):
                drg_name = hub_vcn_name + "_drg"
            elif (vcns.vcn_drgs[hub_vcn_name] != 'n'):
                drg_name = vcns.vcn_drgs[hub_vcn_name]

            if(drg_name!=""):
                drg_tf_name = commonTools.tfname.sub("-", drg_name)
                for drg_destination in vcnInfo.onprem_destinations:
                    if (drg_destination != ''):
                        lpgStr = lpgStr + """
                    route_rules { 
                        destination = \"""" + drg_destination.strip() + """\"
                        network_entity_id = "${oci_core_drg.""" + hub_vcn_tf_name+"_"+drg_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                    """

            lpgStr = lpgStr + """
        }"""
            oname.write(lpgStr)
            oname.close()
            if(rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

def prepareSGWRuleStr(sgw_name,configure_sgw):
    vcn_tf_name = commonTools.tfname.sub("-", vcn_name)
    sgw_tf_name = commonTools.tfname.sub("-", sgw_name)
    data=""
    if(configure_sgw=="all_services"):
        data = data+ """
                    route_rules { 
                        destination = contains(split("-","${data.oci_core_services.oci_services.services.0.cidr_block}"),"all") == true ? "${data.oci_core_services.oci_services.services.0.cidr_block}" : "${data.oci_core_services.oci_services.services.1.cidr_block}"
                        network_entity_id = "${oci_core_service_gateway.""" + vcn_tf_name+"_"+sgw_tf_name + """.id}"
                        destination_type = "SERVICE_CIDR_BLOCK"
                        }
                        """

    elif(configure_sgw=="object_storage"):
        data = data + """
                    route_rules { 
                        destination = contains(split("-","${data.oci_core_services.oci_services.services.0.cidr_block}"),"objectstorage") == true ? "${data.oci_core_services.oci_services.services.0.cidr_block}" : "${data.oci_core_services.oci_services.services.1.cidr_block}"
                        network_entity_id = "${oci_core_service_gateway.""" + vcn_tf_name + "_" + sgw_tf_name + """.id}"
                        destination_type = "SERVICE_CIDR_BLOCK"
                        }
                        """
    return data

def prepareNGWRuleStr(ngw_name):
    vcn_tf_name = commonTools.tfname.sub("-", vcn_name)
    ngw_tf_name = commonTools.tfname.sub("-", ngw_name)
    data=""
    for ngw_destination in vcnInfo.ngw_destinations:
            if (ngw_destination != ''):
                data = data+""" 
                    route_rules { 
                        destination = \"""" + ngw_destination + """\"
                        network_entity_id = "${oci_core_nat_gateway.""" + vcn_tf_name+"_"+ngw_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
    return data

def prepareIGWRuleStr(igw_name):
    vcn_tf_name = commonTools.tfname.sub("-", vcn_name)
    igw_tf_name = commonTools.tfname.sub("-", igw_name)

    data=""
    for igw_destination in vcnInfo.igw_destinations:
            if (igw_destination != ''):
                data = data + """
                    route_rules { 
                        destination = \"""" + igw_destination + """\"
                        network_entity_id = "${oci_core_internet_gateway.""" + vcn_tf_name+"_"+igw_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
    return data

def prepareOnpremRuleStr(drg_name):
    data=""
    if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'hub':
        vcn_tf_name = commonTools.tfname.sub("-", vcn_name)
        drg_tf_name = commonTools.tfname.sub("-", drg_name)
        for drg_destination in vcnInfo.onprem_destinations:
            if (drg_destination != ''):
                data = data + """
                    route_rules { 
                        destination = \"""" + drg_destination.strip() + """\"
                        network_entity_id = "${oci_core_drg.""" + vcn_tf_name+"_"+drg_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """

    if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'spoke':
        """for left_vcn, value in peering_dict.items():
            right_vcns = value.split(",")
            for right_vcn in right_vcns:
                if (right_vcn == vcn_name):
                    hub_vcn_name = left_vcn
                    break

        lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"""""
        lpg_name = vcns.vcn_lpg_names[vcn_name][0]
        lpg_name=vcn_name+"_"+lpg_name
        lpg_tf_name = commonTools.tfname.sub("-", lpg_name)
        for drg_destination in vcnInfo.onprem_destinations:
            if (drg_destination != ''):
                data = data + """
                    route_rules { 
                        destination = \"""" + drg_destination.strip() + """\"
                        network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_tf_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
    return data

def prepareVCNPeerRuleStr():
    data=""
    data = data + vcns.vcn_lpg_rules[vcn_name]
    return data


def processSubnet(region,vcn_name,rt_name,AD,configure_sgw,configure_ngw,configure_igw,configure_onprem,configure_vcnpeering):
    # Route Table name specifiied as 'n' - dont create any routetable
    if (rt_name == "n"):
        return

    if (AD.strip().lower() != 'regional'):
        AD=AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    # check if subnet codr needs to be attached
    if (vcnInfo.subnet_name_attach_cidr == 'y'):
        if (str(ad_name) != ''):
            name1 = rt_name + "-ad" + str(ad_name)
        else:
            name1 = rt_name
        display_name = name1 + "-" + subnet
    else:
        display_name = rt_name

    vcn_tf_name=commonTools.tfname.sub("-",vcn_name)
    subnet_tf_name=commonTools.tfname.sub("-",display_name)

    #Create Route Table File Name
    outfile = outdir + "/" + region + "/" + vcn_tf_name+"_"+subnet_tf_name + "_routetable.tf"
    if (vcn_tf_name + "_" + subnet_tf_name + "_routetable.tf" in routetablefiles[region]):
        routetablefiles[region].remove(vcn_tf_name + "_" + subnet_tf_name + "_routetable.tf")

    #Get VCN component names
    vcn_drg = vcns.vcn_drgs[vcn_name]
    drg_name=""
    if (vcn_drg == "y"):
        drg_name = vcn_name + "_drg"
    elif (vcn_drg != "n"):
        drg_name = vcn_drg

    vcn_igw = vcns.vcn_igws[vcn_name]
    igw_name=""
    if (vcn_igw == "y"):
        igw_name = vcn_name + "_igw"
    elif (vcn_igw != "n"):
        igw_name = vcn_igw

    vcn_ngw = vcns.vcn_ngws[vcn_name]
    ngw_name=""
    if (vcn_ngw == "y"):
        ngw_name = vcn_name + "_ngw"
    elif (vcn_ngw != "n"):
        ngw_name = vcn_ngw

    vcn_sgw = vcns.vcn_sgws[vcn_name]
    sgw_name=""
    if (vcn_sgw == "y"):
        sgw_name = vcn_name + "_sgw"
    elif (vcn_sgw != "n"):
        sgw_name = vcn_sgw

    #Prepare rule str
    data_sgw = prepareSGWRuleStr(sgw_name,configure_sgw)
    data_ngw = prepareNGWRuleStr(ngw_name)
    data_igw = prepareIGWRuleStr(igw_name)
    data_onprem = prepareOnpremRuleStr(drg_name)
    data_vcnpeer = prepareVCNPeerRuleStr()

    dataStr = """
                #SubnetRules Start"""
    if configure_sgw.strip() == 'all_services' or configure_sgw.strip() == 'object_storage' and vcn_sgw != 'n':
        dataStr = dataStr + data_sgw
    if configure_ngw.strip() == 'y' and vcn_ngw != 'n':
        dataStr = dataStr + data_ngw
    if configure_igw.strip() == 'y' and vcn_igw != 'n':
        dataStr = dataStr + data_igw
    if configure_onprem.strip() == 'y':
        if (vcn_name in vcns.hub_vcn_names or vcn_name in vcns.spoke_vcn_names):
            dataStr = dataStr + data_onprem
    if (configure_vcnpeering.strip() == 'y' and vcns.vcn_lpg_rules[vcn_name] != ''):
        dataStr = dataStr + data_vcnpeer
    dataStr = dataStr + """
                #SubnetRules End
                """

    # Either same route table name is used for subsequent subnets or Modify Network is set to true - Add rules modified to y
    # and remove rules modified to n
    if (os.path.exists(outfile)):# and modify_network == 'true'):
        newlines=[]
        with open(outfile, 'r') as file:
            copy=True
            for line in file:
                if line.strip() == "#SubnetRules Start":
                    copy=False
                    newlines.append(dataStr)
                    continue
                elif(line.strip() == "#SubnetRules End"):
                    copy=True
                    continue
                elif copy:
                    newlines.append(line)
            file.close()
        with open(outfile, 'w') as file:
            file.writelines(newlines)
            file.close()
        return

    #New routetable
    oname = open(outfile, "w")
    data_res = """ 
            resource "oci_core_route_table" \"""" +vcn_tf_name+"_"+ subnet_tf_name + """"{
                compartment_id = "${var.""" + compartment_var_name + """}"
                vcn_id = "${oci_core_vcn.""" + vcn_tf_name + """.id}"
                display_name = \"""" + display_name.strip() + """\" """

    end="""
            ##Add More rules for subnet """ + vcn_tf_name+"_"+subnet_tf_name + """##
            }
            """
    tempStr=data_res+dataStr+end
    oname.write(tempStr)
    oname.close()
    print(outfile + " containing TF for routerules has been created for region " + region)

#If input is CD3 excel file
if('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Purge existing routetable files
    if (modify_network == 'false'):
        for reg in vcnInfo.all_regions:
            routetablefiles.setdefault(reg, [])
            purge(outdir + "/" + reg, "_routetable.tf")


    # Get existing list of route table files
    if(modify_network == 'true'):
        for reg in vcnInfo.all_regions:
            routetablefiles.setdefault(reg,[])
            lisoffiles = os.listdir(outdir + "/" + reg)
            for file in lisoffiles:
                if "_routetable.tf" in file:
                    routetablefiles[reg].append(file)

    # Create LPG Rules
    createLPGRouteRules(vcns.peering_dict)

    # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
    for hub_vcn_name in vcns.hub_vcn_names:
        compartment_var_name = vcns.vcn_compartment[hub_vcn_name]
        #String for Route Table Assocaited with DRG
        r = vcns.vcn_region[hub_vcn_name].strip().lower()
        createDRGRtTableString(compartment_var_name,hub_vcn_name,vcns.peering_dict,r)

    # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
    for hub_vcn_name in vcns.hub_vcn_names:
        compartment_var_name = vcns.vcn_compartment[hub_vcn_name]
        r = vcns.vcn_region[hub_vcn_name].strip().lower()
        #String for Route Table Associated with each LPG in hub VCN peered with Spoke VCN
        createLPGRtTableString(compartment_var_name,hub_vcn_name,vcns.peering_dict,r)

    # Start processing for each subnet
    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    for i in df.index:
        # Get subnet data
        region = df.iat[i,0]
        if (region in commonTools.endNames):
            break
        compartment_var_name = df.iat[i, 1]
        region = region.strip().lower()
        if region not in vcnInfo.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the values mentioned in VCN Info tab..Exiting!")
            exit(1)
        vcn_name = str(df['vcn_name'][i]).strip()
        if (vcn_name.strip() not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
            exit(1)
        name = df.iat[i, 3]
        subnet = df.iat[i, 4]
        AD = df.iat[i, 5]
        pubpvt = df.iat[i, 6]
        dhcp = df.iat[i, 7]
        rt_name=df.iat[i,8]

        configure_sgw = df.iat[i, 11]
        configure_ngw = df.iat[i, 12]
        configure_igw = df.iat[i, 13]
        configure_onprem = df.iat[i, 14]
        configure_vcnpeering = df.iat[i,15]

        # Check to see if any column is empty in Subnets Sheet
        if (str(compartment_var_name).lower() == 'nan' or str(vcn_name).lower() == 'nan' or
                str(name).lower() == 'nan' or str(subnet).lower() == 'nan'
                or str(AD).lower() == 'nan' or str(pubpvt).lower() == 'nan'
                or str(configure_sgw).lower() == 'nan' or str(configure_ngw).lower() == 'nan'
                or str(configure_igw).lower() == 'nan' or str(configure_onprem).lower() == 'nan' or str(configure_vcnpeering).lower() == 'nan'):
            print("\nERROR!!! Column Values (except dhcp_option_name, route_table_name, seclist_name, common_seclist_name or dns_label) or Rows cannot be left empty in Subnets sheet in CD3..Exiting!")
            exit(1)

        compartment_var_name=compartment_var_name.strip()
        configure_sgw=configure_sgw.strip().lower()
        configure_ngw = configure_ngw.strip().lower()
        configure_igw = configure_igw.strip().lower()
        configure_onprem = configure_onprem.strip().lower()
        configure_vcnpeering = configure_vcnpeering.strip().lower()
        subnet=subnet.strip()
        name=name.strip()
        if (str(rt_name).lower() != 'nan'):
            rt_name=rt_name.strip()
        else:
            # route table not provided; use subnet name as route table name
            rt_name=name

        processSubnet(region, vcn_name, rt_name,AD,configure_sgw, configure_ngw, configure_igw, configure_onprem, configure_vcnpeering)

    #remove any extra route table files (not part of latest cd3)
    for reg in vcnInfo.all_regions:
        for remaining_rt_file in routetablefiles[reg]:
            print("Removing "+outdir+"/"+reg+"/"+remaining_rt_file)
            os.remove(outdir+"/"+reg+"/"+remaining_rt_file)
            #routetablefiles[reg].remove(remaining_rt_file)


# If CD3 excel file is not given as input
elif('.properties' in filename):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
    drg_ocid = config.get('Default', 'drg_ocid')
    onprem_destinations = config.get('Default', 'drg_subnet')
    #onprem_destinations = onprem_destinations.split(",")
    if (onprem_destinations == ''):
        print("\ndrg_subnet should not be left empty.. It will create empty route tables")
    else:
        onprem_destinations = onprem_destinations.split(",")

    ngw_destinations = config.get('Default', 'ngw_destination')
    if (ngw_destinations == ''):
        ngw_destinations = '0.0.0.0/0'
    ngw_destinations = ngw_destinations.split(",")

    igw_destinations = config.get('Default', 'igw_destination')
    if (igw_destinations == ''):
        igw_destinations = '0.0.0.0/0'
    igw_destinations = igw_destinations.split(",")

    all_regions = config.get('Default', 'regions')
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]


    # Purge existing routetable files
    if (subnet_add == 'false'):
        for reg in all_regions:
            purge(outdir + "/" + reg, "routetable.tf")

    # Get VCN Info from VCN_INFO section
    vcns = config.options('VCN_INFO')
    for vcn_name in vcns:
        vcn_lpg_rules.setdefault(vcn_name, '')
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        hub_spoke_none = vcn_data[6].strip().lower()
        compartment_var_name = vcn_data[12].strip()
        vcn_compartment[vcn_name]=compartment_var_name
        region=vcn_data[0].strip().lower()
        if region not in all_regions:
            print("Invalid Region")
            exit(1)
        vcn_region[vcn_name]=region

        if (vcn_data[2].strip().lower() != 'n'):
            vcn_drgs[vcn_name] = vcn_data[2].strip().lower()

        if (hub_spoke_none == 'hub'):
            hub_vcn_names.append(vcn_name)
        if (hub_spoke_none == 'spoke'):
            spoke_vcn_names.append(vcn_name)

    # Creating route rules for LPGs as per Section VCN_PEERING
    peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_cidr=peering_dict['ocs_vcn_cidr']
    peering_dict.pop('ocs_vcn_lpg_ocid')
    peering_dict.pop('ocs_vcn_cidr')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('add_ping_sec_rules_vcnpeering')

    createLPGRouteRules(peering_dict)

    # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
    #if (subnet_add == 'false'):
    for hub_vcn_name in hub_vcn_names:
        compartment_var_name = vcn_compartment[hub_vcn_name]

            # String for Route Table Assocaited with DRG
        r = vcn_region[hub_vcn_name].strip().lower()
        createDRGRtTableString(compartment_var_name, hub_vcn_name, peering_dict,r)


        # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
    for hub_vcn_name in hub_vcn_names:
        compartment_var_name = vcn_compartment[hub_vcn_name]
        r = vcn_region[hub_vcn_name].strip().lower()

            # String for Route Tavle Associated with each LPG in hub VCN peered with Spoke VCN
        createLPGRtTableString(compartment_var_name, hub_vcn_name, peering_dict,r)


    #Start processing each VCN
    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')

        region = vcn_data[0].strip().lower()
        vcn_cidr = vcn_data[1].strip().lower()
        vcn_drg = vcn_data[2].strip().lower()
        if (vcn_drg == "y"):
            drg_name = vcn_name + "_drg"
        elif (vcn_drg != "n"):
            drg_name = vcn_drg

        vcn_igw = vcn_data[3].strip().lower()
        if (vcn_igw == "y"):
            igw_name = vcn_name + "_igw"
        elif (vcn_igw != "n"):
            igw_name = vcn_igw

        vcn_ngw = vcn_data[4].strip().lower()
        if (vcn_ngw == "y"):
            ngw_name = vcn_name + "_ngw"
        elif (vcn_ngw != "n"):
            ngw_name = vcn_ngw

        vcn_sgw = vcn_data[5].strip().lower()
        if (vcn_sgw == "y"):
            sgw_name = vcn_name + "_sgw"
        elif (vcn_sgw != "n"):
            sgw_name = vcn_sgw

        hub_spoke_none = vcn_data[6].strip().lower()

        vcn_subnet_file = vcn_data[7].strip().lower()
        if os.path.isfile(vcn_subnet_file)==False:
            print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping Route TF creation for this VCN.")
            continue
        fname = open(vcn_subnet_file, "r")


        ruleStr = ""
        #Add DRG rules (this will add rules to hub vcn since for hub vcn drg_required is set to y
        if (vcn_drg =="y" and onprem_destinations!=''):
            if(drg_ocid==''):
                for drg_destination in onprem_destinations:
                    if(drg_destination!=''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
            if(drg_ocid!=''):
                for drg_destination in onprem_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id =  \"""" + drg_ocid + """"
                destination_type = "CIDR_BLOCK"
                }
                """

        #Add DRG rules to each Spoke VCN
        if (hub_spoke_none=='spoke' and onprem_destinations!=''):
            for left_vcn, value in peering_dict.items():
                right_vcns = value.split(",")
                for right_vcn in right_vcns:
                    if (right_vcn == vcn_name):
                        hub_vcn_name = left_vcn
                        break

            lpg_name=vcn_name+"_"+hub_vcn_name+"_lpg"
            for drg_destination in onprem_destinations:
                if(drg_destination!=''):
                    ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """

        # Add LPG rules
        if(vcn_lpg_rules[vcn_name]!=''):
            ruleStr=ruleStr+vcn_lpg_rules[vcn_name]

        # Read input subnet file
        for line in fname:
            if not line.startswith('#') and line !='\n':
                # print "processing : " + line
                subnet = ""
                name = ""

                [compartment_var_name, name, sub, AD, pubpvt, dhcp, rt_name,seclist_name,common_seclist_name,configure_sgw, configure_ngw, configure_igw,dns_label] = line.split(',')
                linearr = line.split(",")
                compartment_var_name = linearr[0].strip()
                name = linearr[1].strip()
                subnet = linearr[2].strip()


                processSubnet(region,vcn_name,name,rt_name.strip(),ruleStr,AD,configure_sgw,configure_ngw,configure_igw,vcn_sgw,vcn_ngw,vcn_igw)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit()

if(fname!=None):
    fname.close()

