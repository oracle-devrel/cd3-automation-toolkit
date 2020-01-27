import argparse
import configparser
import os

parser = argparse.ArgumentParser(description="Sets Up OCI via TF")
parser.add_argument("propsfile",help="Full Path of properties file containing input variables. eg setUpOCI.properties")

args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

#Read Config file Variables
try:
    input_format=config.get('Default','input').strip()
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

#Set Default Value as cd3
if(input_format==''):
    input_format='cd3'

if(input_format=='cd3'):
    try:
        input_cd3file=config.get('Default','cd3file').strip()
        if(input_cd3file==''):
            print("input cd3file location cannot be left blank. Exiting... ")
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

print("1.  Identity")
print("2.  Networking")
print("3.  Instances/Dedicated VM Hosts")
print("4.  Create and Attach Block Volumes")
print("5.  Tagging Resources")
print("6.  BackUp Policy")
print("7.  File Storage Service")
print("8.  Load Balancer Service")
print("9.  Create ADW/ADT")
print("10. Create Database")
print("\nSee example folder for sample input files\n")

userInput = input('Enter your choice; multiple choices allowed as comma separated: ')
userInput=userInput.split(',')

if('1' in userInput):
    print('-----------------------------Identity----------------------')
    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("1.  Create Compartments")
    print("2.  Create Groups")
    print("3.  Create Policies")
    choice = input("Enter your choice; multiple choices allowed as comma separated ")
    choice = choice.split(",")
    if ('1' in choice):
        print("---------------------------Creating Compartments--------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_compartments_csv == ''):
                print("input compartments_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_compartments_csv

        os.chdir('Identity/Compartments')
        command = 'python create_terraform_compartments.py '+inputfile + ' ' + outdir+ ' '+prefix
        print("Executing Command: "+command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    if('2' in choice):
        print("---------------------------Creating Groups--------------------------------")
        if (input_format=='cd3'):
            inputfile=input_cd3file
        elif(input_format=='csv'):
            if (input_groups_csv == ''):
                print("input groups_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile=input_groups_csv
        outdir = input_outdir

        os.chdir('Identity/Groups')
        command = 'python create_terraform_groups.py '+inputfile + ' ' + outdir+ ' '+prefix
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    if('3' in choice):
        print("----------------------Creating Policies----------------------------------")
        if (input_format=='cd3'):
            inputfile=input_cd3file

        os.chdir('Identity/Policies')
        command = 'python create_terraform_policies.py '+inputfile + ' ' +  outdir+ ' '+prefix
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

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
    os.chdir('CoreInfra/Networking/BaseNetwork')

    print("1.  Create Network- overwrites all TF files; reverts all SecLists and RouteTables to original rules")
    print("2.  Modify Network- Add/Remove/Modify any network object; updates TF files with changes; this option should be used after modifications have been done to SecRules or RouteRules")
    print("3.  Export SecRules and RouteRules to cd3")
    print("4.  Modify SecRules")
    print("5.  Modify RouteRules")
    print("6.  Create Network Security Groups")
    choice = input("Enter one choice ")

    if (choice=='1'):
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    elif (choice=='2'):
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --modify_network true'
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    elif(choice == '3'):
        print("---------------------------Exporting Rules--------------------------")
        if (input_format == 'cd3'):
            cd3outfile = input_cd3file
        inputConfigFile = input_config_file
        input_vcn = input("Enter name of VCN for which you want to export security rules and route rules; Leave blank if want to export for all VCNs: ")
        if (input_vcn != ''):
            input_Comp = input("Enter Compartment Name where this VCN resides: ")

        if (input_vcn == ''):
            if (inputConfigFile == ''):
                command_sl = 'python exportSeclist.py ' + cd3outfile
                command_rt = 'python exportRoutetable.py ' + cd3outfile
            else:
                command_sl = 'python exportSeclist.py ' + cd3outfile + ' --configFileName ' + inputConfigFile
                command_rt = 'python exportRoutetable.py ' + cd3outfile + ' --configFileName ' + inputConfigFile
        else:
            if (inputConfigFile == ''):
                command_sl = 'python exportSeclist.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp
                command_rt = 'python exportRoutetable.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp
            else:
                command_sl = 'python exportSeclist.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp + ' --configFileName ' + inputConfigFile
                command_rt = 'python exportRoutetable.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp + ' --configFileName ' + inputConfigFile

        print("Executing Command: " + command_sl)
        os.system(command_sl)
        print("-----------------------------------------------------------------------------")
        print("Executing Command: " + command_rt)
        os.system(command_rt)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    elif(choice == '4'):
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


#        if (inputConfigFile == ''):
        command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv
 #       else:
 #           command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv + ' --configFileName ' + inputConfigFile
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    elif(choice == '5'):
        print("------------------------Modifying Route Rules--------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_add_routes_csv == ''):
                print("input add_routes_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_add_routes_csv


        command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    elif(choice=='6'):
        print("---------------------Creating NSGs----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_nsgs_csv == ''):
                print("input nsgs_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_nsgs_csv

        command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")
    else:
        print("Invalid Choice")
if('3' in userInput):
    print("--------------------Creating Instances/Dedicated VM Hosts------------------------------------")
    print("1.  Create Dedicated VM Hosts")
    print("2.  Create Instances")
    print("3.  Update existing instance to be part of NSG")

    choice = input("Enter one choice ")
    outdir = input_outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Compute')

    if (choice=='1'):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif(input_format=='csv'):
            if (input_dedicatedhosts_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile=input_dedicatedhosts_csv

        command = 'python create_terraform_dedicatedhosts.py '+inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    elif (choice=='2'):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv

        command = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

    elif (choice=='3'):
        print("---------------------Updating Instances to have NSG----------------------------------")
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
    command = 'python create_terraform_block_volumes.py '+inputfile + ' ' + outdir
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")


if('5' in userInput):
    print("---------------------Creating Tags------------------------------")
    print("1.  Create Tags and Tag Namespaces")
    print("2.  Attach Tags to Servers")
    print("3.  Attach Tags to Block Volumes")

    tag_choice = input("Enter your choice; multiple choices allowed as comma separated ")
    tag_choice=tag_choice.split(",")
    if('1' in tag_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        outdir = input_outdir


        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python create_namespace_tagkey.py '+inputfile + ' ' + outdir
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

if('6' in userInput):
    print("------------------------Attaching Backup Policy---------------------------")

    outdir = input_outdir
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    print("1. Attach BackupPolicy to Boot Volumes")
    print("2. Attach BackupPolicy to Block Volumes")
    backup_choice = input("Enter your choice; multiple choices allowed as comma separated ")
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
        command = 'python boot_backups_policy.py '+inputfile + ' ' + outdir
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
        command = 'python block_backups_policy.py '+inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

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
    command = 'python create_terraform_fss.py '+inputfile + ' ' + outdir
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
    command = 'python create_terraform_lbr.py '+inputfile + ' ' + outdir
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
    command = 'python create_terraform_adw_atp.py ' + inputfile + ' ' + outdir + ' ' + prefix
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../")
    print("--------------------------------------------------------------------------")
if('10' in userInput):
    print("---------------------Create DB System----------------------------------")
    print("1.  Virtual Machine")
    print("2.  Bare Metal")
    print("3.  ExaData")

    update_choice = input("Enter your choice; multiple choices allowed as comma separated ")
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
        command = 'python create_terraform_database_VM.py ' + inputfile + ' ' + outdir + ' ' + prefix
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
        command = 'python create_terraform_database_BM.py ' + inputfile + ' ' + outdir + ' ' + prefix
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
        command = 'python create_terraform_database_EXA.py ' + inputfile + ' ' + outdir + ' ' + prefix
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../")
        print("--------------------------------------------------------------------------")