#!/bin/python

import sys
import argparse
import shutil
import re
import pandas as pd
import glob
######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
#parser.add_argument("routefile", help= "Required: Full path of routes tf file which will be modified. This should ideally be the tf file which was created using create_all_tf_objects.py script.")
parser.add_argument("outdir",help="directory path for output tf files ")
parser.add_argument("--overwrite",help="This will overwrite all sec rules in OCI with whatever is specified in cd3 excel file sheet- SecRulesinOCI (yes or no) ",required=False)


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
#routefile = args.routefile
inputfile = args.inputfile
outdir=args.outdir

ash_dir=outdir+"/ashburn"
phx_dir=outdir+"/phoenix"
routefile_ash=''
routefile_phx=''
for file in glob.glob(ash_dir+'/*routes.tf'):
    routefile_ash=file
for file in glob.glob(phx_dir+'/*routes.tf'):
    routefile_phx=file

# Backup the existing Routes tf file
shutil.copy(routefile_ash, routefile_ash + "_backup")
shutil.copy(routefile_phx, routefile_phx + "_backup")

if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "no"

data=""
tempStrASH = ""
tempStrPHX = ""

subnets_done_ash=[]
subnets_done_phx=[]
#If input is CD3 excel file
if('.xls' in inputfile):
    endNames = {'<END>', '<end>'}
    NaNstr = 'NaN'
    if (overwrite == 'yes'):
        print("\nReading RouteRulesinOCI sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI')
        df.dropna(how='all')
        for i in df.index:

            region = df.iat[i, 0]
            region = region.strip().lower()
            comp_name = df.iat[i, 1]
            comp_name = comp_name.strip()
            vcn_name = df.iat[i, 2]
            vcn_name = vcn_name.strip()

            subnet_name = df.iat[i, 3]
            if (str(subnet_name).lower() == NaNstr.lower()):
                continue
            dest_cidr = df.iat[i, 4]
            dest_cidr = str(dest_cidr).strip()
            dest_obj = df.iat[i, 5]
            dest_obj = str(dest_obj).strip()
            if('_ngw' in dest_obj.lower()):
                dest_obj="${oci_core_nat_gateway." + dest_obj + ".id}"

            if ('_igw' in dest_obj.lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_obj + ".id}"

            if ('_lpg' in dest_obj.lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_obj + ".id}"

            if ('_drg' in dest_obj.lower()):
                dest_obj = "${oci_core_drg." + dest_obj + ".id}"


            dest_type = df.iat[i, 6]
            dest_type = str(dest_type).strip()
            #if('in-oracle-services-network' in dest_cidr):
            #    dest_cidr="${data.oci_core_services.oci_services.services.0.cidr_block}"
            if('Route Table associated with DRG' in subnet_name):
                rt_var = vcn_name + "_drg_rt"
            elif('Default Route Table for' in subnet_name):
                continue;
            elif('Route Table associated with LPG' in subnet_name):
                lpg_name= subnet_name.split('LPG')
                rt_var = lpg_name[1].strip() + "_rt"
            else:
                rt_var=subnet_name

            if(region=='ashburn'):
                if(subnet_name not in subnets_done_ash):
                    if(len(subnets_done_ash)!=0):
                        tempStrASH=tempStrASH+"""
    }"""

                    tempStrASH = tempStrASH + """
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
                    subnets_done_ash.append(subnet_name)

                else:
                    tempStrASH=tempStrASH+"""
            route_rules {
                destination =\"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
            }
            """
            if (region == 'phoenix'):
                if (subnet_name not in subnets_done_phx):
                    if (len(subnets_done_phx) != 0):
                        tempStrPHX = tempStrPHX + """
                }"""

                    tempStrPHX = tempStrPHX + """
                resource "oci_core_route_table" \"""" + rt_var + """"{
                    compartment_id = "${var.""" + comp_name + """}"
                    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"

                    ##Add More rules for subnet """ + subnet_name + """##

                    route_rules {

                            destination =\"""" + dest_cidr + """\"
                            network_entity_id = \"""" + dest_obj + """\"
                            destination_type = \"""" + dest_type + """\"
                        }
                        """
                    subnets_done_phx.append(subnet_name)

                else:
                    tempStrPHX = tempStrPHX + """
                        route_rules {
                            destination =\"""" + dest_cidr + """\"
                            network_entity_id = \"""" + dest_obj + """\"
                            destination_type = \"""" + dest_type + """\"
                        }
                        """
        tempStrASH=tempStrASH+"""
}"""
        tempStrPHX = tempStrPHX + """
}"""
        with open(routefile_ash, 'w') as f:
            f.write(tempStrASH)
        with open(routefile_phx, 'w') as f:
            f.write(tempStrPHX)

    elif(overwrite=='no'):
        print("Reading AddRouteRules sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='AddRouteRules')
        df.dropna(how='all')
        for i in df.index:
            region = df.iat[i, 0]
            region = str(region).lower()

            if (region in endNames):
                break
            if(region==NaNstr.lower()):
                continue
            region=region.strip()
            comp_name = df.iat[i, 1]
            vcn_name = df.iat[i, 2]
            dest_cidr = df.iat[i, 4]
            dest_cidr = str(dest_cidr).strip()
            dest_obj = df.iat[i, 5]
            dest_obj = str(dest_obj).strip()
            if ('_ngw' in dest_obj.lower()):
                dest_obj = "${oci_core_nat_gateway." + dest_obj + ".id}"

            if ('_igw' in dest_obj.lower()):
                dest_obj = "${oci_core_internet_gateway." + dest_obj + ".id}"

            if ('_lpg' in dest_obj.lower()):
                dest_obj = "${oci_core_local_peering_gateway." + dest_obj + ".id}"

            if ('_drg' in dest_obj.lower()):
                dest_obj = "${oci_core_drg." + dest_obj + ".id}"


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
            strRule = strRule + "##Add More rules for subnet " + subnet_name + "##"

            # Update file contents
            if(region=='ashburn'):
                with open(routefile_ash) as f:
                    data = f.read()

                with open(routefile_ash, 'w') as f:
                    updated_data = re.sub(searchString, strRule, data)
                    f.write(updated_data)
            if (region == 'phoenix'):
                with open(routefile_phx) as f:
                    data = f.read()

                with open(routefile_phx, 'w') as f:
                    updated_data = re.sub(searchString, strRule, data)
                    f.write(updated_data)



# If input is a csv file
elif ('.csv' in inputfile):
    fname = open(inputfile, "r")
    # Read the input csv file
    endNames = {'<END>', '<end>'}

    for route in fname:
        if (route.strip() in endNames):
            break
        if not route.startswith('#') and route != '\n':
            subnet_name = route.split(":")[0]
            subnet_name=subnet_name.strip()
            dest_cidr = route.split(":")[1]
            dest_cidr=dest_cidr.strip()
            dest_obj = route.split(":")[2]
            dest_obj=dest_obj.strip()
            dest_type = route.split(":")[3]
            dest_type = dest_type.strip()
            region=route.split(":")[4]

            searchString = "##Add More rules for subnet "+subnet_name+"##"
            strRule = ""
            strRule = strRule+"""
                route_rules {
                destination = \"""" + dest_cidr + """\"
                network_entity_id = \"""" + dest_obj + """\"
                destination_type = \"""" + dest_type + """\"
                }
                """
            strRule = strRule + "##Add More rules for subnet " +subnet_name+"##"

            # Update file contents
            if (region == 'phoenix'):
                with open(routefile_phx) as f:
                    data = f.read()

                with open(routefile_phx, 'w') as f:
                    updated_data = re.sub(searchString, strRule, data)
                    f.write(updated_data)

    fname.close()

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")

print("Route Rules added to the file successfully. Please run terraform plan from your outdir to see the changes")
f.close()