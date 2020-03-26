#!/usr/bin/python3
# Author: Shruthi Subramanian
#shruthi.subramanian@oracle.com
import argparse
import re
import pandas as pd
import os
import sys
import ipaddr
import oci
from oci.core.virtual_network_client import VirtualNetworkClient
from oci.identity import IdentityClient
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *

parser = argparse.ArgumentParser(description="CD3 Validator")
parser.add_argument("file", help="Full Path of CD3 file")
parser.add_argument("config", help="Path to config file")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
config = args.config
compartment_ids={}
vcn_ids = {}

config = oci.config.from_file(file_location=config)

#Prepares dictionery containing compartments names and its OCIDs
def get_network_compartment_id(config):
    #Fetch the compartment ID
    identity = IdentityClient(config)
    comp_list = oci.pagination.list_call_get_all_results(identity.list_compartments,config["tenancy"],compartment_id_in_subtree=True)
    compartment_list = comp_list.data
    for compartment in compartment_list:
        if(compartment.lifecycle_state == 'ACTIVE'):
            compartment_ids[compartment.name]=compartment.id

    compartment_ids['root']=config['tenancy']
    return compartment_ids

#Chceks for special characters in dns_label name
def checklabel(lable,count,present):
    lable = str(lable)
    if (lable == "Nan") or (lable == "") or (lable == "NaN") or (lable == "nan"):
        pass
    else:
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if (regex.search(lable) == None):
            pass
        else:
            print ("Error: Label name is not accepted as it has special characters. Change the value at row " + str(count))
            present = True
    return present
#Checks if duplicates are present in dns_label names
def checkduplicatednslabel(df,subset,name,present):
    df = df.dropna(subset=[subset])
    duplicateRowsDF = df[df.duplicated([subset],keep=False)]
    print("Checking for Duplicates in DNS Label column ---->")
    if len(duplicateRowsDF[subset]) > 0:
        rows = list(duplicateRowsDF[subset].index)
        for row in rows:
            print("Duplicate Value "+duplicateRowsDF[subset][row]+" found at Row: " + str(row))
            present = True
    print("<---- End Checking for Duplicates in DNS Label column of "+name+ " Tab")
    return present

#Shows LPG Peering that will be established based on hub_spoke_peer_none column
def showPeering(vcnsob,present):
    #Check if the LPGs are sufficient for creating the peers.
    for left_vcn, value in vcnsob.peering_dict.items():
        right_vcns = value.split(",")
        for right_vcn in right_vcns:
            if(right_vcn==""):
                continue
            right_vcn=right_vcn.strip()
            try:
                if(vcnsob.vcn_lpg_names[left_vcn][0].lower()=='n' or vcnsob.vcn_lpg_names[right_vcn][0].lower()=='n'):
                    print("ERROR!!! Cannot specify n for lpg_required field for either "+left_vcn +" or "+ right_vcn+ "; Since they are part of VCN peering")
                    present = True
                    continue

            except IndexError:
                print("ERROR!!! Insufficient LPGs declared for either "+left_vcn + " or "+right_vcn + ". Check lpg_required column for both VCNs in VCNs tab")
                present = True
                continue
            left_vcn_lpg=vcnsob.vcn_lpg_names[left_vcn][0]
            vcnsob.vcn_lpg_names[left_vcn].pop(0)
            right_vcn_lpg=vcnsob.vcn_lpg_names[right_vcn][0]
            vcnsob.vcn_lpg_names[right_vcn].pop(0)
            print(left_vcn_lpg +" of VCN "+ left_vcn+ " will be peered with "+right_vcn_lpg +" of VCN "+right_vcn)
    return present

#Checks the state of each LPG in OCI and display the details
def lpg_details(comp_id,vcn_id,lpg_name,vcn_list,vcn_name):
    vnc = VirtualNetworkClient(config)
    lpg_list = oci.pagination.list_call_get_all_results(vnc.list_local_peering_gateways,comp_id,vcn_id)
    lpg_list = lpg_list.data
    for lpg in lpg_list:
        print("here  "+lpg.display_name)
        if lpg.display_name == lpg_name:
            print("---- "+lpg_name)
            if lpg.lifecycle_state == "AVAILABLE":
                 if lpg.peering_status == "PEERED":
                    for vcn in vcn_list:
                        if lpg.peer_advertised_cidr == vcn.cidr_block:
                            lpg_peers = oci.pagination.list_call_get_all_results(vnc.list_local_peering_gateways,comp_id, vcn.id)
                            lpg_peers = lpg_peers.data
                            for lpg_peer in lpg_peers:
                                print("LPG with name \""+ lpg_name + "\" exists for VCN \""+vcn_name+"\" and is peered with LPG - \""+lpg_peer.display_name+"\" of VCN - \""+vcn.display_name+"\"  currently.")
                 else:
                    print("LPG with name \""+ lpg_name + "\" exists for VCN \""+vcn_name+"\" and is in "+lpg.peering_status+" state currently.")

# Checks for duplicates
def checkIfDuplicates(listOfElems):
    setOfElems = set()
    for elem in listOfElems:
        if elem in setOfElems:
            return elem
        else:
            setOfElems.add(elem)
    return False

# Checks if the CIDRs overlap for each VCN mentioned in excelsheet
def validate_vcn_cidr(filename,present):
    cidr_list = []
    duplicate = []
    count = 0

    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    print("\nValidating VCN CIDRs --->")
    for i in df.index:
        if str(df[df.columns[3]][i]) == "Nan" or str(df[df.columns[3]][i]) == "NAN" or str(df[df.columns[3]][i]) == "nan":
            continue
        else:
            cidr_list.append(str(df[df.columns[3]][i]))

    for x in enumerate(cidr_list):
        if x[0] != None and x[0] + 1 != None:
            cidr_left = x[1]
            for y in enumerate(cidr_list):
                if y[0] != None and y[0] + 1 != None:

                    cidr_right = y[1]
                    cidr_left = ipaddr.IPNetwork(cidr_left)
                    cidr_right = ipaddr.IPNetwork(cidr_right)

                    if str(cidr_left) == str(cidr_right):
                        break
                    else:
                        bool = cidr_right.overlaps(cidr_left)
                        if bool == True:
                            duplicate.append(df[df.columns[2]][x[0]])
                            duplicate = set(duplicate)
                            duplicate = list(duplicate)
                            if count == 0:
                                print("The below CIDR Ranges overlap. Please change the values !!!")
                                count = count + 1
                            print(str(cidr_right) + " of " + df[df.columns[2]][y[0]] + " overlaps with CIDR of " +
                                  df[df.columns[2]][x[0]])
                            present = True
    #Checks if the CIDRs have duplicates
    result = checkIfDuplicates(cidr_list)
    if result:
        print('VCN CIDR ' + result + ' is duplicated. Please check !!!')
        present = True
    print("<--- End Validating VCN CIDRs")
    return present

#Checks if the CIDRs overlap for each Subnet mentioned in excelsheet
def validate_subnet_cidr(filename,present):
    cidr_list = []
    duplicate = []
    count = 0

    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)
    print("\nValidating Subnet CIDRs --->")
    for i in df.index:
        if str(df[df.columns[4]][i]) == "Nan" or str(df[df.columns[4]][i]) == "NAN" or str(df[df.columns[4]][i]) == "nan":
            continue
        else:
            cidr_list.append(str(df[df.columns[4]][i]))

    for x in enumerate(cidr_list):
        if x[0] != None and x[0] + 1 != None:
            cidr_left = x[1]
            for y in enumerate(cidr_list):
                if y[0] != None and y[0] + 1 != None:

                    cidr_right = y[1]
                    cidr_left = ipaddr.IPNetwork(cidr_left)
                    cidr_right = ipaddr.IPNetwork(cidr_right)

                    if str(cidr_left) == str(cidr_right):
                        break
                    else:
                        bool = cidr_right.overlaps(cidr_left)
                        if bool == True:
                            duplicate.append(df[df.columns[3]][x[0]])
                            duplicate = set(duplicate)
                            duplicate = list(duplicate)
                            if count == 0:
                                print("The below CIDR Ranges overlap. Please change the values !!!")
                                count = count + 1
                            print(str(cidr_right) + " of " + df[df.columns[3]][y[0]] + " overlaps with CIDR of " +
                                  df[df.columns[3]][x[0]])
                            present = True
    # Checks if the CIDRs have duplicates
    result = checkIfDuplicates(cidr_list)
    if result:
        print('Subnet CIDR ' + result + ' is duplicated. Please check !!!')
        present = True
    print("<--- End Validating Subnet CIDRs")
    return present

#Compare 2 lists for difference in their elements
def check_item(List1, List2, name,present):
    list = []
    for element in List2:
        if element not in List1:
            if element == "nan" or element == "NaN" or element == "Nan":
                continue
            else:
                list.append(element)
    if len(list)>=1:
        print("The below VCN names are not present in VCNs tab.Please check the VCN name in " + name + " Tab and try again")
        print(*list, sep = "\n")
        present = True
    return present

#Check if the VCN names present in Subnets and DHCP Tabs are present in VCN Tab
def validate_vcn_names(filename,present):
    subnet_list = []
    vcn_list = []
    dhcp_list = []

    #Read the excel sheets - Subnets, VCNs and DHCP
    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    dfv = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    dfv = dfv.dropna(how='all')
    dfv = dfv.reset_index(drop=True)

    dfh = pd.read_excel(filename, sheet_name='DHCP', skiprows=1)
    dfh = dfh.dropna(how='all')
    dfh = dfh.reset_index(drop=True)

    print("\nValidating VCNs mentioned in the Subnets and DHCP Tabs --->")

    #Store the VCN names in each of these sheets in separate lists to compare later
    for i in dfv.index:
        if str(dfv[dfv.columns[0]][i]) not in commonTools.endNames:
            if str(dfv[dfv.columns[2]][i]) == "Nan" or str(dfv[dfv.columns[2]][i]) == "NAN" or str(dfv[dfv.columns[2]][i]) == "nan":
                continue
            else:
                vcn_list.append(str(dfv[dfv.columns[2]][i]))


    for i in df.index:
        if str(df[df.columns[0]][i]) not in commonTools.endNames:
            if str(df[df.columns[2]][i]) == "Nan" or str(df[df.columns[2]][i]) == "NAN" or str(df[df.columns[2]][i]) == "nan":
                continue
            else:
                subnet_list.append(str(df[df.columns[2]][i]))


    for i in dfh.index:
        if str(dfh[dfh.columns[0]][i]) not in commonTools.endNames:
            if str(dfh[dfh.columns[2]][i]) == "Nan" or str(dfh[dfh.columns[2]][i]) == "NAN" or str(dfh[dfh.columns[2]][i]) == "nan":
                continue
        else:
            dhcp_list.append(str(dfh[dfh.columns[2]][i]))

    #Check if the vcn names mentioned in Subnets and DHCP Tabs are present in VCN tab as well
    statevcn = check_item(vcn_list,subnet_list,"Subnets",present)
    statedhcp = check_item(vcn_list,dhcp_list,"DHCP",present)
    print("<--- End of Validating VCNs mentioned in the Subnets and DHCP Tabs")
    if statevcn == True or statedhcp == True:
        return True
    return present

#Check if subnets tab is compliant
def subnets(filename,present):

    # Read the Subnets tab from excel
    df = pd.read_excel(filename, sheet_name='Subnets', skiprows=1)
    #Drop null values
    df = df.dropna(how='all')
    #Reset index
    df = df.reset_index(drop=True)

    # Counter to fetch the row number
    count = 0

    # Check if the column dns_label has duplicate values
    present = checkduplicatednslabel(df,str(df.columns[16]), "Subnets",present)

    print ("\nChecking for null or wrong values in each row ---->")
    #Loop through each row
    for i in df.index:
        count = count + 1
        print("ROW  " + str(count)+":")
        for j in df.keys():

            # Check for <END> in the inputs; if found the validation ends there and return the status of flag
            if (str(df[j][i]) in commonTools.endNames):
                print("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
                print("<--- End Checking for null or wrong values in each row")
                return present
            else:
                # Check if the dns_label field has special characters
                if j == str(df.columns[16]):
                    present = checklabel(df[j][i],count,present)

                # Check for null values and display appropriate message
                if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                    if j == str(df.columns[16]) or j == str(df.columns[7]):
                        pass
                    else:
                        print("Empty value at column = " +j)
                        present = True

                #Check if the Service and Internet gateways are set appropriately; if not display the message;
                if j == str(df.columns[11]):
                    if str(df[j][i]) == "-"  or str(df[j][i]) == "n" or str(df[j][i]) == "all_services" or str(df[j][i]) == "object_storage":
                        if (str(df.columns[13])[i] == "y" and str(str(df.columns[11])[i]) == "all_services"):
                            print("Internet Gateway target cannot be used together with Service Gateway target for All Services in the same routing table. Change either the value of SGW or IGW configure route !!")
                            present = True
                    else:
                        print("The value entered for configure SGW route should be either '-' ,'n' or 'object_storage' or 'all_services' and cannot be "+df[j][i])
                        present = True
    print("<--- End Checking for null or wrong values in each row")
    return present

#Check if VCNs tab is compliant
def vcns(filename,present,comp_ids):
    vcnsob = parseVCNs(filename)
    print("Show LPG's Status  --->")

    #Read the VCNs tab from excel
    df = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
    # Drop null values
    df = df.dropna(how='all')
    # Reset index
    df = df.reset_index(drop=True)

    #Loop through each row
    for i in df.index:
        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df[df.columns[0]][i]) in commonTools.endNames:
            print("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            print("\nPlease verify if the LPGs status is as you desire otherwise please correct the order of LPGs!!!")
            print("<---End LPG's Status\n")
            return present

        #Check if the Compartment,VCN and lpg exists in OCI console for each of the lpgs mentioned in the excel
        for lpg in vcnsob.vcn_lpg_names[str(df[df.columns[2]][i])]:
            if(lpg!='n'):
                comp_name = str(df[df.columns[1]][i])
                vcn_name = str(df[df.columns[2]][i])
                try:
                    vnc = VirtualNetworkClient(config)
                    vcn_list = oci.pagination.list_call_get_all_results(vnc.list_vcns, comp_ids[comp_name])
                    vcn_list = vcn_list.data

                    #Check if the lpg is present and is Available; if so check its peering status; else display appropriate message
                    for vcn in vcn_list:
                        if (vcn.lifecycle_state == 'AVAILABLE'):
                            vcn_ids[vcn.display_name] = vcn.id
                    try:
                        vcn_id = vcn_ids[vcn_name]
                        print("calling----lpg_details for "+vcn_name+",,"+lpg)
                        lpg_details(comp_ids[comp_name], vcn_id, lpg, vcn_list, vcn_name)

                    except KeyError:
                        print("VCN with name \"" + vcn_name + "\" does not exist. So this VCN and LPG - \"" + lpg + "\" will be created new.")
                        pass
                except KeyError:
                    print("Compartment with name \"" + comp_name + "\" does not exist. So the VCN(" + vcn_name + ") and LPG(" + lpg + ") will be created new once the compartment is created..")
                    pass
    print("Below Peering would be established new ======>")

    #Show the peering details of each lpg in Hub,Spoke or Peer VCNs
    present = showPeering(vcnsob, present)
    print("\nPlease verify if the LPGs status is as you desire otherwise please correct the order of LPGs!!!")
    print("<---End LPG's Status\n")

    #Counter to fetch the row number
    count = 0

    #Check if the column dns_label has duplicate values
    present = checkduplicatednslabel(df,str(df.columns[10]), "VCNs",present)
    print ("\nChecking for null or wrong values in each row ---->")

    #Loop through each row
    for i in df.index:
        count = count + 1
        print("ROW  " + str(count)+":")

        # Check for <END> in the inputs; if found the validation ends there and return the status of flag
        if str(df[df.columns[0]][i]) in commonTools.endNames:
            print("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
            print("<--- End Checking for null or wrong values in each row")
            return present

        for j in df.keys():
            if (str(df[j][i]) not in commonTools.endNames):
                #Check if the dns_label field has special characters
                if j == str(df.columns[10]):
                    checklabel(df[j][i], count,present)

            #Check for null values and display appropriate message
            if (str(df[j][i]) == "NaN" or str(df[j][i]) == "nan" or str(df[j][i]) == ""):
                if j == str(df.columns[10]):
                    continue
                else:
                    print("Empty value at column = " + j)
                    present = True

    print("<--- End Checking for null or wrong values in each row")
    return present

#Checks if the fields in DHCP tab are compliant
def dhcp(filename,present):
    #Read DHCP tab from excel
    df = pd.read_excel(filename, sheet_name='DHCP', skiprows=1)
    #Drop null values
    df = df.dropna(how='all')
    #Reset index
    df = df.reset_index(drop=True)

    empty = ['', 'Nan', 'NaN', 'nan']

    # Counter to fetch the row number
    count = 0

    print("\nChecking for null or wrong values in each row ---->")
    for i in df.index:
        count = count + 1
        print("ROW  " + str(count) + ":")
        for j in df.keys():

            #Check for <END> in the inputs; if found the validation ends there and return the status of flag
            if str(df[df.columns[0]][i]) in commonTools.endNames:
                print("Reached <END> Tag. Validation ends here, any data beyond this tag will not be checked for errors !!!")
                print("<--- End Checking for null or wrong values in each row")
                return present

            #Check the customer_dns_servers column; if empty return error based on the value in server_type column
            if j == str(df.columns[6]):
                if str(df[df.columns[6]][i]) in empty:
                    if str(df[df.columns[4]][i]) == "CustomDnsServer":
                        print("'custom_dns_servers' column cannot be empty if server type is 'CustomDnsServer'. Please make sure you have a value and try again!")
                        present = True
                    elif str(df[df.columns[4]][i]) == "VcnLocalPlusInternet":
                        continue
            else:
                #Check if there are any field that is empty; display appropriate message
                if str(df[j][i]) in empty and j != str(df.columns[5]):
                    print("Empty value at column = " + j)
                    present = True
    print("<--- End Checking for null or wrong values in each row")
    return present

def main():
    #CD3 Validation begins here for Sunbnets, VCNs and DHCP tabs
    #Flag to check if for errors
    present = False

    print("============================= Verifying Subnets Tab ==========================================\n")
    subpres = subnets(filename,present)
    subprescidr = validate_subnet_cidr(filename,present)

    print("\n============================= Verifying VCNs Tab ==========================================\n")
    comp_ids = get_network_compartment_id(config)
    vcn = vcns(filename,present,comp_ids)
    vcnpres = validate_vcn_cidr(filename,present)
    vcnprescidr = validate_vcn_names(filename,present)

    print("\n============================= Verifying DHCP Tab ==========================================\n")
    dhcps = dhcp(filename,present)

    #Prints the final result; once the validation is complete
    if subprescidr == True or subpres == True or vcnpres == True  or vcnprescidr == True or vcn == True or dhcps == True:
        print("\n")
        print("Impression:")
        print("ERROR: Make appropriate changes to CD3 Values and try again!!!")
    elif subprescidr == False and subpres == False and vcnpres == False  and vcnprescidr == False and vcn == False and dhcps == False:
        print("\n")
        print("Impression:")
        print("There are no errors in CD3. You are good to proceed !!!")

if __name__ == '__main__':

    #Execution of the code begins here
    main()