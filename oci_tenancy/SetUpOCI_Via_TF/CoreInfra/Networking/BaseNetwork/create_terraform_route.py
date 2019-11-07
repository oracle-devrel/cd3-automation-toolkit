#!/usr/bin/python3
# Author: Suruchi Singla
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import os
import argparse
import configparser
import pandas as pd
import re
import datetime
import shutil

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
parser.add_argument("prefix", help="customer name/prefix for all file names")
parser.add_argument("--subnet_add", help="Add new subnet: true or false", required=False)

if len(sys.argv)<3:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
filename=args.inputfile
outdir = args.outdir
prefix=args.prefix
if args.subnet_add is not None:
    subnet_add = str(args.subnet_add)
else:
    subnet_add = "false"

outfile={}
oname={}


ADS = ["AD1", "AD2", "AD3"]
fname = None
#Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING
hub_vcn_names=[]
spoke_vcn_names=[]
vcn_lpg_rules = {}
vcn_compartment = {}
vcn_region = {}
vcn_drgs= {}
peering_dict = dict()
ruleStr=""

def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            print("Purge ....." +  os.path.join(dir, f))
            os.remove(os.path.join(dir, f))

def createLPGRouteRules(peering_dict):
    global vcn_lpg_rules

    for left_vcn, value in peering_dict.items():

        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            if (right_vcn == 'ocs_vcn'):
                # Build rule for VCN on left for OCS VCN on right
                lpg_name = left_vcn + "_ocs_lpg"
                ruleStr = """
            route_rules { 
                destination = \"""" + ocs_vcn_cidr + """"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                            """
                vcn_lpg_rules[left_vcn] = vcn_lpg_rules[left_vcn] + ruleStr

            else:
                # Build rule for VCN on left
                lpg_name = left_vcn + "_" + right_vcn + "_lpg"
                ruleStr = """
            route_rules { 
                destination = "${oci_core_vcn.""" + right_vcn + """.cidr_block}"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
            """
                vcn_lpg_rules[left_vcn] = vcn_lpg_rules[left_vcn] + ruleStr

                # Build rule for VCNs on right
                lpg_name = right_vcn + "_" + left_vcn + "_lpg"
                ruleStr = """
            route_rules { 
                destination = "${oci_core_vcn.""" + left_vcn + """.cidr_block}"
                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                destination_type = "CIDR_BLOCK"
            }
            """
                vcn_lpg_rules[right_vcn] = vcn_lpg_rules[right_vcn] + ruleStr

def createDRGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,region):
    if(vcn_drgs[hub_vcn_name]=='y'):
        rt_var = hub_vcn_name + "_drg_rt"
        drg_name = hub_vcn_name + "_drg"
    elif(vcn_drgs[hub_vcn_name]!='n'):
        rt_var=vcn_drgs[hub_vcn_name]+"_rt"
        drg_name=vcn_drgs[hub_vcn_name]

    outfile = outdir + "/" + region + "/" + rt_var + "_routetable.tf"
    oname = open(outfile, "w")
    drgStr = """ 
        resource "oci_core_route_table" \"""" + rt_var + """"{
                compartment_id = "${var.""" + compartment_var_name + """}"
                vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
                display_name = "Route Table associated with DRG """ + drg_name + """"
                
                ##Add More rules for subnet """ + rt_var + """##
                """
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")
    for right_vcn in right_vcns:
        if right_vcn in spoke_vcn_names:
            lpg_name = hub_vcn_name + "_" + right_vcn + "_lpg"
            drgStr = drgStr + """
                route_rules { 
                    destination = "${oci_core_vcn.""" + right_vcn + """.cidr_block}"
                    network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
                """
    drgStr = drgStr + """
        }"""
    oname.write(drgStr)
    oname.close()

def createLPGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,region):
    right_vcns = peering_dict[hub_vcn_name]
    right_vcns = right_vcns.split(",")

    for right_vcn in right_vcns:
        if(right_vcn in spoke_vcn_names):
            lpg_name = hub_vcn_name + "_" + right_vcn + "_lpg"
            rt_var = lpg_name + "_rt"
            outfile = outdir + "/" + region + "/" + rt_var + "_routetable.tf"
            oname = open(outfile, "w")
            lpgStr = """ 
            resource "oci_core_route_table" \"""" + rt_var + """"{
                    compartment_id = "${var.""" + compartment_var_name + """}"
                    vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
                    display_name = "Route Table associated with LPG """ + lpg_name + """"
                    
                    ##Add More rules for subnet """ + rt_var + """##
                """
            if (drg_ocid == ''):
                if (vcn_drgs[hub_vcn_name] == 'y'):
                    drg_name = hub_vcn_name + "_drg"
                elif (vcn_drgs[hub_vcn_name] != 'n'):
                    drg_name = vcn_drgs[hub_vcn_name]

                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        lpgStr = lpgStr + """
                    route_rules { 
                        destination = \"""" + drg_destination.strip() + """\"
                        network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                """
            if (drg_ocid != ''):
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        lpgStr = lpgStr + """
                    route_rules { 
                            destination = \"""" + drg_destination.strip() + """\"
                            network_entity_id =  \"""" + drg_ocid + """"
                            destination_type = "CIDR_BLOCK"
                            }
                """

            lpgStr = lpgStr + """
        }"""
            oname.write(lpgStr)
            oname.close()

def processSubnet(region,vcn_name,name,rt_name,ruleStr,AD,configure_sgw,configure_ngw,configure_igw,vcn_sgw,vcn_ngw,vcn_igw):
    # process each subnet row for ngw, igw, sgw
    if (AD.strip().lower() != 'regional'):
        AD=AD.strip().upper()
        ad = ADS.index(AD)
        ad_name_int = ad + 1
        ad_name = str(ad_name_int)
    else:
        ad_name = ""

    #route table not provided; use subnet name as route table name
    if(rt_name==''):
        subnet_res_name = name
        if (str(ad_name) != ''):
            name1 = subnet_res_name + "-ad" + str(ad_name)
        else:
            name1 = subnet_res_name

        #check if subnet codr needs to be attached
        if (subnet_name_attach_cidr == 'y'):
            display_name = name1 + "-" + subnet
        else:
            display_name = subnet_res_name

    # route table name provided
    else:
        subnet_res_name=rt_name
        # no need to attach subnet cidr to display name
        display_name = subnet_res_name

    outfile = outdir + "/" + region + "/" + vcn_name+"_"+subnet_res_name + "_routetable.tf"
    # Same routetable used for subnets
    if (os.path.exists(outfile)):
        data=""
        if configure_sgw.strip() == 'y' and vcn_sgw != 'n':
            data = """
                        route_rules { 
                            destination = "${data.oci_core_services.oci_services.services.0.cidr_block}"
                            network_entity_id = "${oci_core_service_gateway.""" + sgw_name + """.id}"
                            destination_type = "SERVICE_CIDR_BLOCK"
                            }
                            """
        if configure_ngw.strip() == 'y' and vcn_ngw != 'n':
            for ngw_destination in ngw_destinations:
                if (ngw_destination != ''):
                    data = data + """ 

                        route_rules { 
                            destination = \"""" + ngw_destination + """\"
                            network_entity_id = "${oci_core_nat_gateway.""" + ngw_name + """.id}"
                            destination_type = "CIDR_BLOCK"
                            }
                            """
        if configure_igw.strip() == 'y' and vcn_igw != 'n':
            for igw_destination in igw_destinations:
                if (igw_destination != ''):
                    data = data + """

                        route_rules { 
                            destination = \"""" + igw_destination + """\"
                            network_entity_id = "${oci_core_internet_gateway.""" + igw_name + """.id}"
                            destination_type = "CIDR_BLOCK"
                            }
                            """
        end = """
                            ##Add More rules for subnet """ + vcn_name+"_"+subnet_res_name + """##
                    """

        with open(outfile, 'r+') as file:
            filedata = file.read()
        file.close()
        # Replace the target string
        textToSearch = """##Add More rules for subnet """ + vcn_name+"_"+subnet_res_name + """##"""
        filedata = filedata.replace(textToSearch, data+end)
        oname = open(outfile, "w")
        oname.write(filedata)
        oname.close()
        return

    #New routetable
    oname = open(outfile, "w")

    data_res = """ 
            resource "oci_core_route_table" \"""" +vcn_name+"_"+ subnet_res_name + """"{
                compartment_id = "${var.""" + compartment_var_name + """}"
                vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
                display_name = \"""" + display_name.strip() + """\" """
    data=""
    if configure_sgw.strip() == 'y' and vcn_sgw != 'n':
        data = """
                    route_rules { 
                        destination = "${data.oci_core_services.oci_services.services.0.cidr_block}"
                        network_entity_id = "${oci_core_service_gateway.""" + sgw_name + """.id}"
                        destination_type = "SERVICE_CIDR_BLOCK"
                        }
                        """
    if configure_ngw.strip() == 'y' and vcn_ngw != 'n':
        for ngw_destination in ngw_destinations:
            if (ngw_destination != ''):
                data = data + """ 

                    route_rules { 
                        destination = \"""" + ngw_destination + """\"
                        network_entity_id = "${oci_core_nat_gateway.""" + ngw_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
    if configure_igw.strip() == 'y' and vcn_igw != 'n':
        for igw_destination in igw_destinations:
            if (igw_destination != ''):
                data = data + """

                    route_rules { 
                        destination = \"""" + igw_destination + """\"
                        network_entity_id = "${oci_core_internet_gateway.""" + igw_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                        """
    end="""
                        ##Add More rules for subnet """ + vcn_name+"_"+subnet_res_name + """##
                }
                """
    tempStr=data_res+ruleStr+data+end
    oname.write(tempStr)
    oname.close()
    print(outfile + " containing TF for routerules has been created for region " + region)



endNames = {'<END>', '<end>'}

#If input is CD3 excel file
if('.xls' in filename):
        NaNstr = 'NaN'
        df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
        df_vcn.dropna(how='all')
        df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

        # Get Property Values
        properties = df_info['Property']
        values = df_info['Value']

        drg_destinations = str(values[0]).strip()
        if (drg_destinations.lower() == NaNstr.lower()):
            print("\ndrg_subnet should not be left empty.. It will create empty route tables")
            drg_destinations = ''
        drg_destinations=drg_destinations.split(",")

        drg_ocid = str(values[1]).strip()

        if (drg_ocid.lower() == NaNstr.lower()):
            drg_ocid = ''

        all_regions = str(values[7]).strip()
        all_regions = all_regions.split(",")
        all_regions = [x.strip().lower() for x in all_regions]

        # Purge existing routetable files
        if (subnet_add == 'false'):
            for reg in all_regions:
                purge(outdir + "/" + reg, "_routetable.tf")

        ngw_destinations = str(values[2]).strip()
        if (ngw_destinations.lower() == NaNstr.lower()):
            ngw_destinations = '0.0.0.0/0'
        ngw_destinations = ngw_destinations.split(",")

        igw_destinations = str(values[3]).strip()
        if (igw_destinations.lower() == NaNstr.lower()):
            igw_destinations = '0.0.0.0/0'
        igw_destinations=igw_destinations.split(",")

        subnet_name_attach_cidr = str(values[4]).strip()
        if (subnet_name_attach_cidr.lower() == NaNstr.lower()):
            subnet_name_attach_cidr = 'n'


        for j in df_info.index:
            if (j > 8):
                peering_dict[properties[j]] = values[j]

        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
                region = df_vcn['Region'][i]
                if (region in endNames):
                    break
                region = region.strip().lower()

                if region not in all_regions:
                    print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                    exit(1)
                vcn_name=df_vcn['vcn_name'][i]
                if(df_vcn['drg_required'][i]!='n'):
                    vcn_drgs[vcn_name]=df_vcn['drg_required'][i]

                compartment_var_name = df_vcn['compartment_name'][i]
                vcn_compartment[vcn_name]=compartment_var_name
                vcn_region[vcn_name]=region
                vcn_lpg_rules.setdefault(vcn_name, '')
                hub_spoke_none=df_vcn['hub_spoke_none'][i]
                if (hub_spoke_none == 'hub'):
                    hub_vcn_names.append(vcn_name)
                if (hub_spoke_none == 'spoke'):
                    spoke_vcn_names.append(vcn_name)


        # Create LPG Rules
        createLPGRouteRules(peering_dict)

        #if(subnet_add=='false'):
        # Create Route Table associated with DRG for Hub VCN and route rules for its each spoke VCN
        for hub_vcn_name in hub_vcn_names:
            compartment_var_name = vcn_compartment[hub_vcn_name]

            #String for Route Table Assocaited with DRG
            r = vcn_region[hub_vcn_name].strip().lower()
            createDRGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,r)


        # Create Route Table associated with LPGs in Hub VCN peered with spoke VCNs
        for hub_vcn_name in hub_vcn_names:
            compartment_var_name = vcn_compartment[hub_vcn_name]
            r = vcn_region[hub_vcn_name].strip().lower()
            #String for Route Tavle Associated with each LPG in hub VCN peered with Spoke VCN
            createLPGRtTableString(compartment_var_name,hub_vcn_name,peering_dict,r)


        # Start processing for each subnet
        NaNstr = 'NaN'
        df_vcn.set_index("vcn_name", inplace=True)
        df_vcn.head()
        df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
        df.dropna(how='all')
        for i in df.index:

            # Get subnet data
            compartment_var_name = df.iat[i, 0]
            if (compartment_var_name in endNames):
                break
            vcn_name = df['vcn_name'][i]

            name = df.iat[i, 2]
            subnet = df.iat[i, 3]
            AD = df.iat[i, 4]
            pubpvt = df.iat[i, 5]
            dhcp = df.iat[i, 6]
            rt_name=df.iat[i,7]

            configure_sgw = df.iat[i, 10]
            configure_ngw = df.iat[i, 11]
            configure_igw = df.iat[i, 12]

            # Check to see if any column is empty in Subnets Sheet
            if (str(compartment_var_name).lower() == NaNstr.lower() or str(vcn_name).lower() == NaNstr.lower() or
                    str(name).lower() == NaNstr.lower() or str(subnet).lower() == NaNstr.lower()
                    or str(AD).lower() == NaNstr.lower() or str(pubpvt).lower() == NaNstr.lower()
                    or str(configure_sgw).lower() == NaNstr.lower() or str(configure_ngw).lower() == NaNstr.lower()
                    or str(configure_igw).lower() == NaNstr.lower()):
                print("Column Values (except dhcp_option_name, route_table_name, seclist_name, common_seclist_name or dns_label) or Rows cannot be left empty in Subnets sheet in CD3..exiting...")
                exit(1)

            compartment_var_name=compartment_var_name.strip()
            configure_sgw=configure_sgw.strip()
            configure_ngw = configure_ngw.strip()
            configure_igw = configure_igw.strip()
            pubpvt=pubpvt.strip()
            subnet=subnet.strip()
            name=name.strip()
            if (str(rt_name).lower() != 'nan'):
                rt_name=rt_name.strip()
            else:
                rt_name=''

            vcn_data = df_vcn.loc[vcn_name]
            region = vcn_data['Region']
            region = region.strip().lower()

            vcn_drg = vcn_data['drg_required']
            if(vcn_drg=="y"):
                drg_name = vcn_name + "_drg"
            elif(vcn_drg!="n"):
                drg_name=vcn_drg

            vcn_igw = vcn_data['igw_required']
            if(vcn_igw=="y"):
                igw_name = vcn_name + "_igw"
            elif (vcn_igw != "n"):
                igw_name = vcn_igw

            vcn_ngw = vcn_data['ngw_required']
            if (vcn_ngw == "y"):
                ngw_name = vcn_name + "_ngw"
            elif (vcn_ngw != "n"):
                ngw_name = vcn_ngw

            vcn_sgw = vcn_data['sgw_required']
            if (vcn_sgw == "y"):
                sgw_name = vcn_name + "_sgw"
            elif (vcn_sgw != "n"):
                sgw_name = vcn_sgw


            hub_spoke_none = vcn_data['hub_spoke_none']

            ruleStr = ""
            # Add DRG rules (this will add rules to hub vcn since for hub vcn drg_required is set to y
            if (vcn_drg != "n" and drg_destinations != ''):
                if (drg_ocid == ''):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            ruleStr = ruleStr + """
                        route_rules { 
                            destination = \"""" + drg_destination.strip() + """\"
                            network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                            destination_type = "CIDR_BLOCK"
                            }
                            """
                if (drg_ocid != ''):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            ruleStr = ruleStr + """
                        route_rules { 
                            destination = \"""" + drg_destination.strip() + """\"
                            network_entity_id =  \"""" + drg_ocid + """"
                            destination_type = "CIDR_BLOCK"
                            }
                            """

            # Add DRG rules to each Spoke VCN
            if (hub_spoke_none == 'spoke' and drg_destinations != ''):
                for left_vcn, value in peering_dict.items():
                    right_vcns = value.split(",")
                    for right_vcn in right_vcns:
                        if(right_vcn==vcn_name):
                            hub_vcn_name=left_vcn
                            break

                lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"
                for drg_destination in drg_destinations:
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

            processSubnet(region, vcn_name, name,rt_name,ruleStr,AD,configure_sgw, configure_ngw, configure_igw, vcn_sgw, vcn_ngw, vcn_igw)



# If CD3 excel file is not given as input
elif('.properties' in filename):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.inputfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
    drg_ocid = config.get('Default', 'drg_ocid')
    drg_destinations = config.get('Default', 'drg_subnet')
    #drg_destinations = drg_destinations.split(",")
    if (drg_destinations == ''):
        print("\ndrg_subnet should not be left empty.. It will create empty route tables")
    else:
        drg_destinations = drg_destinations.split(",")

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
        if (vcn_drg =="y" and drg_destinations!=''):
            if(drg_ocid==''):
                for drg_destination in drg_destinations:
                    if(drg_destination!=''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
            if(drg_ocid!=''):
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination.strip() + """\"
                network_entity_id =  \"""" + drg_ocid + """"
                destination_type = "CIDR_BLOCK"
                }
                """

        #Add DRG rules to each Spoke VCN
        if (hub_spoke_none=='spoke' and drg_destinations!=''):
            for left_vcn, value in peering_dict.items():
                right_vcns = value.split(",")
                for right_vcn in right_vcns:
                    if (right_vcn == vcn_name):
                        hub_vcn_name = left_vcn
                        break

            lpg_name=vcn_name+"_"+hub_vcn_name+"_lpg"
            for drg_destination in drg_destinations:
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

routedata={}

