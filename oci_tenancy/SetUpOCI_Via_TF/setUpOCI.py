#!/usr/bin/python
import os

print("1.  Create Compartments")
print("2.  Create Groups")
print("3.  Create Policies")
print("4.  Create Base Network Objects")
print("5.  Create Instances")
print("6.  Create and Attach Block Volumes")
print("7.  Tagging Resources")
print("8.  Add Route Rules to existing Route Table")
print("9.  Add Security Rules to existing Security List")
print("10. Export Security List to CSV")

print("\nSee example folder for sample input files\n")
userInput = input('Enter your choice; multiple choices allowed as comma separated'
                  '\neg 1 if you want to create only Compartments; 1,2,3 if you want to create Compartments, Groups, Policies at one go ')

userInput=userInput.split(',')
inputfile=''
outdir=''
prefix=''

if('1' in userInput):
    print('-----------------------------Creating Compartments----------------------')
    if(inputfile==''  or '.xls' not in inputfile):
        inputfile = input("Enter full path to input CD3 excel file or csv file containing Compartments info: ")
    if(outdir==''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    if(prefix==''):
        prefix = input("Enter prefix for output files: ")
    outfile = outdir + "/" + prefix + '-compartments.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Compartments')
    command = 'python create_terraform_compartments.py '+inputfile + ' ' + outfile
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('2' in userInput):
    print("---------------------------Creating Groups--------------------------------")
    if(inputfile=='' or '.xls' not in inputfile):
        inputfile = input("Enter full path to input CD3 excel file or csv file containing Groups info: ")
    else:
        print("using already provided CD3 file: "+inputfile)
    if(outdir==''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    else:
        print("using already provided outdir: "+outdir)
    if(prefix==''):
        prefix = input("Enter prefix for output files: ")
    else:
        print("using already provided prefix: "+prefix)
    outfile = outdir + "/" + prefix + '-groups.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Groups')
    command = 'python create_terraform_groups.py '+inputfile + ' ' + outfile
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('3' in userInput):
    print("----------------------Creating Policies----------------------------------")
    if (inputfile == '' or '.xls' not in inputfile):
        inputfile = input("Enter full path to input CD3 excel file or csv file containing Policies info: ")
    else:
        print("using already provided CD3 file: " + inputfile)
    if (outdir == ''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    else:
        print("using already provided outdir: " + outdir)
    if (prefix == ''):
        prefix = input("Enter prefix for output files: ")
    else:
        print("using already provided prefix: " + prefix)
    outfile = outdir + "/" + prefix + '-policies.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('Identity/Policies')
    command = 'python create_terraform_policies.py '+inputfile + ' ' + outfile
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('4' in userInput):
    print("---------------------Creating Base Network----------------------------------")
    inputfile = input("Enter full path to properties file eg example\vcn-info.properties: ")
    if (outdir == ''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    else:
        print("using already provided outdir: " + outdir)
    if (prefix == ''):
        prefix = input("Enter prefix for output files: ")
    else:
        print("using already provided prefix: " + prefix)

    outfile = outdir + "/" + prefix + '-policies.tf'
    inputCD3 = input("Enter full path to CD3 excel file. Leave blank if don't want want to specify CD3 input..")

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Networking/BaseNetwork')
    if(inputCD3=='' or inputCD3 == ' '):
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix
    else:
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --inputCD3 ' +inputCD3
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('5' in userInput):
    print("--------------------Creating Instances------------------------------------")
    if (inputfile == ''  or '.xls' not in inputfile):
        inputfile = input("Enter full path to input CD3 excel file or csv file containing Instances info: ")
    else:
        print("using already provided CD3 file: " + inputfile)
    if (outdir == ''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    else:
        print("using already provided outdir: " + outdir)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/Compute')
    command = 'python create_terraform_instances.py '+inputfile + ' ' + outdir
    os.system(command)
    os.chdir("../..")
    print("--------------------------------------------------------------------------")

if('6' in userInput):
    print("------------------------Creating BlockVolumes---------------------------")
    if (inputfile == ''  or '.xls' not in inputfile):
        inputfile = input("Enter full path to input CD3 excel file or csv file containing Block Volumet info: ")
    else:
        print("using already provided CD3 file: " + inputfile)
    if (outdir == ''):
        outdir = input("Enter full path to output directory where you want to create terraform files: ")
    else:
        print("using already provided outdir: " + outdir)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('CoreInfra/BlockVolume')
    command = 'python create_terraform_block_volumes.py '+inputfile + ' ' + outdir
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
        inputfile = input("Enter full path to input CD3 excel file: ")
        if (outdir == ''):
            outdir = input("Enter full path to output directory where you want to create terraform files: ")
        else:
            print("using already provided outdir: " + outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python create_namespace_tagkey.py '+inputfile + ' ' + outdir
        os.system(command)
        os.chdir("../..")

    if ('2' in tag_choice):
        inputfile = input("Enter full path to input csv file containing tag information eg example\Tagging\tag_server-csv-example.csv: ")
        if (outdir == ''):
            outdir = input("Enter full path to output directory where you want to create terraform files: ")
        else:
            print("using already provided outdir: " + outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python attach_tag_server.py ' + inputfile + ' ' + outdir
        os.system(command)
        os.chdir("../..")


    if ('3' in tag_choice):
        inputfile = input("Enter full path to input csv file containing tag information eg example\Tagging\tag_volume-csv-example.csv: ")
        if (outdir == ''):
            outdir = input("Enter full path to output directory where you want to create terraform files: ")
        else:
            print("using already provided outdir: " + outdir)

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('Governance/Tagging')
        command = 'python attach_tag_volume.py ' + inputfile + ' ' + outdir
        os.system(command)
        os.chdir("../..")
    print("--------------------------------------------------------------------------")


if('8' in userInput):
    print("------------------------Adding Route Rules--------------------------------")
    inputfile = input("Enter full path to input csv file containing route rules info eg example/BaseNetwork/add_routes-example.csv: ")
    outfile = input("Enter full path to routes terraform file created earlier while setting up Base Network Objects: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')
    command = 'python add_routerules_to_tf.py ' + inputfile + ' ' + outfile
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")


if('9' in userInput):
    print("------------------------Adding Security Rules--------------------------------")
    inputfile = input("Enter full path to either properties file eg example/vcn-info.properties or CD3 excel file: ")
    inputcsv = input("Enter full path to input csv file containing security rules info eg example/BaseNetwork/update_seclist-example.csv: ")
    outdir = input("Enter full path to output directory used while setting up Base Network Objects: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')
    command = 'python update_seclist_to_tf.py --inputfile ' + inputfile + ' --outdir ' + outdir + ' --secrulesfile '+inputcsv
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")

if('10' in userInput):
    print("---------------------------Exporting Security Rules--------------------------")
    inputComp = input("Enter Compartment Name of VCN for which you want to export Security Lists: ")
    outdir = input("Enter full path to output directory where csv will be generated: ")
    inputConfigFile = input("Enter path to pyhton config file This is required when you are executing the code from some other workstation rather than OCS VM"
                            " else leave it empty: ")

    os.chdir('CoreInfra/Networking/BaseNetwork')
    if(inputConfigFile==''):
        command = 'python exportSeclistToCSV.py ' + inputComp + ' ' + outdir
    else:
        command = 'python exportSeclistToCSV.py ' + inputComp + ' ' + outdir + ' --configFileName '+inputConfigFile
    os.system(command)
    os.chdir("../../..")
    print("--------------------------------------------------------------------------")
