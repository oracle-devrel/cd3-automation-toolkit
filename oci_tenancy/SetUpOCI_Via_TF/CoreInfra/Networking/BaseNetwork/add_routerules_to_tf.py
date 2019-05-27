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

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()
routefile = args.routefile
inputfile = args.inputfile

# Backup the existing Routes tf file
shutil.copy(routefile, routefile + "_backup")

#If input is CD3 excel file
if('.xls' in inputfile):
    endNames = {'<END>', '<end>'}
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