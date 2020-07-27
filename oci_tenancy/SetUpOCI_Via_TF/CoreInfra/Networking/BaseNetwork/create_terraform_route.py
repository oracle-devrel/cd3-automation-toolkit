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

sys.path.append(os.getcwd() + "/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

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
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) < 3:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
if args.modify_network is not None:
    modify_network = str(args.modify_network)
else:
    modify_network = "false"
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName = ""

ct = commonTools()
ct.get_subscribedregions(configFileName)

outfile = {}
oname = {}
routetablefiles = {}
lisoffiles = []
tempStr={}

ADS = ["AD1", "AD2", "AD3"]
fname = None

# Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader,keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('route-table-template')
routerule = env.get_template("route-rule-template")

def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." + os.path.join(dir, f))
            os.remove(os.path.join(dir, f))


def createLPGRouteRules(peering_dict):
    for left_vcn, value in peering_dict.items():
        right_vcns = value.split(",")
        left_vcn_tf_name = commonTools.check_tf_variable(left_vcn)

        for right_vcn in right_vcns:
            if (right_vcn == ""):
                continue
            right_vcn = right_vcn.strip()
            right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)

            # Build rule for VCN on left
            lpg_name = vcns.vcn_lpg_names1[left_vcn][0]

            lpg_name = left_vcn + "_" + lpg_name
            lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

            vcns.vcn_lpg_names1[left_vcn].pop(0)
            tempStr['destination']= "oci_core_vcn."+right_vcn_tf_name+".cidr_block"
            tempStr['lpg_vcn_name']=lpg_name_tf_name
            tempStr['destination_type']="CIDR_BLOCK"
            tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_name_tf_name+".id"
            ruleStr = routerule.render(tempStr)

            vcns.vcn_lpg_rules[left_vcn] = vcns.vcn_lpg_rules[left_vcn] + ruleStr

            # Build rule for VCNs on right
            # lpg_name = right_vcn + "_" + left_vcn + "_lpg"
            lpg_name = vcns.vcn_lpg_names1[right_vcn][0]
            lpg_name = right_vcn + "_" + lpg_name
            lpg_name_tf_name = commonTools.check_tf_variable(lpg_name)

            vcns.vcn_lpg_names1[right_vcn].pop(0)
            tempStr['destination']= "oci_core_vcn."+left_vcn_tf_name+".cidr_block"
            tempStr['lpg_vcn_name']=lpg_name_tf_name
            tempStr['destination_type']="CIDR_BLOCK"
            tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_name_tf_name+".id"
            ruleStr = routerule.render(tempStr)

            vcns.vcn_lpg_rules[right_vcn] = vcns.vcn_lpg_rules[right_vcn] + ruleStr

def createDRGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, region):
    if (vcns.vcn_drgs[hub_vcn_name] == 'y'):
        # rt_tmp = hub_vcn_name+"_"+hub_vcn_name + "_drg_rt"
        # drg_name = hub_vcn_name + "_drg"
        drg_name = region + "_drg"
    elif (vcns.vcn_drgs[hub_vcn_name] != 'n'):
        # rt_tmp=hub_vcn_name+"_"+vcns.vcn_drgs[hub_vcn_name]+"_rt"
        drg_name = vcns.vcn_drgs[hub_vcn_name]
    elif (vcns.vcn_drgs[hub_vcn_name] == 'n'):
        print("drg_required column for VCN " + hub_vcn_name + " marked as Hub should not be set to n!!\n")
        return

    drg_rt_name = ""
    if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
        with open(outdir + "/" + region + "/obj_names.safe") as f:
            for line in f:
                if ("drginfo::::" + hub_vcn_name + "::::" + drg_name in line):
                    drg_rt_name = line.split("::::")[3].strip()

    if (drg_rt_name == ""):

        rt_display = "Route Table associated with DRG-""" + drg_name
        rt_var = hub_vcn_name + "_" + rt_display
    else:
        rt_var = hub_vcn_name + "_" + drg_rt_name
        rt_display = drg_rt_name

    rt_tf_name = commonTools.check_tf_variable(rt_var)

    outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")

    drgRuleStr = ""
    for right_vcn in right_vcns:
        if (right_vcn == ""):
            continue
        if right_vcn in vcns.spoke_vcn_names:
            right_vcn_tf_name = commonTools.check_tf_variable(right_vcn)
            lpg_name = vcns.vcn_lpg_names2[hub_vcn_name][0]
            lpg_name = hub_vcn_name + "_" + lpg_name
            lpg_tf_name = commonTools.check_tf_variable(lpg_name)
            hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)
            vcns.vcn_lpg_names2[hub_vcn_name].pop(0)

            tempStr['rt_tf_name'] = rt_tf_name
            tempStr['destination']= "oci_core_vcn."+right_vcn_tf_name+".cidr_block"
            tempStr['lpg_vcn_name']=lpg_tf_name
            tempStr['destination_type']="CIDR_BLOCK"
            tempStr['network_entity_id']="oci_core_local_peering_gateway."+lpg_tf_name+".id"
            temprule = routerule.render(tempStr)

            if (os.path.exists(outfile)):
                filedata = open(outfile, "r").read()
                if temprule not in filedata:
                    srcStr = "##Add More rules for subnet " + rt_tf_name + "##"
                    tempstr = temprule + srcStr
                    filedata = filedata.replace(srcStr, tempstr)
                    oname = open(outfile, "w")
                    oname.write(filedata)
                    oname.close()

            else:
                oname = open(outfile, "w")

                tempStr['rt_tf_name'] = rt_tf_name
                tempStr['compartment_tf_name'] = compartment_var_name
                tempStr['rt_display'] = rt_display
                tempStr['vcn_tf_name'] =hub_vcn_tf_name
                srcStr = "##Add More rules for subnet " + rt_tf_name + "##"
                drgStr = template.render(tempStr)
                temprule = temprule + srcStr
                drgStr = drgStr.replace(srcStr,temprule)
                oname.write(drgStr)
                oname.close()
                print(outfile + " containing TF for DRG Route Table has been created for region " + region)

    if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
        routetablefiles[region].remove(rt_tf_name + "_routetable.tf")


def createLPGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, region):
    # Retain exported route tables associated with exported LPGs
    if (os.path.exists(outdir + "/" + region + "/obj_names.safe")):
        with open(outdir + "/" + region + "/obj_names.safe") as f:
            for line in f:
                if ("lpginfo::::" + hub_vcn_name in line):
                    lpg_rt_name = line.split("::::")[3].strip()
                    rt_var = hub_vcn_name + "_" + lpg_rt_name
                    rt_tf_name = commonTools.check_tf_variable(rt_var)
                    if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                        routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

    # Create Rt table String for new spoke VCNs
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")

    for right_vcn in right_vcns:
        if (right_vcn == ""):
            continue
        temprule=''
        if (right_vcn in vcns.spoke_vcn_names):
            lpg_name = vcns.vcn_lpg_names3[hub_vcn_name][0]
            vcns.vcn_lpg_names3[hub_vcn_name].pop(0)
            # rt_var = hub_vcn_name + "_" + lpg_name + "_rt"
            rt_display = "Route Table associated with LPG-""" + lpg_name
            rt_var = hub_vcn_name + "_" + rt_display
            rt_tf_name = commonTools.check_tf_variable(rt_var)
            hub_vcn_tf_name = commonTools.check_tf_variable(hub_vcn_name)

            outfile = outdir + "/" + region + "/" + rt_tf_name + "_routetable.tf"
            oname = open(outfile, "w")

            tempStr['rt_display']= rt_display
            tempStr['rt_var'] = rt_var
            tempStr['rt_tf_name'] = rt_tf_name
            tempStr['vcn_tf_name'] = hub_vcn_tf_name

            lpgStr = template.render(tempStr)
            srcStr = "##Add More rules for subnet "+ rt_tf_name +"##"
            drg_name = ""
            if (vcns.vcn_drgs[hub_vcn_name] == 'y'):
                # drg_name = hub_vcn_name + "_drg"
                drg_name = region + "_drg"
            elif (vcns.vcn_drgs[hub_vcn_name] != 'n'):
                drg_name = vcns.vcn_drgs[hub_vcn_name]

            if (drg_name != ""):
                drg_tf_name = commonTools.check_tf_variable(drg_name)
                for drg_destination in vcnInfo.onprem_destinations:
                    if (drg_destination != ''):
                        tempStr['vcn_tf_name'] = ''
                        tempStr['destination'] = "\"" + drg_destination + "\""
                        tempStr['destination_type'] = "CIDR_BLOCK"
                        tempStr['network_entity_id'] = "oci_core_drg." + drg_tf_name + ".id"
                        temprule = temprule + routerule.render(tempStr)

            temprule = srcStr + temprule
            lpgStr = lpgStr.replace(srcStr,temprule)
            oname.write(lpgStr)
            oname.close()
            print(outfile + " containing TF for LPG Route Table has been created for region " + region)
            if (rt_tf_name + "_routetable.tf" in routetablefiles[region]):
                routetablefiles[region].remove(rt_tf_name + "_routetable.tf")

def prepareSGWRuleStr(sgw_name,destination,configure_sgw,tempStr,data):
    sgw_tf_name = vcn_name + "_" + sgw_name
    sgw_tf_name = commonTools.check_tf_variable(sgw_tf_name)
    if (configure_sgw=="all_services"):
        destination = "contains(split(\"-\",data.oci_core_services.oci_services.services.0.cidr_block),\"all\") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block"
    elif (configure_sgw=="object_storage"):
        destination = "contains(split(\"-\",data.oci_core_services.oci_services.services.0.cidr_block),\"objectstorage\") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block"
    tempStr['destination'] = destination
    tempStr['sgw_tf_name'] = sgw_tf_name
    tempStr['configure_sgw'] = configure_sgw
    tempStr['destination_type'] = "SERVICE_CIDR_BLOCK"
    tempStr['network_entity_id'] = "oci_core_service_gateway."+sgw_tf_name+".id"
    rem_keys=['vcn_tf_name','drg_tf_name','ngw_tf_name','igw_tf_name','lpg_tf_name']
    [tempStr.pop(key) for key in rem_keys if key in tempStr]
    data = data + routerule.render(tempStr)
    return data

def prepareNGWRuleStr(ngw_name,tempStr):
    ngw_tf_name = vcn_name + "_" + ngw_name
    ngw_tf_name = commonTools.check_tf_variable(ngw_tf_name)
    data = ""
    for ngw_destination in vcnInfo.ngw_destinations:
        if (ngw_destination != ''):
            tempStr['destination'] = "\""+ngw_destination+"\""
            tempStr['ngw_tf_name'] = ngw_tf_name
            tempStr['destination_type'] = "CIDR_BLOCK"
            tempStr['network_entity_id'] = "oci_core_nat_gateway." + ngw_tf_name + ".id"
            rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'igw_tf_name', 'lpg_tf_name']
            [tempStr.pop(key) for key in rem_keys if key in tempStr]
            data = data + routerule.render(tempStr)
    return data

def prepareIGWRuleStr(igw_name,tempStr):
    igw_tf_name = vcn_name + "_" + igw_name
    igw_tf_name = commonTools.check_tf_variable(igw_tf_name)
    data = ""
    for igw_destination in vcnInfo.igw_destinations:
        if (igw_destination != ''):
            tempStr['igw_tf_name'] = igw_tf_name
            tempStr['destination'] = "\""+igw_destination+"\""
            tempStr['destination_type'] = "CIDR_BLOCK"
            tempStr['network_entity_id'] = "oci_core_internet_gateway." + igw_tf_name + ".id"
            rem_keys = ['vcn_tf_name', 'drg_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
            [tempStr.pop(key) for key in rem_keys if key in tempStr]
            data = data + routerule.render(tempStr)
    return data

def prepareOnpremRuleStr(drg_name,tempStr):
    data = ""
    if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'hub':
        drg_tf_name = commonTools.check_tf_variable(drg_name)
        for drg_destination in vcnInfo.onprem_destinations:
            if (drg_destination != ''):
                tempStr['drg_tf_name'] = drg_tf_name
                tempStr['destination'] = "\""+drg_destination+"\""
                tempStr['destination_type'] = "CIDR_BLOCK"
                tempStr['network_entity_id'] = "oci_core_drg."+ drg_tf_name +".id"
                rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'lpg_tf_name']
                [tempStr.pop(key) for key in rem_keys if key in tempStr]
                data = data + routerule.render(tempStr)

    if vcns.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'spoke':
        """for left_vcn, value in peering_dict.items():
            right_vcns = value.split(",")
            for right_vcn in right_vcns:
                if (right_vcn == vcn_name):
                    hub_vcn_name = left_vcn
                    break

        lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"""""
        lpg_name = vcns.vcn_lpg_names[vcn_name][0]
        lpg_name = vcn_name + "_" + lpg_name
        lpg_tf_name = commonTools.check_tf_variable(lpg_name)
        for drg_destination in vcnInfo.onprem_destinations:
            if (drg_destination != ''):
                tempStr['lpg_tf_name'] = lpg_tf_name
                tempStr['destination'] = "\""+drg_destination+"\""
                tempStr['destination_type'] = "CIDR_BLOCK"
                tempStr['network_entity_id'] = "oci_core_local_peering_gateway."+ lpg_tf_name +".id"
                rem_keys = ['vcn_tf_name', 'igw_tf_name', 'configure_sgw', 'ngw_tf_name', 'drg_tf_name']
                [tempStr.pop(key) for key in rem_keys if key in tempStr]
                data = data + routerule.render(tempStr)
    return data

def prepareVCNPeerRuleStr():
    data = ""
    data = data + vcns.vcn_lpg_rules[vcn_name]
    return data

def processSubnet(tempStr):

    rt_name = tempStr['route_table_name']
    AD = tempStr['availability_domain']
    subnet =  tempStr['cidr_block']
    configure_sgw = tempStr['configure_sgw_route'].strip()
    configure_ngw = tempStr['configure_ngw_route'].strip()
    configure_igw = tempStr['configure_igw_route'].strip()
    configure_onprem = tempStr['configure_onprem_route'].strip()
    configure_vcnpeering = tempStr['configure_vcnpeering_route'].strip()

    # Route Table name specifiied as 'n' - dont create any routetable
    if (rt_name == "n"):
        return

    if (AD.strip().lower() != 'regional'):
        AD = AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    tempStr['ad_name'] = ad_name

    # check if subnet codr needs to be attached
    if (vcnInfo.subnet_name_attach_cidr == 'y'):
        if (str(ad_name) != ''):
            name1 = rt_name + "-ad" + str(ad_name)
        else:
            name1 = rt_name
        display_name = name1 + "-" + subnet
    else:
        display_name = rt_name

    tempStr['display_name'] = display_name

    vcn_tf_name=commonTools.check_tf_variable(tempStr['vcn_name'])
    subnet_tf_name = tempStr['vcn_name']+"_"+display_name

    print(subnet_tf_name)

    subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)

    tempStr['vcn_tf_name'] = vcn_tf_name
    tempStr['subnet_tf_name'] = subnet_tf_name

    #Create Route Table File Name
    outfile = outdir + "/" + region + "/" + subnet_tf_name + "_routetable.tf"
    if (subnet_tf_name + "_routetable.tf" in routetablefiles[region]):
        routetablefiles[region].remove(subnet_tf_name + "_routetable.tf")

    # Get VCN component names
    vcn_drg = vcns.vcn_drgs[vcn_name]
    drg_name = ""
    if (vcn_drg == "y"):
        # drg_name = vcn_name + "_drg"
        drg_name = region + "_drg"
    elif (vcn_drg != "n"):
        drg_name = vcn_drg
    tempStr['drg_name'] = drg_name

    vcn_igw = vcns.vcn_igws[vcn_name]
    igw_name = ""
    if (vcn_igw == "y"):
        igw_name = vcn_name + "_igw"
    elif (vcn_igw != "n"):
        igw_name = vcn_igw
    tempStr['igw_name'] = igw_name

    vcn_ngw = vcns.vcn_ngws[vcn_name]
    ngw_name = ""
    if (vcn_ngw == "y"):
        ngw_name = vcn_name + "_ngw"
    elif (vcn_ngw != "n"):
        ngw_name = vcn_ngw
    tempStr['ngw_name'] = ngw_name

    vcn_sgw = vcns.vcn_sgws[vcn_name]
    sgw_name = ""
    if (vcn_sgw == "y"):
        sgw_name = vcn_name + "_sgw"
    elif (vcn_sgw != "n"):
        sgw_name = vcn_sgw
    tempStr['sgw_name'] = sgw_name

    # Prepare rule str
    data=''
    data_sgw = prepareSGWRuleStr(sgw_name,destination,configure_sgw,tempStr,data)
    data_ngw = prepareNGWRuleStr(ngw_name,tempStr)
    data_igw = prepareIGWRuleStr(igw_name,tempStr)
    data_onprem = prepareOnpremRuleStr(drg_name,tempStr)
    data_vcnpeer = prepareVCNPeerRuleStr()

    dataStr = """#SubnetRules Start \n"""
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
    if (os.path.exists(outfile)):  # and modify_network == 'true'):
        newlines = []
        with open(outfile, 'r') as file:
            copy = True
            for line in file:
                if line.strip() == "#SubnetRules Start":
                    copy = False
                    newlines.append(dataStr)
                    continue
                elif (line.strip() == "#SubnetRules End"):
                    copy = True
                    continue
                elif copy:
                    newlines.append(line)
            file.close()
        with open(outfile, 'w') as file:
            file.writelines(newlines)
            file.close()
        return

    # New routetable
    oname = open(outfile, "w")
    rt_tf_name = subnet_tf_name
    tempStr['rt_tf_name'] = rt_tf_name
    tempStr['vcn_tf_name'] = vcn_tf_name
    tempStr['rt_display'] = display_name
    tempStr['compartment_tf_name'] = compartment_var_name
    srcStr = "##Add More rules for subnet " + rt_tf_name + "##"
    dataStr = dataStr + "\n" +"    "+ srcStr
    data_res = template.render(tempStr)
    tempStr = data_res.replace(srcStr, dataStr)

    oname.write(tempStr)
    oname.close()
    print(outfile + " containing TF for routerules has been created for region " + region)


# If input is CD3 excel file
if ('.xls' in filename):
    vcnInfo = parseVCNInfo(filename)
    vcns = parseVCNs(filename)

    # Purge existing routetable files
    if (modify_network == 'false'):
        for reg in ct.all_regions:
            routetablefiles.setdefault(reg, [])
            purge(outdir + "/" + reg, "_routetable.tf")

    # Get existing list of route table files
    if (modify_network == 'true'):
        for reg in ct.all_regions:
            routetablefiles.setdefault(reg, [])
            lisoffiles = os.listdir(outdir + "/" + reg)
            for file in lisoffiles:
                if "_routetable.tf" in file:
                    routetablefiles[reg].append(file)

    if (vcnInfo.onprem_destinations[0] == ""):
        print("\nonprem_destinations field is empty in VCN Info Sheet.. It will create empty route tables!!\n")

    # Create LPG Rules
    createLPGRouteRules(vcns.peering_dict)


    # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
    for hub_vcn_name in vcns.hub_vcn_names:
        compartment_var_name = vcns.vcn_compartment[hub_vcn_name]

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        # String for Route Table Assocaited with DRG
        r = vcns.vcn_region[hub_vcn_name].strip().lower()
        createDRGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r)

    # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
    for hub_vcn_name in vcns.hub_vcn_names:
        compartment_var_name = vcns.vcn_compartment[hub_vcn_name]
        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        r = vcns.vcn_region[hub_vcn_name].strip().lower()
        # String for Route Table Associated with each LPG in hub VCN peered with Spoke VCN
        createLPGRtTableString(compartment_var_name, hub_vcn_name, vcns.peering_dict, r)


    # Start processing for each subnet
    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # temporary dictionary1, dictionary2
    tempStr = {}
    tempdict = {}
    tempdict2 = {}
    rt_name=''
    compartment_var_name=''
    destination = ''

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for i in df.index:
        # Get subnet data
        region = df.loc[i,'Region']
        if (region in commonTools.endNames):
            break

        compartment_var_name = str(df.loc[i, 'Compartment Name'])
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        vcn_name = str(df['VCN Name'][i]).strip()
        if (vcn_name.strip() not in vcns.vcn_names):
            print("\nERROR!!! " + vcn_name + " specified in Subnets tab has not been declared in VCNs tab..Exiting!")
            exit(1)

        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'VCN Name']).lower() == 'nan' or
                str(df.loc[i, 'Subnet Name']).lower() == 'nan' or str(df.loc[i, 'CIDR Block']).lower() == 'nan' or str(
                    df.loc[i, 'Availability Domain\n(AD1|AD2|AD3|Regional)']).lower() == 'nan' or
                str(df.loc[i, 'Type(private|public)']).lower() == 'nan' or str(
                    df.loc[i, 'Configure SGW Route\n(n|object_storage|all_services)']).lower() == 'nan' or str(df.loc[i, 'Configure NGW Route\n(y|n)']).lower() == 'nan' or
                str(df.loc[i, 'Configure IGW Route (y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure OnPrem Route (y|n)']).lower() == 'nan' or str(df.loc[i, 'Configure VCNPeering\nRoute (y|n)']).lower() == 'nan'):
            print("\nERROR!!! Column Values (except DHCP Option Name, Route Table Name, Seclist Name, Common Seclist Name or DNS Label) or Rows cannot be left empty in Subnets sheet in CD3..Exiting!")
            exit(1)

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if columnvalue == '1.0' or  columnvalue == '0.0':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if "::" in columnvalue:
                if columnname != 'Compartment Name':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == 'Availability Domain\n(AD1|AD2|AD3|Regional)':
                columnname = 'availability_domain'
                tempdict = {'availability_domain' : columnvalue }

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue
                compartment_var_name = compartment_var_name.strip()
                # Added to check if compartment name is compatible with TF variable name syntax
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name' : compartment_var_name }

            if columnname == 'Configure SGW Route\n(n|object_storage|all_services)':
                columnname = 'configure_sgw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = { 'configure_sgw_route' : columnvalue }

            if columnname == 'Configure NGW Route\n(y|n)':
                columnname = 'configure_ngw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_ngw_route' : columnvalue }

            if columnname == 'Configure IGW Route (y|n)':
                columnname = 'configure_igw_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_igw_route' : columnvalue }

            if columnname == 'Configure OnPrem Route (y|n)':
                columnname = 'configure_onprem_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_onprem_route' : columnvalue }

            if columnname == 'Configure VCNPeering\nRoute (y|n)':
                columnname = 'configure_vcnpeering_route'
                columnvalue = columnvalue.lower().strip()
                tempdict = {'configure_vcnpeering_route' : columnvalue }

            if columnname == 'Route Table Name':
                if str(columnvalue).lower().strip() != 'nan' and str(columnvalue).lower().strip() != '':
                    rt_name = columnvalue.strip()
                    tempdict = {'route_table_name': rt_name}
                else:
                    rt_name = str(df.loc[i,'Subnet Name']).strip()
                    tempdict = {'route_table_name': rt_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = columnvalue
            tempStr.update(tempdict)

        processSubnet(tempStr)

    # remove any extra route table files (not part of latest cd3)
    RTs_in_objnames = []
    for reg in ct.all_regions:
        # Get any route tables from objnames.safe
        if (os.path.exists(outdir + "/" + reg + "/obj_names.safe")):
            with open(outdir + "/" + reg + "/obj_names.safe") as f:
                for line in f:
                    if (line != "\n"):
                        names = line.split("::::")
                        file_name = names[1] + "_" + commonTools.check_tf_variable(names[3].strip()) + "_routetable.tf"
                        RTs_in_objnames.append(file_name)

        if (len(routetablefiles[reg]) != 0):
            print("\nATTENION!!! Below RouteTables are not attached to any subnet or DRG and LPG; If you want to delete any of them, remove the TF file!!!")
        for remaining_rt_file in routetablefiles[reg]:
            if (remaining_rt_file in RTs_in_objnames):
                continue
            print(outdir + "/" + reg + "/" + remaining_rt_file)
            # print("Removing "+outdir+"/"+reg+"/"+remaining_rt_file)
            # os.remove(outdir+"/"+reg+"/"+remaining_rt_file)
            # routetablefiles[reg].remove(remaining_rt_file)


# If CD3 excel file is not given as input
elif ('.properties' in filename):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
    drg_ocid = config.get('Default', 'drg_ocid')
    onprem_destinations = config.get('Default', 'drg_subnet')
    # onprem_destinations = onprem_destinations.split(",")
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
        vcn_compartment[vcn_name] = compartment_var_name
        region = vcn_data[0].strip().lower()
        if region not in all_regions:
            print("Invalid Region")
            exit(1)
        vcn_region[vcn_name] = region

        if (vcn_data[2].strip().lower() != 'n'):
            vcn_drgs[vcn_name] = vcn_data[2].strip().lower()

        if (hub_spoke_none == 'hub'):
            hub_vcn_names.append(vcn_name)
        if (hub_spoke_none == 'spoke'):
            spoke_vcn_names.append(vcn_name)

    # Creating route rules for LPGs as per Section VCN_PEERING
    peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_cidr = peering_dict['ocs_vcn_cidr']
    peering_dict.pop('ocs_vcn_lpg_ocid')
    peering_dict.pop('ocs_vcn_cidr')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('add_ping_sec_rules_vcnpeering')

    createLPGRouteRules(peering_dict)

    # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
    # if (subnet_add == 'false'):
    for hub_vcn_name in hub_vcn_names:
        compartment_var_name = vcn_compartment[hub_vcn_name]

        # String for Route Table Assocaited with DRG
        r = vcn_region[hub_vcn_name].strip().lower()
        createDRGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, r)

        # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
    for hub_vcn_name in hub_vcn_names:
        compartment_var_name = vcn_compartment[hub_vcn_name]
        r = vcn_region[hub_vcn_name].strip().lower()

        # String for Route Tavle Associated with each LPG in hub VCN peered with Spoke VCN
        createLPGRtTableString(compartment_var_name, hub_vcn_name, peering_dict, r)

    # Start processing each VCN
    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')

        region = vcn_data[0].strip().lower()
        vcn_cidr = vcn_data[1].strip().lower()
        vcn_drg = vcn_data[2].strip().lower()
        if (vcn_drg == "y"):
            # drg_name = vcn_name + "_drg"
            drg_name = region + "_drg"
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
        if os.path.isfile(vcn_subnet_file) == False:
            print("input subnet file " + vcn_subnet_file + " for VCN " + vcn_name + " does not exist. Skipping Route TF creation for this VCN.")
            continue
        fname = open(vcn_subnet_file, "r")

        ruleStr = ""
        # Add DRG rules (this will add rules to hub vcn since for hub vcn drg_required is set to y
        if (vcn_drg == "y" and onprem_destinations != ''):
            if (drg_ocid == ''):
                for drg_destination in onprem_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
            if (drg_ocid != ''):
                for drg_destination in onprem_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id =  \"""" + drg_ocid + """"
                destination_type = "CIDR_BLOCK"
                }
                """

        # Add DRG rules to each Spoke VCN
        if (hub_spoke_none == 'spoke' and onprem_destinations != ''):
            for left_vcn, value in peering_dict.items():
                right_vcns = value.split(",")
                for right_vcn in right_vcns:
                    if (right_vcn == vcn_name):
                        hub_vcn_name = left_vcn
                        break

            lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"
            for drg_destination in onprem_destinations:
                if (drg_destination != ''):
                    ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """

        # Add LPG rules
        if (vcn_lpg_rules[vcn_name] != ''):
            ruleStr = ruleStr + vcn_lpg_rules[vcn_name]

        # Read input subnet file
        for line in fname:
            if not line.startswith('#') and line != '\n':
                # print "processing : " + line
                subnet = ""
                name = ""

                [compartment_var_name, name, sub, AD, pubpvt, dhcp, rt_name, seclist_name, common_seclist_name,
                 configure_sgw, configure_ngw, configure_igw, dns_label] = line.split(',')
                linearr = line.split(",")
                compartment_var_name = linearr[0].strip()
                name = linearr[1].strip()
                subnet = linearr[2].strip()

                processSubnet(region, vcn_name, name, rt_name.strip(), ruleStr, AD, configure_sgw, configure_ngw,
                              configure_igw, vcn_sgw, vcn_ngw, vcn_igw)

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .properties")
    exit()

if (fname != None):
    fname.close()
