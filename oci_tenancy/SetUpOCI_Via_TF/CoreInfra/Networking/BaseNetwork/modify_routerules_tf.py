#!/bin/python

import sys
import argparse
import shutil
import re
import pandas as pd
######
# Takes in input csv or CD3 excel which contains routerules to be updated for the subnet and updates the routes tf file created using BaseNetwork TF generation.
# ######



parser = argparse.ArgumentParser(description="Updates routelist for subnet. It accepts input file which contains new rules to be added to the existing rule list of the subnet.")
parser.add_argument("inputfile", help="Required; Full Path to input route file (either csv or CD3 excel file) containing rules to be updated; See example folder for sample format: add_routes-example.txt")
parser.add_argument("routefile", help= "Required: Full path of routes tf file which will be modified. This should ideally be the tf file which was created using create_all_tf_objects.py script.")
parser.add_argument("--overwrite",help="This will overwrite all sec rules in OCI with whatever is specified in cd3 excel file sheet- SecRulesinOCI (true or false) ",required=False)


if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
routefile = args.routefile
inputfile = args.inputfile

# Backup the existing Routes tf file
shutil.copy(routefile, routefile + "_backup")

if args.overwrite is not None:
    overwrite = str(args.overwrite)
else:
    overwrite = "false"

ruleStr=""
subnets_done=[]
#If input is CD3 excel file
if('.xls' in inputfile):
    endNames = {'<END>', '<end>'}
    NaNstr = 'NaN'
    if (overwrite == 'true'):
        print("Reading RouteRulesinOCI sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='RouteRulesinOCI')
        for i in df.index:
            subnet_name = df.iat[i, 0]
            if (str(subnet_name).lower() == NaNstr.lower()):
                continue
            dest_cidr = df.iat[i, 1]
            dest_cidr = str(dest_cidr).strip()
            dest_obj = df.iat[i, 2]
            dest_obj = str(dest_obj).strip()
            dest_type = df.iat[i, 3]
            dest_type = str(dest_type).strip()
            vcn_name = df.iat[i,4]
            vcn_name = vcn_name.strip()
            comp_name = df.iat[i,5]
            comp_name = comp_name.strip()
            if('in-oracle-services-network' in dest_cidr):
                dest_cidr="${data.oci_core_services.oci_services.services.0.cidr_block}"
            if(subnet_name=='Route Table associated with DRG'):
                rt_var = vcn_name + "_drg_rt"
            elif('Default Route Table for' in subnet_name):
                continue;
            elif('Route Table associated with LPG' in subnet_name):
                lpg_name= subnet_name.split('LPG')
                rt_var = lpg_name[1].strip() + "_rt"
            # display name contaoin AD1, AD2 or AD3 and CIDR
            elif ('-1-10.' in subnet_name or '-2-10.' in subnet_name or '-3-10.' in subnet_name):
                rt_var=subnet_name.rsplit("-",2)[0]
            #display name contains CIDR
            elif('-10.' in subnet_name):
                rt_var=subnet_name.rsplit("-",1)[0]
            else:
                rt_var=subnet_name

            if(subnet_name not in subnets_done):
                if(len(subnets_done)!=0):
                    ruleStr=ruleStr+"""
}"""

                ruleStr = ruleStr + """
resource "oci_core_route_table" \"""" + rt_var + """"{
    compartment_id = "${var.""" + comp_name + """}"
    vcn_id = "${oci_core_vcn.""" + vcn_name + """.id}"
    
    ##Add More rules for subnet """ + rt_var+ """##
    
    route_rules {
        
            destination =\"""" + dest_cidr + """\"
            network_entity_id = \"""" + dest_obj + """\"
            destination_type = \"""" + dest_type + """\"
        }
        """
                subnets_done.append(subnet_name)

            else:
                ruleStr=ruleStr+"""
        route_rules {
            destination =\"""" + dest_cidr + """\"
            network_entity_id = \"""" + dest_obj + """\"
            destination_type = \"""" + dest_type + """\"
        }
        """
        ruleStr=ruleStr+"""
}"""
        with open(routefile, 'w') as f:
            f.write(ruleStr)

    elif(overwrite=='false'):
        print("Reading AddRouteRules sheet of cd3")
        df = pd.read_excel(inputfile, sheet_name='AddRouteRules')
        for i in df.index:
            subnet_name = df.iat[i, 0]
            subnet_name = subnet_name.strip()

            if (subnet_name in endNames):
                break

            dest_cidr = df.iat[i, 1]
            dest_cidr=dest_cidr.strip()
            dest_obj = df.iat[i, 2]
            dest_obj=dest_obj.strip()
            dest_type = df.iat[i, 3]
            dest_type=dest_type.strip()


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
            with open(routefile) as f:
                data = f.read()

            with open(routefile, 'w') as f:
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
            print ("processing : " + route)
            subnet_name = route.split(":")[0]
            subnet_name=subnet_name.strip()
            dest_cidr = route.split(":")[1]
            dest_cidr=dest_cidr.strip()
            dest_obj = route.split(":")[2]
            dest_obj=dest_obj.strip()
            dest_type = route.split(":")[3]
            dest_type = dest_type.strip()

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
            with open(routefile) as f:
                data = f.read()

            with open(routefile, 'w') as f:
                updated_data = re.sub(searchString, strRule, data)
                f.write(updated_data)
    fname.close()

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")

print("Route Rules added to the file successfully. Please run terraform plan from your outdir to see the changes")
f.close()