import argparse
import configparser
import os
import sys
from commonTools import *

parser = argparse.ArgumentParser(description="Sets Up OCI via TF")
parser.add_argument("propsfile",help="Full Path of properties file containing input variables. eg setUpOCI.properties")

args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

#Read Config file Variables
try:
    input_format=config.get('Default','input').strip()
    input_nongf_tenancy = config.get('Default', 'non_gf_tenancy').strip()

    input_outdir = config.get('Default', 'outdir').strip()
    if(input_outdir==''):
        print("input outdir location cannot be left blank. Exiting... ")
        exit(1)

    input_prefix = config.get('Default', 'prefix').strip()
    if(input_prefix==''):
        print("input prefix value cannot be left blank. Exiting... ")
        exit(1)

    input_config_file=config.get('Default', 'config_file').strip()
except Exception as e:
    print(e)
    print('Check if input properties exist and try again..exiting...`    ')
    exit()

#Set Default Value as cd3 and non-greenfield tenancy as false
if(input_format==''):
    input_format='cd3'
if (input_nongf_tenancy == ''):
    input_nongf_tenancy="false"

if(input_format=='cd3'):
    try:
        input_cd3file=config.get('Default','cd3file').strip()
        if(input_cd3file==''):
            print("input cd3file location cannot be left blank. Exiting... ")
            exit(1)
        elif(".xls" not in input_cd3file):
            print("valid formats for input cd3file are either .xls or .xlsx")
            exit(1)

    except Exception as e:
        print(e)
        print('Check if input properties exist and try again..exiting...`    ')
        exit()

if(input_format=='csv'):
    try:
        input_vcninfo=config.get('Default','vcn_info_file').strip()
        input_compartments_csv = config.get('Default', 'compartments_csv').strip()
        input_groups_csv = config.get('Default', 'groups_csv').strip()
        input_dedicatedhosts_csv = config.get('Default', 'dedicatedhosts_csv').strip()
        input_instances_csv = config.get('Default', 'instances_csv').strip()
        input_blocks_csv = config.get('Default', 'blocks_csv').strip()
        input_tag_servers_csv = config.get('Default', 'tag_servers_csv').strip()
        input_tag_volumes_csv = config.get('Default', 'tag_volumes_csv').strip()
        input_add_routes_csv = config.get('Default', 'add_routes_csv').strip()
        input_add_secrules_csv = config.get('Default', 'add_secrules_csv').strip()
        input_nsgs_csv = config.get('Default', 'nsgs_csv').strip()
        input_fss_csv = config.get('Default', 'fss_csv').strip()
        input_lbr_csv = config.get('Default', 'lbr_csv').strip()
        input_adw_atp_csv = config.get('Default', 'adw_atp_csv').strip()
        dbsystem_VM_csv_example_csv = config.get('Default', 'dbsystem_VM_csv').strip()
        dbsystem_BM_csv_example_csv = config.get('Default', 'dbsystem_BM_csv').strip()
        dbsystem_EXA_csv_example_csv = config.get('Default', 'dbsystem_EXA_csv').strip()
    except Exception as e:
        print(e)
        print('Check if input properties exist and try again..exiting...`    ')
        exit()

if (input_nongf_tenancy.lower() == 'true'):
    print("\nnon_gf_tenancy in properties files is set to true..Export existing OCI objects and Synch with TF state")
    print("Process will fetch objects from OCI in the specified compartment from all regions tenancy is subscribed to\n")
    print("1. Export Identity Objects(Compartments, Groups, Policies) to CD3 and create TF Files")
    print("2. Export Network Objects(VCNs, Subnets, Security Lists, Route Tables) to CD3 and create TF Files")
    print("3. Run bash script to import objects to TF state")
    print("q. Press q to quit")
    userInput = input('Enter your choice: multiple allowed ')

    if ("q" in userInput or "Q" in userInput):
        print("Exiting...")
        exit()

    ct = commonTools()
    ct.get_subscribedregions(input_config_file)

    print("\nChecking if specified outdir contains any existing tf files...")
    tf_list = {}
    for reg in ct.all_regions:
        tf_list[reg]=[]
        list = os.listdir(input_outdir + "/" + reg)
        for f in list:
            if f.endswith(".tf") and f!="provider.tf" and f!="variables_"+reg+".tf":
                tf_list[reg].append(f)
    found=0
    for reg in ct.all_regions:
        if (len(tf_list[reg]) != 0):
            if(len(tf_list[reg]) > 2):
                print(reg + " directory under outdir is not empty; contains below tf files " + str(tf_list[reg][0])+","+str(tf_list[reg][1])+" ...")
                found=1
            elif(len(tf_list[reg]) ==1):
                print(reg + " directory under outdir is not empty; contains below tf files " + str(tf_list[reg][0]))
                found = 1
    if(found==1):
        print("\nMake sure you have clean outdir(other than provider.tf and variables_<region>.tf) for fresh export.")
        print("Existing tf files should not be conflicting with new tf files that are going to be generated with this process.")
        proceed = input("Proceed y/n: ")
        if(proceed.lower()=='n'):
            print("Exiting...")
            exit()
    else:
        print("None Found. Proceeding to Export...")
    print("----------------------------------------------------------")
    if ("1" in userInput):
        if (input_config_file == ''):
            command = "python export_identity_nonGreenField.py " + input_cd3file + ' ' + input_outdir
        else:
            command = "python export_identity_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nIdentity Objects export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        print("----------------------------------------------------------")
        print("Fetching Compartment Info to variables files...\n")
        if (input_config_file == ''):
            command = "python fetch_compartments_to_variablesTF.py " + input_outdir
        else:
            command = "python fetch_compartments_to_variablesTF.py " + input_outdir + " --configFileName " + input_config_file

        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        print("----------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n-----------Process Compartments tab-----------")
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_compartments.py '+input_cd3file + ' ' + input_outdir+ ' '+input_prefix + ' --configFileName ' + input_config_file

        os.chdir('Identity/Compartments')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n-----------Process Groups tab-----------")
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_groups.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file

        os.chdir("../..")
        os.chdir('Identity/Groups')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n-----------Process Policies tab-----------")
        if (input_config_file == ''):
            command = 'python create_terraform_policies.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_policies.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file

        os.chdir("../..")
        os.chdir('Identity/Policies')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        os.chdir("../..")
        print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI objects; option No 3\n")

    if("2" in userInput):
        input_comp = input("Enter name of Compartment as it appears in OCI (comma seperated without spaces if multiple)for which you want to export network objects;\nLeave blank if want to export for all Compartments: ")

        if(input_comp==''):
            if (input_config_file == ''):
                command = "python export_network_nonGreenField.py "+input_cd3file + ' ' + input_outdir
            else:
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir +" --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_network_nonGreenField.py "+input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp +"\""
            else:
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp+"\""" --configFileName " + input_config_file
        print("\nExecuting command "+command)
        exitval =os.system(command)
        if (exitval==0):
            print("\nNetwork Objects export completed for CD3 excel "+ input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        print("----------------------------------------------------------")
        print("\nFetching Compartment Info to variables files...")
        if (input_config_file == ''):
            command = "python fetch_compartments_to_variablesTF.py " + input_outdir
        else:
            command = "python fetch_compartments_to_variablesTF.py " + input_outdir + " --configFileName " + input_config_file

        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        print("----------------------------------------------------------")
        print("\nProceeding to create TF files...\n")
        print("\n-----------Process VCNs tab-----------")
        if (input_config_file == ''):
            command = 'python create_all_tf_objects.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_all_tf_objects.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file

        os.chdir('CoreInfra/Networking/BaseNetwork')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n--------------Process DHCP tab------------")
        if (input_config_file == ''):
            command = 'python create_terraform_dhcp_options.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_dhcp_options.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n----------------Process Subnets tab for Subnets creation----------------")
        if (input_config_file == ''):
            command = 'python create_terraform_subnet.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_subnet.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n----------------Process SecRulesinOCI tab for SecList creation----------------")
        if (input_config_file == ''):
            command = 'python modify_secrules_tf.py ' + input_cd3file + ' ' + input_outdir + ' '+input_cd3file
        else:
            command = 'python modify_secrules_tf.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_cd3file + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitval=os.system(command)
        if (exitval == 1):
            exit()
        print("\n----------------Process RouteRulesinOCI tab for RouteRule creation----------------")
        if (input_config_file == ''):
            command = 'python modify_routerules_tf.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python modify_routerules_tf.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitval=os.system(command)
        if (exitval == 1):
            exit()
        print("\n\nExecute tf_import_commands_network_nonGF.sh script created under each region directory to synch TF with OCI objects; option No 3\n")

    if ("3" in userInput):
        print("\nterraform tfstate file should not be existing while doing fresh export/import!!\n")
        if ("linux" not in sys.platform):
            print("You are not using Linux system. Please proceed with manual execution of TF import cmds")
            print("scripts are in files: ")
            for reg in ct.all_regions:
                if (os.path.exists(input_outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")):
                    print(input_outdir+ "/" + reg+"/tf_import_commands_network_nonGF.sh")
                if (os.path.exists(input_outdir + "/" + reg + "/tf_import_commands_identity_nonGF.sh")):
                    print(input_outdir + "/" + reg + "/tf_import_commands_identity_nonGF.sh")
        else:
            for reg in ct.all_regions:
                os.chdir(input_outdir+ "/" + reg)
                if(os.path.exists(input_outdir+ "/" + reg + "/tf_import_commands_identity_nonGF.sh")):
                    print("Executing " + input_outdir + "/" + reg + "/tf_import_commands_identity_nonGF.sh")
                    os.system("chmod +x tf_import_commands_identity_nonGF.sh")
                    os.system("./tf_import_commands_identity_nonGF.sh")

                if (os.path.exists(input_outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")):
                    print("Executing " + input_outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")
                    os.system("chmod +x tf_import_commands_network_nonGF.sh")
                    os.system("./tf_import_commands_network_nonGF.sh")

    exit()

print("1.  Identity")
print("2.  Networking")
print("3.  Instances/Dedicated VM Hosts")
print("4.  Create and Attach Block Volumes")
print("5.  Tagging Resources")
print("6.  BackUp Policy")
print("7.  File Storage Service")
print("8.  Load Balancer Service")
print("9.  Create ADW/ATP")
print("10. Create Database")
print("q. Press q to quit")
print("\nSee example folder for sample input files\n")

userInput = input('Enter your choice: ')
userInput=userInput.split(',')

if('1' in userInput):
    print('-----------------------------Identity----------------------')
    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("1.  Add/Modify/Delete Compartments")
    print("2.  Add/Modify/Delete Groups")
    print("3.  Add/Modify/Delete Policies")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")
    choice = input("Enter your choice ")
    choice = choice.split(",")
    if ('1' in choice):
        print("--------------------------Processing Compartments Tab--------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_compartments_csv == ''):
                print("input compartments_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_compartments_csv

        os.chdir('Identity/Compartments')
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_compartments.py '+inputfile + ' ' + outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: "+command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    if('2' in choice):
        print("---------------------------Processing Groups Tab--------------------------------")
        if (input_format=='cd3'):
            inputfile=input_cd3file
        elif(input_format=='csv'):
            if (input_groups_csv == ''):
                print("input groups_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile=input_groups_csv
        outdir = input_outdir

        os.chdir('Identity/Groups')
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_groups.py '+inputfile + ' ' + outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    if('3' in choice):
        print("----------------------Processing Policies Tab----------------------------------")
        if (input_format=='cd3'):
            inputfile=input_cd3file

        os.chdir('Identity/Policies')
        if (input_config_file == ''):
            command = 'python create_terraform_policies.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_policies.py '+inputfile + ' ' +  outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    if("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py "+args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()
if('2' in userInput):
    print("---------------------Networking----------------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_vcninfo == ''):
            print("input vcn_info_file location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_vcninfo

    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    cd3validate = input("Do you want to verify CD3 Network Tabs? Enter y or n: ")
    if (cd3validate.lower() == 'y'):
        print("It will verify tabs: VCNs, DHCP and Subnets in excel sheet\n")
        if (input_config_file == ''):
            command = 'python cd3Validator.py ' + inputfile
            print("Executing Command: " + command)
            exitval = os.system(command)
        else:
            command = 'python cd3Validator.py ' + inputfile + ' --configFileName ' + input_config_file
            print("Executing Command: " + command)
            exitval = os.system(command)
        print("\n")
        if (exitval == 1 or exitval == 256):
            prcd_input = input("Do you still want to proceed with setUpOCI? Enter y or n: ")
            if (prcd_input.lower() == 'y'):
                pass
            else:
                print("Exiting...")
                exit()
    elif (cd3validate.lower() == 'n'):
        pass
    else:
        print("wrong input")
        exit()

    print("1.  Create Network- overwrites all TF files; reverts all SecLists and RouteTables to original rules")
    print("2.  Modify Network- Add/Remove/Modify any network object; updates TF files with changes; this option should be used after modifications have been done to SecRules or RouteRules")
    print("3.  Export existing SecRules and RouteRules to cd3")
    print("4.  Modify SecRules")
    print("5.  Modify RouteRules")
    print("6.  Add/Modify/Delete Network Security Groups")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    choice = input("Enter your choice ")
    choice = choice.split(",")

    if ('1' in choice):
        if (input_config_file == ''):
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if ('2' in choice):
        if (input_config_file == ''):
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --modify_network true'
        else:
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --configFileName ' + input_config_file + ' --modify_network true'
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if('3' in choice):
        print("---------------------------Exporting Rules--------------------------")
        if (input_format == 'cd3'):
            cd3outfile = input_cd3file
        inputConfigFile = input_config_file
        input_comp = input("Enter name of Compartment as it appears in OCI (comma seperated if multiple) for which you want to export rules; Leave blank if want to export for all Compartments: ")

        if (input_comp is ""):
            if (input_config_file == ''):
                command_sl = 'python exportSeclist.py ' + cd3outfile
                command_rt = 'python exportRoutetable.py ' + cd3outfile
            else:
                command_sl = 'python exportSeclist.py ' + cd3outfile + ' --configFileName ' + input_config_file
                command_rt = 'python exportRoutetable.py ' + cd3outfile+ ' --configFileName ' + input_config_file
        else:
            if (input_config_file == ''):
                command_sl = 'python exportSeclist.py ' + cd3outfile +" --networkCompartment \""+input_comp +"\""
                command_rt = 'python exportRoutetable.py ' + cd3outfile + " --networkCompartment \""+input_comp +"\""
            else:
                command_sl = 'python exportSeclist.py ' + cd3outfile + ' --configFileName ' + input_config_file + " --networkCompartment \""+input_comp +"\""
                command_rt = 'python exportRoutetable.py ' + cd3outfile +' --configFileName ' + input_config_file + " --networkCompartment \""+input_comp +"\""

        print("Executing Command: " + command_sl)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command_sl)
        print("-----------------------------------------------------------------------------")
        print("Executing Command: " + command_rt)
        os.system(command_rt)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if('4' in choice):
        print("------------------------Modifying Security Rules--------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
            inputcsv = inputfile
        elif (input_format == 'csv'):
            if (input_vcninfo == ''):
                print("input vcn_info_file location cannot be left blank. Exiting... ")
                exit(1)
            if (input_add_secrules_csv == ''):
                print("input add_secrules_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_vcninfo
            inputcsv = input_add_secrules_csv


        if (input_config_file == ''):
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv
        else:
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv + ' --configFileName ' + input_config_file

        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if('5' in choice):
        print("------------------------Modifying Route Rules--------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_add_routes_csv == ''):
                print("input add_routes_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_add_routes_csv

        if (input_config_file == ''):
            command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir
        else:
            command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir +' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if('6' in choice):
        print("---------------------Processing NSGs Tab----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_nsgs_csv == ''):
                print("input nsgs_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_nsgs_csv
        if (input_config_file == ''):
           command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir
        else:
            command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir +' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")
    if ("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()

if('3' in userInput):
    print("--------------------Instances/Dedicated VM Hosts------------------------------------")
    print("1.  Create Dedicated VM Hosts")
    print("2.  Create Instances")
    print("3.  Update existing instance to be part of NSG")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    choice = input("Enter your choice ")
    outdir = input_outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if (choice=='1'):
        os.chdir('CoreInfra/Compute')
        print("---------------------Processing DedicatedVMHosts Tab----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif(input_format=='csv'):
            if (input_dedicatedhosts_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile=input_dedicatedhosts_csv
        if (input_config_file == ''):
            command = 'python create_terraform_dedicatedhosts.py '+inputfile + ' ' + outdir
        else:
            command = 'python create_terraform_dedicatedhosts.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    elif (choice=='2'):
        os.chdir('CoreInfra/Compute')
        print("---------------------Processing Instances Tab----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv
        if (input_config_file == ''):
            command = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir
        else:
            command = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    elif (choice=='3'):
        os.chdir('CoreInfra/Compute')
        print("---------------------Processing Instances Tab----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv

        command = 'python update_instance_nsg.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    elif (choice == 'm' or choice=="M"):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    elif (choice == 'q' or choice=="Q"):
        print("Exiting...")
        exit()
    else:
        print("Invalid Choice")


if('4' in userInput):
    print("------------------------Creating BlockVolumes---------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_blocks_csv == ''):
            print("input blocks_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_blocks_csv
    outdir = input_outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/BlockVolume')
    if (input_config_file == ''):
        command = 'python create_terraform_block_volumes.py '+inputfile + ' ' + outdir
    else:
        command = 'python create_terraform_block_volumes.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")


if('5' in userInput):
    print("---------------------Creating Tags------------------------------")
    print("1.  Create Tags and Tag Namespaces")
    print("2.  Attach Tags to Servers")
    print("3.  Attach Tags to Block Volumes")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    tag_choice = input("Enter your choice ")
    tag_choice=tag_choice.split(",")
    if('1' in tag_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        outdir = input_outdir


        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        if (input_config_file == ''):
            command = 'python create_namespace_tagkey.py '+inputfile + ' ' + outdir
        else:
            command = 'python create_namespace_tagkey.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")

    if ('2' in tag_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_tag_servers_csv == ''):
                print("input tag_servers_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_tag_servers_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python attach_tag_server.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")


    if ('3' in tag_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_tag_volumes_csv == ''):
                print("input tag_volumes_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_tag_volumes_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python attach_tag_volume.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")

    print("--------------------------------------------------------------------------")
    if ("m" in tag_choice or "M" in tag_choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in tag_choice or "Q" in tag_choice):
        print("Exiting...")
        exit()

if('6' in userInput):
    print("------------------------Attaching Backup Policy---------------------------")

    outdir = input_outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("1. Attach BackupPolicy to Boot Volumes")
    print("2. Attach BackupPolicy to Block Volumes")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    backup_choice = input("Enter your choice ")
    backup_choice = backup_choice.split(",")
    if ('1' in backup_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv

        os.chdir('CoreInfra/Compute')
        if (input_config_file == ''):
            command = 'python boot_backups_policy.py '+inputfile + ' ' + outdir
        else:
            command = 'python boot_backups_policy.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    if ('2' in backup_choice):
        print("------------------------Attaching Backup Policy to Block Volumes---------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_blocks_csv == ''):
                print("input blocks_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_blocks_csv

        os.chdir('CoreInfra/BlockVolume')
        if (input_config_file == ''):
            command = 'python block_backups_policy.py '+inputfile + ' ' + outdir
        else:
            command = 'python block_backups_policy.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    if ("m" in backup_choice or "M" in backup_choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in backup_choice or "Q" in backup_choice):
        print("Exiting...")
        exit()

if('7' in userInput):
    print("------------------------Setting up FSS---------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_fss_csv == ''):
            print("input fss_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_fss_csv
    outdir = input_outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/FileStorage')
    if (input_config_file == ''):
        command = 'python create_terraform_fss.py '+inputfile + ' ' + outdir
    else:
        command = 'python create_terraform_fss.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('8' in userInput):
    print("------------------------Setting up LBR---------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_lbr_csv == ''):
            print("input lbr_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_lbr_csv
    outdir = input_outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Networking/LoadBalancers')
    if (input_config_file == ''):
        command = 'python create_terraform_lbr.py '+inputfile + ' ' + outdir
    else:
        command = 'python create_terraform_lbr.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file

    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('9' in userInput):
    print("------------------------Creating ADW/ATP---------------------------")
    if (input_format == 'cd3'):
        inputfile = input_cd3file
    elif (input_format == 'csv'):
        if (input_adw_atp_csv == ''):
            print("input adw_atp_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile = input_adw_atp_csv
    outdir = input_outdir
    prefix = input_prefix
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    os.chdir('Database')
    if (input_config_file == ''):
        command = 'python create_terraform_adw_atp.py ' + inputfile + ' ' + outdir + ' ' + prefix
    else:
        command = 'python create_terraform_adw_atp.py ' + inputfile + ' ' + outdir + ' ' + prefix  + ' --configFileName ' + input_config_file
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../")
    print("--------------------------------------------------------------------------")
if('10' in userInput):
    print("---------------------Create DB System----------------------------------")
    print("1.  Virtual Machine")
    print("2.  Bare Metal")
    print("3.  ExaData")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    update_choice = input("Enter your choice ")
    update_choice = update_choice.split(",")

    if ('1' in update_choice):
        print("---------------------------Create DB_System_VM--------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (dbsystem_VM_csv_example_csv == ''):
                print("input dbsystem_VM_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = dbsystem_VM_csv_example_csv
            # print(f"{inputfile}")
        outdir = input_outdir
        prefix = input_prefix
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir('Database')
        if (input_config_file == ''):
            command = 'python create_terraform_database_VM.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_database_VM.py ' + inputfile + ' ' + outdir + ' ' + prefix  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../")
        print("--------------------------------------------------------------------------")
    if ('2' in update_choice):
        print("---------------------------Create DB_System_BM--------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (dbsystem_BM_csv_example_csv == ''):
                print("input dbsystem_BM_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = dbsystem_BM_csv_example_csv
            # print(f"{inputfile}")
        outdir = input_outdir
        prefix = input_prefix
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir('Database')
        if (input_config_file == ''):
            command = 'python create_terraform_database_BM.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_database_BM.py ' + inputfile + ' ' + outdir + ' ' + prefix  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../")
        print("--------------------------------------------------------------------------")
    if ('3' in update_choice):
        print("---------------------------Create DB_System_EXA--------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (dbsystem_EXA_csv_example_csv == ''):
                print("input dbsystem_EXA_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = dbsystem_EXA_csv_example_csv
            # print(f"{inputfile}")
        outdir = input_outdir
        prefix = input_prefix
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir('Database')
        if (input_config_file == ''):
            command = 'python create_terraform_database_EXA.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_database_EXA.py ' + inputfile + ' ' + outdir + ' ' + prefix  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../")
        print("--------------------------------------------------------------------------")
    if ("m" in update_choice or "M" in update_choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in update_choice or "Q" in update_choice):
        print("Exiting...")
        exit()

if ("q" in userInput):
    print("Exiting...")
    exit()
