#!/usr/bin/python3
import os
import configparser
import argparse

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

    except Exception as e:
        print(e)
        print('Check if input properties exist and try again..exiting...`    ')
        exit()


print("1.  Create Compartments")
print("2.  Create Groups")
print("3.  Create Policies")
print("4.  Create Base Network Objects")
print("5.  Create Instances/Dedicated VM Hosts")
print("6.  Create and Attach Block Volumes")
print("7.  Tagging Resources")
print("8.  Modify Route Rules in existing Route Table")
print("9.  Modify Security Rules in existing Security List")
print("10. Attach Back up policy to Boot Volumes")
print("11. Attach Back up policy to Block Volumes")
print("12. Export Security Lists to CD3")
print("13. Export Route Tables to CD3")
print("14. Update Base Network Objects; Use this option only if you have already made changes/updates "
      "to the configurations after initial Base Network Creation.\n    Else you should use Option 4 again with required changes to CD3 - It will overwrite all network objects.")
print("15. Network Security Groups")
print("16. File Storage Services")
print("\nSee example folder for sample input files\n")
userInput = input('Enter your choice; multiple choices allowed as comma separated: ')
userInput=userInput.split(',')

if('1' in userInput):
    print('-----------------------------Creating Compartments----------------------')
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_compartments_csv == ''):
            print("input compartments_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_compartments_csv
    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Compartments')
    command = 'python create_terraform_compartments.py '+inputfile + ' ' + outdir+ ' '+prefix
    print("Executing Command: "+command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('2' in userInput):
    print("---------------------------Creating Groups--------------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_groups_csv == ''):
            print("input groups_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_groups_csv
    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Groups')
    command = 'python create_terraform_groups.py '+inputfile + ' ' + outdir+ ' '+prefix
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('3' in userInput):
    print("----------------------Creating Policies----------------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    outdir = input_outdir
    prefix = input_prefix

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Policies')
    command = 'python create_terraform_policies.py '+inputfile + ' ' +  outdir+ ' '+prefix
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('4' in userInput):
    print("---------------------Creating Base Network----------------------------------")
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
    command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('5' in userInput):
    print("--------------------Creating Instances/Dedicated VM Hosts------------------------------------")
    print("1.  Create Dedicated VM Hosts")
    print("2.  Create Instances")

    choice = input("Enter your choice; multiple choices allowed as comma separated ")
    choice = choice.split(",")
    if ('1' in choice):
        if (input_format=='cd3'):
            inputfile=input_cd3file
        elif(input_format=='csv'):
            if (input_dedicatedhosts_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile=input_dedicatedhosts_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('CoreInfra/Compute')
        command = 'python create_terraform_dedicatedhosts.py '+inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")
    if ('2' in choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('CoreInfra/Compute')
        command = 'python create_terraform_instances.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

if('6' in userInput):
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


if('7' in userInput):
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


if('8' in userInput):
    print("------------------------Adding Route Rules--------------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
    elif(input_format=='csv'):
        if (input_add_routes_csv == ''):
            print("input add_routes_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_add_routes_csv
    outdir = input_outdir
    overwrite = input("Do you want to overwrite rules in OCI or add more rules to existing ones. Enter yes for overwrite or no for addition: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')
    if(overwrite=='' or overwrite=='no'):
        command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir
    if(overwrite=='yes'):
        command = 'python modify_routerules_tf.py ' + inputfile + ' ' + outdir + ' --overwrite yes'
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")


if('9' in userInput):
    print("------------------------Adding Security Rules--------------------------------")
    if (input_format=='cd3'):
        inputfile=input_cd3file
        inputcsv=inputfile
    elif(input_format=='csv'):
        if (input_vcninfo == ''):
            print("input vcn_info_file location cannot be left blank. Exiting... ")
            exit(1)
        if (input_add_secrules_csv == ''):
            print("input add_secrules_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile=input_vcninfo
        inputcsv=input_add_secrules_csv

    outdir = input_outdir
    inputConfigFile = input_config_file
    overwrite = input("Do you want to overwrite rules in OCI or add more rules to existing ones. Enter yes for overwrite or no for addition: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')

    if (overwrite == '' or overwrite == 'no'):
        if(inputConfigFile==''):
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' '+inputcsv
        else:
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' '+inputcsv+' --configFileName '+inputConfigFile
    if(overwrite=='yes'):
        if (inputConfigFile == ''):
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv + ' --overwrite yes'
        else:
            command = 'python modify_secrules_tf.py ' + inputfile + ' ' + outdir + ' ' + inputcsv + ' --configFileName ' + inputConfigFile +' --overwrite yes'
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('10' in userInput):
    print("------------------------Attaching Backup Policy to Boot Volumes---------------------------")
    if (input_format == 'cd3'):
        inputfile = input_cd3file
    elif (input_format == 'csv'):
        if (input_instances_csv == ''):
            print("input instances_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile = input_instances_csv
    outdir = input_outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Compute')
    command = 'python boot_backups_policy.py '+inputfile + ' ' + outdir
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('11' in userInput):
    print("------------------------Attaching Backup Policy to Block Volumes---------------------------")
    if (input_format == 'cd3'):
        inputfile = input_cd3file
    elif (input_format == 'csv'):
        if (input_blocks_csv == ''):
            print("input blocks_csv location cannot be left blank. Exiting... ")
            exit(1)
        inputfile = input_blocks_csv
    outdir = input_outdir

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/BlockVolume')
    print("Executing Command: " + command)
    command = 'python block_backups_policy.py '+inputfile + ' ' + outdir
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('12' in userInput):
    print("---------------------------Exporting Security Rules--------------------------")
    if (input_format == 'cd3'):
        cd3outfile = input_cd3file
    inputConfigFile = input_config_file
    input_vcn = input("Enter name of VCN for which you want to export security rules; Leave blank if want to export for all VCNs: ")
    if (input_vcn != ''):
        input_Comp = input("Enter Compartment Name where this VCN resides: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')

    if (input_vcn == ''):
        if (inputConfigFile == ''):
            command = 'python exportSeclist.py ' + cd3outfile
        else:
            command = 'python exportSeclist.py ' + cd3outfile + ' --configFileName ' + inputConfigFile
    else:
        if (inputConfigFile == ''):
            command = 'python exportSeclist.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp
        else:
            command = 'python exportSeclist.py ' + cd3outfile + ' --vcnName ' + input_vcn + ' --networkCompartment ' + input_Comp + ' --configFileName ' + inputConfigFile

    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('13' in userInput):
    print("---------------------------Exporting Route Rules--------------------------")
    if (input_format == 'cd3'):
        cd3outfile = input_cd3file
    inputConfigFile = input_config_file

    input_vcn=input("Enter name of VCN for which you want to export route rules; Leave blank if want to export for all VCNs: ")
    if(input_vcn!=''):
        input_Comp = input("Enter Compartment Name where this VCN resides: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')
    if(input_vcn==''):
        if(inputConfigFile==''):
            command = 'python exportRoutetable.py ' +  cd3outfile
        else:
            command = 'python exportRoutetable.py ' + cd3outfile + ' --configFileName '+inputConfigFile
    else:
        if (inputConfigFile == ''):
            command = 'python exportRoutetable.py '+cd3outfile+' --vcnName '+input_vcn + ' --networkCompartment '+input_Comp
        else:
            command = 'python exportRoutetable.py '+cd3outfile+' --vcnName '+input_vcn + ' --networkCompartment '+input_Comp+ ' --configFileName ' + inputConfigFile
    print("Executing Command: " + command)
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('14' in userInput):
    print("---------------------Updating Base Network----------------------------------")
    print("1.  Add new DHCP Option; Move existing DHCP options to below <END> tag in cd3")
    print("2.  Add New Subnet; Move existing subnets to below <END> tag in cd3")

    update_choice = input("Enter your choice; multiple choices allowed as comma separated ")
    update_choice = update_choice.split(",")

    if ('1' in update_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        outdir = input_outdir
        prefix = input_prefix

        if not os.path.exists(outdir):
            print("out dir doesnot exist; please enter a valid directory")
            exit(1)

        os.chdir('CoreInfra/Networking/BaseNetwork')
        command = 'python update_terraform_network.py ' + inputfile + ' ' + outdir + ' ' + prefix +' 1'
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if ('2' in update_choice):
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        outdir = input_outdir
        prefix = input_prefix

        if not os.path.exists(outdir):
            print("out dir doesnot exist; please enter a valid directory")
            exit(1)

        os.chdir('CoreInfra/Networking/BaseNetwork')
        command = 'python update_terraform_network.py ' + inputfile + ' ' + outdir + ' ' + prefix +' 2'
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

if('15' in userInput):
    print("---------------------Setting up Network Security Groups----------------------------------")
    print("1.  Create NSGs")
    print("2.  Update existing instance to be part of NSG")
    print("Note: Use option 5(Create Instances) to create new instance and make part of NSG after creation of NSGs")

    update_choice = input("\nEnter your choice; multiple choices allowed as comma separated ")
    update_choice = update_choice.split(",")

    if ('1' in update_choice):
        print("---------------------Creating NSGs----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_nsgs_csv == ''):
                print("input nsgs_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_nsgs_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            print("out dir doesnot exist; please enter a valid directory")
            exit(1)

        os.chdir('CoreInfra/Networking/BaseNetwork')
        command = 'python create_terraform_nsg.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../../..")
        print("--------------------------------------------------------------------------")

    if ('2' in update_choice):
        print("---------------------Updating Instances to have NSG----------------------------------")
        if (input_format == 'cd3'):
            inputfile = input_cd3file
        elif (input_format == 'csv'):
            if (input_instances_csv == ''):
                print("input instances_csv location cannot be left blank. Exiting... ")
                exit(1)
            inputfile = input_instances_csv
        outdir = input_outdir

        if not os.path.exists(outdir):
            print("out dir doesnot exist; please enter a valid directory")
            exit(1)

        os.chdir('CoreInfra/Compute')
        command = 'python update_instance_nsg.py ' + inputfile + ' ' + outdir
        print("Executing Command: " + command)
        os.system(command)
        os.chdir("../..")
        print("--------------------------------------------------------------------------")

if('16' in userInput):
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

