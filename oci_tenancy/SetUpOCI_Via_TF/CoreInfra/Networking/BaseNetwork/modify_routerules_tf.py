#!/usr/bin/python3

import sys
import argparse
import shutil
import re
import pandas as pd
import glob
import datetime
import os
######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--overwrite",help="This will overwrite all sec rules in OCI with whatever is specified in cd3 excel file sheet- SecRulesinOCI (yes or no) ",required=False)


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
inputfile = args.inputfile
outdir=args.outdir


if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "no"

data=""
tfStr={}
subnets_done={}
routefile={}
x = datetime.datetime.now()
date = x.strftime("%f").strip()

#If input is CD3 excel file
if('.xls' in inputfile):
    df_info = pd.read_excel(inputfile, sheet_name='VCN Info', skiprows=1)
    properties = df_info['Property']
    values = df_info['Value']

    all_regions = str(values[7]).strip()
    all_regions = all_regions.split(",")
    all_regions = [x.strip().lower() for x in all_regions]
    for reg in all_regions:
        tfStr[reg] = ''
        subnets_done[reg]=[]
        for file in glob.glob(outdir+'/'+reg + '/*routes.tf'):
            routefile[reg] = file
            # Backup the existing Routes tf file
            print("Backing Up "+routefile[reg])
            shutil.copy(routefile[reg], routefile[reg] + "_backup" + date)


    endNames = {'<END>', '<end>'}
    NaNstr = 'NaN'
    if (overwrite == 'yes'):
        print("\nReading RouteRulesinOCI sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI')
        df.dropna(how='all')
        for i in df.index:
            region = df.iat[i, 0]
            region = region.strip().lower()
            if region not in all_regions:
                print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                exit(1)
            comp_name = df.iat[i, 1]
            comp_name = comp_name.strip()
            vcn_name = df.iat[i, 2]
            vcn_name = vcn_name.strip()
            subnet_name = df.iat[i, 3]
            if (str(subnet_name).lower() == NaNstr.lower()):
                continue
            dest_cidr = df.iat[i, 4]
            dest_cidr = str(dest_cidr).strip()
            dest_objs = df.iat[i, 5]
            dest_objs = str(dest_objs).strip().split(":")

            if ('ngw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_objs[1] + ".id}"

            elif ('sgw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_service_gateway." + dest_objs[1] + ".id}"

            elif ('igw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_objs[1] + ".id}"

            elif ('lpg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_objs[1] + ".id}"
            elif ('drg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_drg." + dest_objs[1] + ".id}"
            else:
                dest_obj = dest_objs[0]


            dest_type = df.iat[i, 6]
            dest_type = str(dest_type).strip()
            if('Route Table associated with DRG' in subnet_name):
                drg_name = subnet_name.split('DRG ')[1].strip()
                #rt_var = vcn_name + "_drg_rt"
                rt_var = drg_name + "_rt"
            elif('Default Route Table for' in subnet_name):
                continue;
            elif('Route Table associated with LPG' in subnet_name):
                lpg_name= subnet_name.split('LPG')
                rt_var = lpg_name[1].strip() + "_rt"
            else:
                rt_var=subnet_name

            if(subnet_name not in subnets_done[region]):
                if(len(subnets_done[region])!=0):
                    tfStr[region]=tfStr[region]+"""
    }"""

                tfStr[region] = tfStr[region] + """
    resource "oci_core_route_table" \"""" + rt_var + """"{
        compartment_id = "${var.""" + comp_name + """}"
        vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
        
        ##Add More rules for subnet """ + subnet_name+ """##
        
        route_rules {
            
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """
                subnets_done[region].append(subnet_name)

            else:
                tfStr[region]=tfStr[region]+"""
            route_rules {
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """
        for reg in all_regions:
            if(tfStr[reg]!=''):
                tfStr[reg]=tfStr[reg]+"""
}"""
                with open(routefile[reg], 'w') as f:
                    f.write(tfStr[reg])
                print("Route Rules added to the file "+routefile[reg]+" successfully. Please run terraform plan from your outdir to see the changes")

    elif(overwrite=='no'):
        print("Reading AddRouteRules sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='AddRouteRules')
        df.dropna(how='all')
        df.drop_duplicates()
        for i in df.index:
            region = df.iat[i, 0]
            region = str(region).lower()

            if (region in endNames):
                break
            if(region==NaNstr.lower() or region=='region'):
                continue
            region=region.strip()

            if region not in all_regions:
                print("Invalid Region; It should be one of the values mentioned in VCN Info tab")
                exit(1)
            comp_name = df.iat[i, 1]
            vcn_name = df.iat[i, 2]
            dest_cidr = df.iat[i, 4]
            dest_cidr = str(dest_cidr).strip()
            dest_objs = df.iat[i, 5]
            dest_objs = str(dest_objs).strip().split(":")
            if ('ngw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_objs[1] + ".id}"

            elif ('sgw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_service_gateway." + dest_objs[1] + ".id}"

            elif ('igw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_objs[1] + ".id}"

            elif ('lpg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_objs[1] + ".id}"
            elif ('drg' in dest_objs[0].lower() and 'ocid1' not in dest_objs[0].lower()):
                dest_obj = "${oci_core_drg." + dest_objs[1] + ".id}"
            else:
                dest_obj = dest_objs[0]


            dest_type = df.iat[i, 6]
            dest_type = str(dest_type).strip()

            subnet_name = df.iat[i, 3]
            subnet_name = subnet_name.strip()

            searchString = "##Add More rules for subnet " + subnet_name + "##"
            strRule = ""
            strRule = strRule + """
        route_rules {
            destination = \"""" + dest_cidr + """\"
            network_entity_id = \"""" + dest_obj + """\"
            destination_type = \"""" + dest_type + """\"
        }
        """
            strRule1 = strRule + "##Add More rules for subnet " + subnet_name + "##"

            # Update file contents
            with open(routefile[region]) as f:
                data = f.read()
            f.close()
            #if(strRule not in data):
            updated_data = re.sub(searchString, strRule1, data)
            #else:
            #    updated_data=data

            #if(data!=updated_data):
            with open(routefile[region], 'w') as f:
                f.write(updated_data)
            f.close()
        print("Route Rules added successfully. Please run terraform plan from your outdir to see the changes")
            #else:
            #    print("Nothing to add")

# If input is a csv file
elif ('.csv' in inputfile):
    fname = open(inputfile, "r")
    # Read the input csv file
    endNames = {'<END>', '<end>'}
    all_regions=os.listdir(outdir)
    for reg in all_regions:
        tfStr[reg] = ''
        subnets_done[reg] = []
        for file in glob.glob(outdir + '/' + reg + '/*routes.tf'):
            routefile[reg] = file

    for route in fname:
        if (route.strip() in endNames):
            break
        if not route.startswith('#') and route != '\n':
            subnet_name = route.split(",")[0]
            subnet_name=subnet_name.strip()
            dest_cidr = route.split(",")[1]
            dest_cidr=dest_cidr.strip()
            dest_objs = route.split(",")[2]
            dest_objs = dest_objs.strip().split(":")

            if ('ngw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_objs[1] + ".id}"
            elif ('sgw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_service_gateway." + dest_objs[1] + ".id}"
            elif ('igw' in dest_objs[0].lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_objs[1] + ".id}"
            elif ('lpg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_objs[1] + ".id}"
            elif ('drg' in dest_objs[0].lower()):
                dest_obj = "${oci_core_drg." + dest_objs[1] + ".id}"
            else:
                dest_obj = dest_objs[0]
            dest_type = route.split(",")[3]
            dest_type = dest_type.strip()
            region=route.split(",")[4]
            region=region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                continue

            searchString = "##Add More rules for subnet "+subnet_name+"##"
            strRule = ""
            strRule = strRule+"""
                route_rules {
                destination = \"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
                }
                """
            strRule1 = strRule + "##Add More rules for subnet " +subnet_name+"##"

            # Update file contents
            with open(routefile[region]) as f:
                data = f.read()
            f.close()
            #if(strRule not in data):
            updated_data = re.sub(searchString, strRule1, data)
            #else:
            #    updated_data=data

            #if(data!=updated_data):
            with open(routefile[region], 'w') as f:
                f.write(updated_data)
            f.close()
    print("Route Rules added to the file successfully. Please run terraform plan from your outdir to see the changes")
            #else:
            #    print("Nothing to add")

    fname.close()

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
