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
    input_nongf_tenancy = config.get('Default', 'non_gf_tenancy').strip()

    input_outdir = config.get('Default', 'outdir').strip()
    outdir = input_outdir
    if(input_outdir==''):
        print("input outdir location cannot be left blank. Exiting... ")
        exit(1)

    input_prefix = config.get('Default', 'prefix').strip()
    prefix = input_prefix
    if(input_prefix==''):
        print("input prefix value cannot be left blank. Exiting... ")
        exit(1)

    input_config_file=config.get('Default', 'config_file').strip()

    input_cd3file=config.get('Default','cd3file').strip()
    inputfile=input_cd3file
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

inputs = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
if (input_nongf_tenancy.lower() == 'true'):
    print("\nnon_gf_tenancy in properties files is set to true..Export existing OCI objects and Synch with TF state")
    print("Process will fetch objects from OCI in the specified compartment from all regions tenancy is subscribed to\n")
    print("1. Export Identity Objects(Compartments, Groups, Policies) to CD3 and create TF Files")
    print("2. Export Network Objects(VCNs, Subnets, Security Lists, Route Tables, NSGs) to CD3 and create TF Files")
    print("3. Export Instance Objects to CD3 and create TF Files")
    print("4. Export Block Volumes to CD3 and create TF Files")
    print("5. Export Tag Objects(TagnameSpaces, Tag Keys, Tag Defaults, Tag Values) to CD3 and create TF Files")
    print("6. Export FSS Objects to CD3 and create TF Files")
    print("7. Export LBR Objects to CD3 and create TF Files")
    '''
    print("8. Export ADW/ATP")
    print("9. Export Database")
    '''
    print("8. Export Solutions(Events and Notifications) Objects to CD3 and create TF Files")
    print("q. Press q to quit")
    userInput = input('Enter your choice (you can specify comma separated multiple choices eg 1,2): ')

    userInput=userInput.split(",")
    if ("q" in userInput or "Q" in userInput):
        print("Exiting...")
        exit()
    if (not set(userInput).issubset(set(inputs))):
        if ("m" in userInput or "M" in userInput):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()

    ct = commonTools()
    ct.get_subscribedregions(input_config_file)

    print("\nChecking if the specified outdir contains tf files related to the OCI components being exported...")
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
        print("\nMake sure you have clean tfstate file and outdir(other than provider.tf and variables_<region>.tf) for fresh export.")
        print("Existing tf files should not be conflicting with new tf files that are going to be generated with this process.")
        proceed = input("Proceed y/n: ")
        if(proceed.lower()!='y'):
            print("Exiting...")
            exit()
    else:
        print("None Found. Proceeding to Export...")
    print("-----------------------------------------------------------------------------------------------------------------")
    print("\nFetching Compartment Info to variables files...")
    if (input_config_file == ''):
        command = "python fetch_compartments_to_variablesTF.py " + input_outdir
    else:
        command = "python fetch_compartments_to_variablesTF.py " + input_outdir + " --configFileName " + input_config_file

    print("Executing Command: " + command)
    exitVal = os.system(command)
    if (exitVal == 1) or (exitVal == 256):
        print("Error Occured. Please try again!!!")
        exit()
    if ("1" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Identity...")
        os.chdir('ExportFromOCI')
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
        os.chdir("..")
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n---------------------------------Process Compartments tab------------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_compartments.py '+input_cd3file + ' ' + input_outdir+ ' '+input_prefix + ' --configFileName ' + input_config_file

        os.chdir('Identity/Compartments')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        print("\n---------------------------------Process Groups tab-------------------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_groups.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_groups.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file

        os.chdir("../..")
        os.chdir('Identity/Groups')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n----------------------------------Process Policies tab----------------------------------------------------------")
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
        print("\n\nExecute tf_import_commands_identity_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")
    if ("2" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Network...")

        os.chdir('ExportFromOCI')
        input_comp = input(
            "Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export network objects;\nPress 'Enter' to export from all the Compartments: ")
        if (input_comp == ''):
            if (input_config_file == ''):
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""
            else:
                command = "python export_network_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""" --configFileName " + input_config_file
        print("\nExecuting command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nNetwork Objects export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nProceeding to create TF files...\n")
        print("\n--------------------------------------Process VCNs tab---------------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_major_objects.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_major_objects.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file

        os.chdir('CoreInfra/Networking/BaseNetwork')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n--------------------------------------Process DHCP tab---------------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_dhcp_options.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_dhcp_options.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n--------------------------------------Process Subnets tab for Subnets creation--------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_subnet.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_subnet.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        print("\n--------------------------------------Process SecRulesinOCI tab for SecList creation----------------------------")
        if (input_config_file == ''):
            command = 'python modify_secrules_tf.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_cd3file
        else:
            command = 'python modify_secrules_tf.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_cd3file + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitval = os.system(command)
        if (exitval == 1):
            exit()
        print("\n--------------------------------------Process RouteRulesinOCI tab for RouteRule creation------------------------")
        if (input_config_file == ''):
            command = 'python modify_routerules_tf.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python modify_routerules_tf.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitval = os.system(command)
        if (exitval == 1):
            exit()

        print("\n--------------------------------------Process NSGs tab----------------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_nsg.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python create_terraform_nsg.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        os.chdir("../../..")
        if ("linux" in sys.platform):
            dir = os.getcwd()
            for reg in ct.all_regions:
                os.chdir(input_outdir + "/" + reg)
                if (os.path.exists(input_outdir + "/" + reg + "/tf_import_commands_network_nonGF.sh")):
                    os.system("chmod +x tf_import_commands_network_nonGF.sh")
            os.chdir(dir)

        print("\n\nExecute tf_import_commands_network_nonGF.sh script created under each region directory to synch TF with OCI Network objects\n")

    if ("3" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Instances...")
        os.chdir('ExportFromOCI')
        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export Instances;\nPress 'Enter' to export from all the Compartments:")
        if(input_comp==''):
            if (input_config_file == ''):
                command = "python export_instance_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_instance_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_instance_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""
            else:
                command = "python export_instance_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""" --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nInstance export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n--------------------------------------Process Instances tab----------------------------------------------------")
        if (input_config_file == ''):
            command1 = 'python create_terraform_instances.py ' + input_cd3file + ' ' + input_outdir
            command2 = 'python boot_backups_policy.py ' + inputfile + ' ' + outdir

        else:
            command1 = 'python create_terraform_instances.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command2 = 'python boot_backups_policy.py ' + inputfile + ' ' + outdir + ' --configFileName ' + input_config_file
        os.chdir('CoreInfra/Compute')
        print("Executing Command: " + command1)
        exitVal = os.system(command1)
        if (exitVal == 1):
            exit()
        print("\nExecuting Command: " + command2)
        exitVal = os.system(command2)
        if (exitVal == 1):
            exit()

        os.chdir("../..")
        print("\n\nExecute tf_import_commands_instances_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")

    if ("4" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Block Volumes...")
        os.chdir('ExportFromOCI')
        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export Block Volumes;\nPress 'Enter' to export from all the Compartments: ")
        if(input_comp==''):
            if (input_config_file == ''):
                command = "python export_blockvol_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_blockvol_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_blockvol_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""
            else:
                command = "python export_blockvol_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""" --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nBlock Volume export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n-----------------------------------Process BlockVols tab-------------------------------------------------------")
        if (input_config_file == ''):
            command1 = 'python create_terraform_block_volumes.py ' + input_cd3file + ' ' + input_outdir
            command2 = 'python block_backups_policy.py ' + inputfile + ' ' + outdir
        else:
            command1 = 'python create_terraform_block_volumes.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command2 = 'python block_backups_policy.py ' + inputfile + ' ' + outdir + ' --configFileName ' + input_config_file

        os.chdir('CoreInfra/BlockVolume')
        print("Executing Command: " + command1)
        exitVal = os.system(command1)
        if (exitVal == 1):
            exit()
        print("\nExecuting Command: " + command2)
        exitVal = os.system(command2)
        if (exitVal == 1):
            exit()


        os.chdir("../..")
        print("\n\nExecute tf_import_commands_blockvols_nonGF.sh script created under each region directory to synch TF with OCI Instances\n")


    if ("5" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Tags...")
        os.chdir('ExportFromOCI')
        if (input_config_file == ''):
            command = "python export_tags_nonGreenField.py " + input_cd3file + ' ' + input_outdir
        else:
            command = "python export_tags_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file

        print("Executing Command: " + command)
        exitVal = os.system(command)
        if(exitVal == 1):
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nProceeding to create TF files...\n")
        print("\n--------------------------------------------Process Tags tab---------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_namespace_tagkey.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python create_namespace_tagkey.py ' + input_cd3file + ' ' + input_outdir  + ' --configFileName ' + input_config_file

        os.chdir('Governance/Tagging')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        os.chdir("../..")
        print("\n\nExecute tf_import_commands_tags_nonGF.sh script created under home region directory to synch TF with OCI Identity objects\n")


    if ("6" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting FSS...")
        os.chdir('ExportFromOCI')
        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export FSS objects;\nPress 'Enter' to export from all the Compartments: ")
        if (input_comp == ''):
            if (input_config_file == ''):
                command = "python export_fss_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_fss_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_fss_nonGreenField.py "+input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp +"\""
            else:
                command = "python export_fss_nonGreenField.py " + input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp+"\""" --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nFSS export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n-----------------------------------------------Process FSS tab-------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_fss.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python create_terraform_fss.py '+input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file

        os.chdir('CoreInfra/FileStorage')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()

        os.chdir("../..")
        print("\n\nExecute tf_import_commands_fss_nonGF.sh script created under each region directory to synch TF with OCI FSS objects\n")


    if ("7" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting LBR...")

        os.chdir('ExportFromOCI')
        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export LBR objects;\nPress 'Enter' to export from all the Compartments: ")
        if (input_comp == ''):
            if (input_config_file == ''):
                command = "python export_lbr_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_lbr_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_lbr_nonGreenField.py "+input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp +"\""
            else:
                command = "python export_lbr_nonGreenField.py " + input_cd3file + ' ' + input_outdir +" --networkCompartment \""+input_comp+"\""" --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nLBR export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n---------------------------------------------Process Load Balancer tabs----------------------------------------")
        os.chdir('CoreInfra/Networking/LoadBalancers')
        if (input_config_file == ''):
            command = 'python create_terraform_lbr_hostname_certs.py ' + input_cd3file + ' ' + input_outdir
            command2 = 'python create_backendset_backendservers.py ' + input_cd3file + ' ' + input_outdir
            command3 = 'python create_listener.py ' + input_cd3file + ' ' + input_outdir
            command4 = 'python create_path_route_set.py ' + input_cd3file + ' ' + input_outdir
            command5 = 'python create_ruleset.py ' + input_cd3file + ' ' + input_outdir
        else:
            command = 'python create_terraform_lbr_hostname_certs.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command2 = 'python create_backendset_backendservers.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command3 = 'python create_listener.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command4 = 'python create_path_route_set.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
            command5 = 'python create_ruleset.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        print("\n---------------------------------------------Creating LB and Certificates----------------------------------------")
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        print("\n---------------------------------------------Creating Backend Sets and Backend Servers---------------------------")
        print("Executing Command: " + command2)
        exitVal = os.system(command2)
        if (exitVal == 1):
            exit()
        print("\n---------------------------------------------Creating Listeners--------------------------------------------------")
        print("Executing Command: " + command3)
        exitVal = os.system(command3)
        if (exitVal == 1):
            exit()
        print("\n---------------------------------------------Creating Path Route Sets--------------------------------------------")
        print("Executing Command: " + command4)
        exitVal = os.system(command4)
        if (exitVal == 1):
            exit()
        print("\n---------------------------------------------Creating RuleSets---------------------------------------------------")
        print("Executing Command: " + command5)
        exitVal = os.system(command5)
        os.chdir("../..")
        if (exitVal == 1):
            exit()
        os.chdir("../../..")
        print("\n\nExecute tf_import_commands_lbr_nonGF.sh script created under each region directory to synch TF with OCI LBR objects\n")
    '''
    if ("8" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting ADW/ATP...")
        print("Yet to be Implemented")
        exit()
    if ("9" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Database...")
        print("Yet to be Implemented")
        exit()
    '''
    if ("8" in userInput):
        print("-----------------------------------------------------------------------------------------------------------------")
        print("\nExporting Events and Notifications...")
        try:
            os.chdir('ExportFromOCI')
        except FileNotFoundError as e:
            os.chdir('oci_tenancy/SetUpOCI_Via_TF/ExportFromOCI')

        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated without spaces if multiple)for which you want to export Events and Notifications objects;\nPress 'Enter' to export from all the Compartments: ")
        if (input_comp == ''):
            if (input_config_file == ''):
                command = "python export_solutions_nonGreenField.py " + input_cd3file + ' ' + input_outdir
            else:
                command = "python export_solutions_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --configFileName " + input_config_file
        else:
            if (input_config_file == ''):
                command = "python export_solutions_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""
            else:
                command = "python export_solutions_nonGreenField.py " + input_cd3file + ' ' + input_outdir + " --networkCompartment \"" + input_comp + "\""" --configFileName " + input_config_file

        print("Executing command " + command)
        exitval = os.system(command)
        if (exitval == 0):
            print("\nSolutions export completed for CD3 excel " + input_cd3file)
        else:
            print("\nError Occured. Please try again!!!")
            exit()
        os.chdir('..')
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Proceeding to create TF files...\n")
        print("\n-----------------------------------------Process Events tab----------------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_events.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_events.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        os.chdir('Solutions/EventsAndNotifications')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        print("\n-----------------------------------------Process Notifications tab---------------------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_notifications.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_notifications.py ' + input_cd3file + ' ' + input_outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        os.chdir("../..")
        os.chdir('Solutions/EventsAndNotifications')
        print("Executing Command: " + command)
        exitVal = os.system(command)
        if (exitVal == 1):
            exit()
        os.chdir("../..")

        if ("linux" in sys.platform):
            dir = os.getcwd()
            for reg in ct.all_regions:
                os.chdir(input_outdir + "/" + reg)
                if (os.path.exists(input_outdir + "/" + reg + "/tf_import_solutions_lbr_nonGF.sh")):
                    os.system("chmod +x tf_import_commands_solutions_nonGF.sh")
            os.chdir(dir)

        print("\n\nExecute tf_import_commands_solutions_nonGF.sh script created under each region directory to synch TF with OCI Events and Notifications objects\n")

    exit()

inputs = ["1","2","3","4","5","6","7","8","9","10","11"]
print("1.  Identity")
print("2.  Networking")
print("3.  Dedicated VM Hosts/Instances/Boot Backup Policy")
print("4.  Create and Attach Block Volumes/Block BackUp Policy")
print("5.  Tags")
print("6.  File Storage Service")
print("7.  Load Balancer Service")
print("8.  ADW/ATP")
print("9.  Database")
print("10. Solutions (Events and Notifications)")
print("11. Upload current terraform files/state to Resource Manager")
print("q.  Press q to quit")
print("\nSee example folder for sample input files\n")

userInput = input('Enter your choice: ')
userInput=userInput.split(',')

if('1' in userInput):
    print('-------------------------------------------------------Identity------------------------------------------------------')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    Ideninputs =["1","2","3","m","q"]
    print("1.  Add/Modify/Delete Compartments")
    print("2.  Add/Modify/Delete Groups")
    print("3.  Add/Modify/Delete Policies")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")
    choice = input("Enter your choice ")
    choice = choice.split(",")

    if ('1' in choice):
        print("------------------------------------------Processing Compartments Tab-----------------------------------------------")
        os.chdir('Identity/Compartments')
        if (input_config_file == ''):
            command = 'python create_terraform_compartments.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_compartments.py '+inputfile + ' ' + outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: "+command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------------------------------------------------")

    if('2' in choice):
        print("------------------------------------------Processing Groups Tab-----------------------------------------------------")
        os.chdir('Identity/Groups')
        if (input_config_file == ''):
            command = 'python create_terraform_groups.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_groups.py '+inputfile + ' ' + outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("---------------------------------------------------------------------------------------------------------------------")

    if('3' in choice):
        print("------------------------------------------Processing Policies Tab----------------------------------------------------")
        os.chdir('Identity/Policies')
        if (input_config_file == ''):
            command = 'python create_terraform_policies.py ' + inputfile + ' ' + outdir + ' ' + prefix
        else:
            command = 'python create_terraform_policies.py '+inputfile + ' ' +  outdir+ ' '+prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("---------------------------------------------------------------------------------------------------------------------")

    if("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py "+args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()
    if (not set(choice).issubset(set(Ideninputs))):
        if ("m" in choice or "M" in choice):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()

if('2' in userInput):
    print("---------------------------------------------------Networking--------------------------------------------------------")
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
        print("\nInvalid Input !! Please enter 'y' or 'n'... Exiting!!")
        exit()

    netinputs = ["1", "2", "3", "4", "5", "6"]
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
        print("-------------------------------------------------------------------------------------------------------------")

    if ('2' in choice):
        if (input_config_file == ''):
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --modify_network true'
        else:
            command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --configFileName ' + input_config_file + ' --modify_network true'
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("---------------------------------------------------------------------------------------------------------------")

    if('3' in choice):
        print("-----------------------------------------Exporting Rules-------------------------------------------------------")
        cd3outfile = input_cd3file
        inputConfigFile = input_config_file
        input_comp = input("Enter name of Compartment as it appears in OCI (comma separated if multiple) for which you want to export rules;\nPress 'Enter' to export from all the Compartments: ")

        if (input_comp == ""):
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
        print("-----------------------------------------------------------------------------------------------------------------")
        print("Executing Command: " + command_rt)
        os.system(command_rt)
        os.chdir("../../..")
        print("-----------------------------------------------------------------------------------------------------------------")

    if('4' in choice):
        print("---------------------------------------------Modifying Security Rules--------------------------------------------")
        inputcsv =inputfile
        if (input_config_file == ''):
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv
        else:
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv + ' --configFileName ' + input_config_file

        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("-----------------------------------------------------------------------------------------------------------------")

    if('5' in choice):
        print("---------------------------------------------Modifying Route Rules-----------------------------------------------")
        if (input_config_file == ''):
            command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir
        else:
            command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir +' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("-----------------------------------------------------------------------------------------------------------------")

    if('6' in choice):
        print("---------------------------------------------Processing NSGs Tab-------------------------------------------------")
        if (input_config_file == ''):
           command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir
        else:
            command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir +' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.chdir('CoreInfra/Networking/BaseNetwork')
        os.system(command)
        os.chdir("../../..")
        print("-----------------------------------------------------------------------------------------------------------------")
    if ("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()
    if (not set(choice).issubset(set(netinputs))):
        if ("m" in choice or "M" in choice):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()
if('3' in userInput):
    instinputs = ["1","2"]
    print("-------------------------------------------------Instances/Dedicated VM Hosts----------------------------------------")
    print("1.  Add/Modify/Delete Dedicated VM Hosts")
    print("2.  Add/Modify/Delete Instances/Boot Backup Policy")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    choice = input("Enter your choice ")
    choice = choice.split(",")

    outdir = input_outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if ("1" in choice):
        os.chdir('CoreInfra/Compute')
        print("-----------------------------------------------Processing DedicatedVMHosts Tab-----------------------------------")
        if (input_config_file == ''):
            command = 'python create_terraform_dedicatedhosts.py '+inputfile + ' ' + outdir
        else:
            command = 'python create_terraform_dedicatedhosts.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("-----------------------------------------------------------------------------------------------------------------")
    if ("2" in choice):
        os.chdir('CoreInfra/Compute')
        print("-----------------------------------------------Processing Instances Tab------------------------------------------")
        if (input_config_file == ''):
            command1 = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir
            command2 = 'python boot_backups_policy.py ' + inputfile + ' ' + outdir
        else:
            command1 = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
            command2 = 'python boot_backups_policy.py ' + inputfile + ' ' + outdir + ' --configFileName ' + input_config_file
        print("Executing Command: " + command1)
        exitVal = os.system(command1)
        if (exitVal == 1):
            exit()
        print("\nExecuting Command: " + command2)
        exitVal = os.system(command2)
        if (exitVal == 1):
            exit()
        os.chdir("../..")
        print("------------------------------------------------------------------------------------------------------------------")

    if ("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()
    if (not set(choice).issubset(set(instinputs))):
        if ("m" in choice or "M" in choice):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()

if('4' in userInput):
    print("--------------------------------------------------Processing BlockVolumes Tab-------------------------------------")
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/BlockVolume')
    if (input_config_file == ''):
        command1 = 'python create_terraform_block_volumes.py '+inputfile + ' ' + outdir
        command2 = 'python block_backups_policy.py ' + inputfile + ' ' + outdir
    else:
        command1 = 'python create_terraform_block_volumes.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
        command2 = 'python block_backups_policy.py ' + inputfile + ' ' + outdir + ' --configFileName ' + input_config_file
    print("Executing Command: " + command1)
    exitVal = os.system(command1)
    if (exitVal == 1):
        exit()
    print("\nExecuting Command: " + command2)
    exitVal = os.system(command2)
    if (exitVal == 1):
        exit()
    os.chdir("../..")
    print("------------------------------------------------------------------------------------------------------------------------")

if('5' in userInput):
    print("--------------------------------------------------Processing Tags Tab---------------------------------------------------")
    os.chdir('Governance/Tagging')
    if (input_config_file == ''):
        command = 'python create_namespace_tagkey.py '+inputfile + ' ' + outdir
    else:
        command = 'python create_namespace_tagkey.py ' + inputfile + ' ' + outdir  + ' --configFileName ' + input_config_file
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")

if('6' in userInput):
    print("--------------------------------------------------Processing FSS Tab-----------------------------------------------------")
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
    print("------------------------------------------------------------------------------------------------------------------------")

if('7' in userInput):
    print("-------------------------------------------------Setting up LBR---------------------------------------------------------")
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Networking/LoadBalancers')

    if (input_config_file == ''):
        command = 'python create_terraform_lbr_hostname_certs.py ' + input_cd3file + ' ' + input_outdir
        command2 = 'python create_backendset_backendservers.py ' + input_cd3file + ' ' + input_outdir
        command3 = 'python create_listener.py ' + input_cd3file + ' ' + input_outdir
        command4 = 'python create_path_route_set.py ' + input_cd3file + ' ' + input_outdir
        command5 = 'python create_ruleset.py ' + input_cd3file + ' ' + input_outdir
    else:
        command = 'python create_terraform_lbr_hostname_certs.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        command2 = 'python create_backendset_backendservers.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        command3 = 'python create_listener.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        command4 = 'python create_path_route_set.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
        command5 = 'python create_ruleset.py ' + input_cd3file + ' ' + input_outdir + ' --configFileName ' + input_config_file
    print("\n-----------------------------------------------Creating LBR-------------------------------------------------------------")
    print("Executing Command: " + command)
    exitVal = os.system(command)
    if (exitVal == 1):
        exit()
    print("\n---------------------------------------Creating Backend Sets and Backend Servers----------------------------------------")
    print("Executing Command: " + command2)
    exitVal = os.system(command2)
    if (exitVal == 1):
        exit()
    print("\n------------------------------------------------Creating Listeners-------------------------------------------------------")
    print("Executing Command: " + command3)
    exitVal = os.system(command3)
    if (exitVal == 1):
        exit()
    print("\n-------------------------------------------Creating Path Route Sets------------------------------------------------------")
    print("Executing Command: " + command4)
    exitVal = os.system(command4)
    if (exitVal == 1):
        exit()
    print("\n----------------------------------------------Creating RuleSets----------------------------------------------------------")
    print("Executing Command: " + command5)
    exitVal = os.system(command5)
    if (exitVal == 1):
        exit()

    os.chdir("../../..")
    print("------------------------------------------------------------------------------------------------------------------------")

if('8' in userInput):
    print("----------------------------------------------Processing ADW/ATP Tab----------------------------------------------------")
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
    print("-----------------------------------------------------------------------------------------------------------------------")
if('9' in userInput):
    dbinputs = ["1","2","3"]
    print("------------------------------------------------Databases-------------------------------------------------------------")
    print("1.  Add/Modify/Delete Virtual Machine")
    print("2.  Add/Modify/Delete Bare Metal")
    print("3.  Add/Modify/Delete ExaData")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    update_choice = input("Enter your choice ")
    update_choice = update_choice.split(",")

    if ('1' in update_choice):
        print("----------------------------------------Processing DB_System_VM Tab-----------------------------------------------")
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
        print("------------------------------------------------------------------------------------------------------------------")
    if ('2' in update_choice):
        print("----------------------------------------Processing DB_System_BM Tab-----------------------------------------------")
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
        print("---------------------------------------------------------------------------------------------------------------------")
    if ('3' in update_choice):
        print("----------------------------------------Processing DB_System_EXA Tab-------------------------------------------------")
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
        print("----------------------------------------------------------------------------------------------------------------------")
    if ("m" in update_choice or "M" in update_choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in update_choice or "Q" in update_choice):
        print("Exiting...")
        exit()
    if (not set(update_choice).issubset(set(dbinputs))):
        if ("m"  in update_choice or "M"  in update_choice):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()

if('10' in userInput):
    print("----------------------------------------------Events and Notifications---------------------------------------------------")
    eninputs = ["1", "2"]
    print("1.  Add/Modify/Delete Notifications")
    print("2.  Add/Modify/Delete Events")
    print("m.  Press m to go back to Main Menu")
    print("q.  Press q to quit")

    choice = input("Enter your choice ")
    choice = choice.split(",")

    if ('1' in choice):
        print("-----------------------------------------Setting up Notifications-----------------------------------------------------")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir('Solutions/EventsAndNotifications')
        if (input_config_file == ''):
            command = 'python create_terraform_notifications.py ' + inputfile + ' ' + outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_notifications.py ' + inputfile + ' ' + outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("-----------------------------------------------------------------------------------------------------------------------")

    if ('2' in choice):
        print("-------------------------------------------Setting up Events-----------------------------------------------------------")
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        os.chdir('Solutions/EventsAndNotifications')
        if (input_config_file == ''):
            command = 'python create_terraform_events.py ' + inputfile + ' ' + outdir + ' ' + input_prefix
        else:
            command = 'python create_terraform_events.py ' + inputfile + ' ' + outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("------------------------------------------------------------------------------------------------------------------------")

    if ("m" in choice or "M" in choice):
        cmd = "python setUpOCI.py " + args.propsfile
        print("Going back to Main Menu...")
        os.system(cmd)
    if ("q" in choice or "Q" in choice):
        print("Exiting...")
        exit()
    if (not set(choice).issubset(set(eninputs))):
        if ("m"  in choice or "M"  in choice):
            pass
        else:
            print("\nInvalid Choice..Exiting...")
            exit()

if('11' in userInput):
    print('\n-------------------------------------------------------Resource Manager------------------------------------------------------')
    os.chdir('ResourceManager')
    if (input_config_file == ''):
        command = 'python create_resource_manager_stack.py '+ outdir + ' ' + input_prefix # + ' ' + apply_flag + ' ' + rm_ocid
    else:
        command =  'python create_resource_manager_stack.py '+ outdir + ' ' + input_prefix + ' --configFileName ' + input_config_file #+ ' ' + apply_flag + ' ' + rm_ocid
    print("Executing Command: " + command)
    exitVal = os.system(command)
    if (exitVal == 1):
        exit()
    os.chdir("../..")
    print("-----------------------------------------------------------------------------------------------------------------------")

if ("q" in userInput or "Q" in userInput):
    print("Exiting...")
    exit()

if (not set(userInput).issubset(set(inputs))):
    print("\nInvalid Choice..Exiting...")
    exit()


