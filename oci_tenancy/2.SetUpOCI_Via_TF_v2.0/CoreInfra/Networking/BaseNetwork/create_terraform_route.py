#!/bin/python
# Author: Suruchi Singla
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import os
import argparse
import configparser
import pandas as pd

######
# Required Files
# Properties File: vcn-info.properties"
# Code will read input subnet file name for each vcn from properties file
# Subnets file will contain info about each subnet and which component(SGW, NGW, IGW) is required for which subnet
# Outfile
######

parser = argparse.ArgumentParser(description="Creates route tables containing default routes for each subnet based on inputs given in vcn-info.properties.")
parser.add_argument("inputfile", help="Full Path of properties file. eg vcn-info.properties or cd3 excel file")
parser.add_argument("outfile", help="Output Filename")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
outfile = args.outfile
oname = open(outfile,"w")
fname = None
filename=args.inputfile
tempStr = ""
ADS = ["AD1", "AD2", "AD3"]

#Get Hub VCN name and create route rules for LPGs as per Section VCN_PEERING
hub_vcn_name=''
vcn_lpg_rules = {}
vcn_compartment = {}
peering_dict = dict()
ruleStr=""

drgStr=""
lpgStr=""

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


#If input is CD3 excel file
if('.xlsx' in filename):
        NaNstr = 'NaN'
        df_vcn = pd.read_excel(filename, sheet_name='VCNs',skiprows=1)
        df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

        # Get Property Values
        properties = df_info['Property']
        values = df_info['Value']

        drg_destinations = str(values[0]).strip()
        if (drg_destinations.lower() == NaNstr.lower()):
            print("drg_subnet should not be left empty.. It will create empty route tables")
            drg_destinations = ''
        drg_destinations=drg_destinations.split(",")

        drg_ocid = str(values[1]).strip()

        if (drg_ocid.lower() == NaNstr.lower()):
            drg_ocid = ''

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
            if (j > 7):
                peering_dict[properties[j]] = values[j]


        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
                vcn_name=df_vcn['vcn_name'][i]
                compartment_var_name = df_vcn['compartment_name'][i]
                vcn_compartment[vcn_name]=compartment_var_name
                vcn_lpg_rules.setdefault(vcn_name, '')
                hub_spoke_none=df_vcn['hub_spoke_none'][i]
                if (hub_spoke_none == 'hub'):
                    hub_vcn_name = vcn_name

        # Create LPG Rules
        createLPGRouteRules(peering_dict)


        if (hub_vcn_name != ''):
            # Create Route Table associated with DRG for Hub VCN
            rt_var = hub_vcn_name + "_drg_rt"
            compartment_var_name = vcn_compartment[hub_vcn_name]
            drgStr = """ 
        resource "oci_core_route_table" \"""" + rt_var + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
            display_name = "Route Table associated with DRG"
            """


        # Create Route Table Associated with each LPG in Hub VCN peered with Spoke VCN
        # Get VCN names from vcn_name column in VCNs sheet of CD3 excel
        for i in df_vcn.index:
            vcn_name = df_vcn['vcn_name'][i]
            hub_spoke_none = df_vcn['hub_spoke_none'][i]
            if (hub_spoke_none == 'spoke'):
                lpg_name = hub_vcn_name + "_" + vcn_name + "_lpg"
                rt_var = lpg_name + "_rt"
                lpgStr = lpgStr + """ 
        resource "oci_core_route_table" \"""" + rt_var + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
            display_name = "Route Table associated with LPG """ + lpg_name + """"
        """
                if (drg_ocid == ''):
                    drg_name = hub_vcn_name + "_drg"
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            lpgStr = lpgStr + """
                route_rules { 
                    destination = \"""" + drg_destination + """\"
                    network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
        """
                if (drg_ocid != ''):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            lpgStr = lpgStr + """
                route_rules { 
                    destination = \"""" + drg_destination + """\"
                    network_entity_id =  \"""" + drg_ocid + """"
                    destination_type = "CIDR_BLOCK"
                    }
        """

                lpgStr = lpgStr + """
        }"""
                # Add Rules for each spoke VCN to Route Table associated with DRG of Hub VCN
                if (hub_spoke_none == 'spoke'):
                    lpg_name = hub_vcn_name + "_" + vcn_name + "_lpg"
                    drgStr = drgStr + """
                            route_rules { 
                                destination = "${oci_core_vcn.""" + vcn_name + """.cidr_block}"
                                network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                                destination_type = "CIDR_BLOCK"
                                }
                                """

        # Start processing for each subnet
        NaNstr = 'NaN'
        df_vcn.set_index("vcn_name", inplace=True)
        df_vcn.head()
        df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
        for i in df.index:
            # Get VCN data
            vcn_name = df['vcn_name'][i]

            # Get subnet data
            compartment_var_name = df.iat[i, 0]
            compartment_var_name=compartment_var_name.strip()
            name = df.iat[i, 2]
            name=name.strip()
            subnet = df.iat[i, 3]
            subent=subnet.strip()
            AD = df.iat[i, 4]
            AD=AD.strip()
            pubpvt = df.iat[i, 5]
            pubpvt=pubpvt.strip()
            dhcp = df.iat[i, 6]

            configure_sgw = df.iat[i, 7]
            configure_sgw=configure_sgw.strip()
            configure_ngw = df.iat[i, 8]
            configure_ngw = configure_ngw.strip()
            configure_igw = df.iat[i, 9]
            configure_igw = configure_igw.strip()

            # Check to see if any column is empty in Subnets Sheet
            if (str(compartment_var_name).lower() == NaNstr.lower() or str(vcn_name).lower() == NaNstr.lower() or
                    str(name).lower() == NaNstr.lower() or str(subnet).lower() == NaNstr.lower()
                    or str(AD).lower() == NaNstr.lower() or str(pubpvt).lower() == NaNstr.lower()
                    or str(configure_sgw).lower() == NaNstr.lower() or str(configure_ngw).lower() == NaNstr.lower()
                    or str(configure_igw).lower() == NaNstr.lower()):
                print("Column Values or Rows cannot be left empty in Subnets sheet in CD3..exiting...")
                exit(1)

            vcn_data = df_vcn.loc[vcn_name]
            vcn_drg = vcn_data['drg_required(y|n)']
            drg_name = vcn_name + "_drg"
            vcn_igw = vcn_data['igw_required(y|n)']
            igw_name = vcn_name + "_igw"
            vcn_ngw = vcn_data['ngw_required(y|n)']
            ngw_name = vcn_name + "_ngw"
            vcn_sgw = vcn_data['sgw_required(y|n)']
            sgw_name = vcn_name + "_sgw"
            hub_spoke_none = vcn_data['hub_spoke_none']


            ruleStr = ""
            # Add DRG rules (this will add rules to hub vcn since for hub vcn drg_required is set to y
            if (vcn_drg == "y" and drg_destinations != ''):
                if (drg_ocid == ''):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            ruleStr = ruleStr + """
                route_rules { 
                    destination = \"""" + drg_destination + """\"
                    network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
                    """
                if (drg_ocid != ''):
                    for drg_destination in drg_destinations:
                        if (drg_destination != ''):
                            ruleStr = ruleStr + """
                route_rules { 
                    destination = \"""" + drg_destination + """\"
                    network_entity_id =  \"""" + drg_ocid + """"
                    destination_type = "CIDR_BLOCK"
                    }
                    """

            # Add DRG rules to each Spoke VCN
            if (hub_spoke_none == 'spoke' and drg_destinations != ''):
                lpg_name = vcn_name + "_" + hub_vcn_name + "_lpg"
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
                route_rules { 
                    destination = \"""" + drg_destination + """\"
                    network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
                    """

            # Add LPG rules
            if (vcn_lpg_rules[vcn_name] != ''):
                ruleStr = ruleStr + vcn_lpg_rules[vcn_name]

            # process each subnet row for ngw, igw, sgw
            if (AD.strip() != 'Regional'and  AD.strip() != 'regional'):
                ad = ADS.index(AD)
                ad_name_int = ad + 1
                ad_name = str(ad_name_int)
            else:
                ad_name = ""

            subnet_res_name = name
            if (str(ad_name) != ''):
                name1 = name + "-ad" + str(ad_name)
            else:
                name1 = name
            if (subnet_name_attach_cidr == 'y'):
                display_name = name1 + "-" + subnet
            else:
                display_name = name

            # name=name1
            tempStr = tempStr + """ 
        resource "oci_core_route_table" \"""" + name + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
            display_name = \"""" + display_name.strip() + """\" """ + ruleStr

            if configure_sgw.strip() == 'y' and vcn_sgw == 'y':
                tempStr = tempStr + """

                route_rules { 
                    destination = "${data.oci_core_services.oci_services.services.0.cidr_block}"
                    network_entity_id = "${oci_core_service_gateway.""" + sgw_name + """.id}"
                    destination_type = "SERVICE_CIDR_BLOCK"
                    }
                    """
            if configure_ngw.strip() == 'y' and vcn_ngw == 'y':
                for ngw_destination in ngw_destinations:
                    if (ngw_destination != ''):
                        tempStr = tempStr + """ 

                route_rules { 
                    destination = \"""" + ngw_destination + """\"
                    network_entity_id = "${oci_core_nat_gateway.""" + ngw_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
                    """
            if configure_igw.strip() == 'y' and vcn_igw == 'y':
                for igw_destination in igw_destinations:
                    if (igw_destination != ''):
                        tempStr = tempStr + """

                route_rules { 
                    destination = \"""" + igw_destination + """\"
                    network_entity_id = "${oci_core_internet_gateway.""" + igw_name + """.id}"
                    destination_type = "CIDR_BLOCK"
                    }
                    """
            tempStr = tempStr + """
                    ##Add More rules for subnet """ + subnet_res_name + """##
            }
            """


# If CD3 excel file is not given as input
elif('.csv' in filename):
    config = configparser.RawConfigParser()
    config.optionxform = str
    config.read(args.propsfile)
    sections = config.sections()

    # Get Global Properties from Default Section
    subnet_name_attach_cidr = config.get('Default', 'subnet_name_attach_cidr')
    drg_ocid = config.get('Default', 'drg_ocid')
    drg_destinations = config.get('Default', 'drg_subnet')
    drg_destinations = drg_destinations.split(",")

    ngw_destinations = config.get('Default', 'ngw_destination')
    if (ngw_destinations == ''):
        ngw_destinations = '0.0.0.0/0'
    ngw_destinations = ngw_destinations.split(",")

    igw_destinations = config.get('Default', 'igw_destination')
    if (igw_destinations == ''):
        igw_destinations = '0.0.0.0/0'
    igw_destinations = igw_destinations.split(",")

    # Get VCN Info from VCN_INFO section
    vcns = config.options('VCN_INFO')
    for vcn_name in vcns:
        vcn_lpg_rules.setdefault(vcn_name, '')
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        hub_spoke_none = vcn_data[5].strip().lower()
        compartment_var_name = vcn_data[11].strip()
        vcn_compartment[vcn_name]=compartment_var_name

        if (hub_spoke_none == 'hub'):
            hub_vcn_name = vcn_name


    # Creating route rules for LPGs as per Section VCN_PEERING
    peering_dict = dict(config.items('VCN_PEERING'))
    ocs_vcn_cidr=peering_dict['ocs_vcn_cidr']
    peering_dict.pop('ocs_vcn_lpg_ocid')
    peering_dict.pop('ocs_vcn_cidr')
    peering_dict.pop('add_ping_sec_rules_onprem')
    peering_dict.pop('add_ping_sec_rules_vcnpeering')

    createLPGRouteRules(peering_dict)


    if(hub_vcn_name!=''):
        # Create Route Table associated with DRG for Hub VCN
        rt_var=hub_vcn_name+"_drg_rt"
        compartment_var_name = vcn_compartment[hub_vcn_name]
        drgStr = """ 
        resource "oci_core_route_table" \"""" + rt_var + """"{
            compartment_id = "${var.""" + compartment_var_name + """}"
            vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
            display_name = "Route Table associated with DRG"
            """

    # Create Route Table Associated with each LPG in Hub VCN peered with Spoke VCN
    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')
        hub_spoke_none = vcn_data[5].strip().lower()

        if(hub_spoke_none=='spoke'):
            lpg_name=hub_vcn_name+"_"+vcn_name+"_lpg"
            rt_var=lpg_name+"_rt"
            lpgStr = lpgStr+""" 
resource "oci_core_route_table" \"""" + rt_var + """"{
    compartment_id = "${var.""" + compartment_var_name + """}"
    vcn_id = "${oci_core_vcn.""" + hub_vcn_name + """.id}"
    display_name = "Route Table associated with LPG """+lpg_name +""""
"""
            if (drg_ocid == ''):
                drg_name=hub_vcn_name+"_drg"
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        lpgStr = lpgStr + """
        route_rules { 
            destination = \"""" + drg_destination + """\"
            network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
            destination_type = "CIDR_BLOCK"
            }
"""
            if (drg_ocid != ''):
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        lpgStr = lpgStr + """
        route_rules { 
            destination = \"""" + drg_destination + """\"
            network_entity_id =  \"""" + drg_ocid + """"
            destination_type = "CIDR_BLOCK"
            }
"""

            lpgStr=lpgStr+"""
}"""

            # Add Rules for each spoke VCN to Route Table associated with DRG of Hub VCN
            if (hub_spoke_none == 'spoke'):
                lpg_name = hub_vcn_name + "_" + vcn_name + "_lpg"
                drgStr = drgStr + """
                    route_rules { 
                        destination = "${oci_core_vcn.""" + vcn_name + """.cidr_block}"
                        network_entity_id = "${oci_core_local_peering_gateway.""" + lpg_name + """.id}"
                        destination_type = "CIDR_BLOCK"
                        }
                """

    for vcn_name in vcns:
        vcn_data = config.get('VCN_INFO', vcn_name)
        vcn_data = vcn_data.split(',')

        vcn_cidr = vcn_data[0].strip().lower()
        vcn_drg = vcn_data[1].strip().lower()
        drg_name=vcn_name+"_drg"
        vcn_igw = vcn_data[2].strip().lower()
        igw_name=vcn_name+"_igw"
        vcn_ngw = vcn_data[3].strip().lower()
        ngw_name=vcn_name+"_ngw"
        vcn_sgw = vcn_data[4].strip().lower()
        sgw_name=vcn_name+"_sgw"
        hub_spoke_none = vcn_data[5].strip().lower()

        vcn_subnet_file = vcn_data[6].strip().lower()
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
                destination = \"""" + drg_destination + """\"
                network_entity_id = "${oci_core_drg.""" + drg_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
            if(drg_ocid!=''):
                for drg_destination in drg_destinations:
                    if (drg_destination != ''):
                        ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination + """\"
                network_entity_id =  \"""" + drg_ocid + """"
                destination_type = "CIDR_BLOCK"
                }
                """

        #Add DRG rules to each Spoke VCN
        if (hub_spoke_none=='spoke' and drg_destinations!=''):
            lpg_name=vcn_name+"_"+hub_vcn_name+"_lpg"
            for drg_destination in drg_destinations:
                if(drg_destination!=''):
                    ruleStr = ruleStr + """
            route_rules { 
                destination = \"""" + drg_destination + """\"
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
                if args.omcs:
                    name_sub, AD, pubpvt, dhcp, configure_sgw, configure_ngw, configure_igw = line.split(',')
                    subnet = name_sub.rsplit("-", 1)[1].strip()
                    name = name_sub.rsplit("-", 1)[0].strip()

                else:
                    [compartment_var_name, name, sub, AD, pubpvt, dhcp, configure_sgw, configure_ngw, configure_igw] = line.split(',')
                    linearr = line.split(",")
                    compartment_var_name = linearr[0].strip()
                    name = linearr[1].strip()
                    subnet = linearr[2].strip()

                if (AD.strip() != 'Regional' and AD.strip() != 'regional'):
                    ad = ADS.index(AD)
                    ad_name_int = ad + 1
                    ad_name = str(ad_name_int)
                else:
                    ad_name = ""

                subnet_res_name = name
                if (str(ad_name) != ''):
                    name1 = name + "-ad" + str(ad_name)
                else:
                    name1 = name

                if (subnet_name_attach_cidr == 'y'):
                    display_name = name1 + "-" + subnet
                else:
                    display_name = name
                #name = name1

                tempStr = tempStr + """ 
    resource "oci_core_route_table" \"""" + name + """"{
        compartment_id = "${var.""" + compartment_var_name + """}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        display_name = \"""" + display_name.strip() + """\" """ + ruleStr

                if configure_sgw.strip() == 'y' and vcn_sgw == 'y':
                    tempStr = tempStr + """
    
            route_rules { 
                destination = "${data.oci_core_services.oci_services.services.0.cidr_block}"
                network_entity_id = "${oci_core_service_gateway.""" + sgw_name + """.id}"
                destination_type = "SERVICE_CIDR_BLOCK"
                }
                """
                if configure_ngw.strip() == 'y' and vcn_ngw == 'y':
                    for ngw_destination in ngw_destinations:
                        if (ngw_destination != ''):
                            tempStr = tempStr + """ 
    
            route_rules { 
                destination = \"""" + ngw_destination + """\"
                network_entity_id = "${oci_core_nat_gateway.""" + ngw_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
                if configure_igw.strip() == 'y' and vcn_igw == 'y':
                    for igw_destination in igw_destinations:
                        if (igw_destination != ''):
                            tempStr = tempStr + """
    
            route_rules { 
                destination = \"""" + igw_destination + """\"
                network_entity_id = "${oci_core_internet_gateway.""" + igw_name + """.id}"
                destination_type = "CIDR_BLOCK"
                }
                """
                tempStr = tempStr + """
                
                    ##Add More rules for subnet """ + subnet_res_name + """##
        }
        """
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()

if drgStr!='':
    drgStr=drgStr+"""
}"""

    tempStr = tempStr + drgStr

if(lpgStr!=''):
    tempStr=tempStr+lpgStr

oname.write(tempStr)
if(fname!=None):
    fname.close()
oname.close()

