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

print("\nSee example folder for sample input files")
userInput = input('Enter your choice: ')

if(userInput == '1'):
    inputfile = input("Enter full path to input CD3 excel file or csv file containing Compartments info: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    prefix = input("Enter prefix for output files: ")
    outfile = outdir + "/" + prefix + '-compartments.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../Identity/Compartments')
    command = 'python create_terraform_compartments.py '+inputfile + ' ' + outfile
    os.system(command)

elif(userInput == '2'):
    inputfile = input("Enter full path to input CD3 excel file or csv file containing Groups info: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    prefix = input("Enter prefix for output files: ")
    outfile = outdir + "/" + prefix + '-groups.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../Identity/Groups')
    command = 'python create_terraform_groups.py '+inputfile + ' ' + outfile
    os.system(command)

elif(userInput == '3'):
    inputfile = input("Enter full path to input CD3 excel file: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    prefix = input("Enter prefix for output files: ")
    outfile = outdir + "/" + prefix + '-policies.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../Identity/Groups')
    command = 'python create_terraform_policies.py '+inputfile + ' ' + outfile
    os.system(command)


elif(userInput == '4'):
    inputfile = input("Enter full path to properties file eg example\vcn-info.properties: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    prefix = input("Enter prefix for output files: ")
    inputCD3 = input("Enter full path to CD3 excel file. Leave blank if don't want wnt to specify CD3 input..")

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../CoreInfra/Networking/BaseNetwork')
    if(inputCD3=='' or inputCD3 == ' '):
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix
    else:
        command = 'python create_all_tf_objects.py ' + inputfile + ' ' + outdir + ' ' + prefix + ' --inputCD3 ' +inputCD3
    os.system(command)

elif(userInput == '5'):
    inputfile = input("Enter full path to input CD3 excel file or csv file containing Instances info: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    #prefix = input("Enter prefix for output files: ")
    #outfile = outdir + "/" + prefix + '-compartments.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../CoreInfra/Compute')
    command = 'python create_terraform_instances.py '+inputfile + ' ' + outdir
    os.system(command)

elif(userInput == '6'):
    inputfile = input("Enter full path to input CD3 excel file or csv file containing Block Volumes info: ")
    outdir = input("Enter full path to output directory where you want to create terraform files: ")
    #prefix = input("Enter prefix for output files: ")
    #outfile = outdir + "/" + prefix + '-compartments.tf'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    os.chdir('../CoreInfra/BlockVolume')
    command = 'python create_terraform_block_volumes.py '+inputfile + ' ' + outdir
    os.system(command)

elif(userInput == '7'):
    print("1.  Create Tags and Tag Namespaces")
    print("2.  Attach Tags to Servers")
    print("3.  Attach Tags to Block Volumes")

    tag_choice = input("Enter your choice ")
    if(tag_choice=='1'):
        inputfile = input("Enter full path to input CD3 excel file: ")
        outdir = input("Enter full path to output directory where you `want to create terraform files: ")

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('../Governance/Tagging')
        command = 'python create_namespace_tagkey.py '+inputfile + ' ' + outdir
        os.system(command)

    elif (tag_choice == '2'):
        inputfile = input("Enter full path to input csv file containing tag information eg example\Tagging\tag_server-csv-example.csv: ")
        outdir = input("Enter full path to output directory where you `want to create terraform files: ")

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('../Governance/Tagging')
        command = 'python attach_tag_server.py ' + inputfile + ' ' + outdir
        os.system(command)

    elif (tag_choice == '3'):
        inputfile = input("Enter full path to input csv file containing tag information eg example\Tagging\tag_volume-csv-example.csv: ")
        outdir = input("Enter full path to output directory where you `want to create terraform files: ")

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        os.chdir('../Governance/Tagging')
        command = 'python attach_tag_volume.py ' + inputfile + ' ' + outdir
        os.system(command)

elif(userInput == '8'):
    inputfile = input("Enter full path to input csv file containing route rules info eg example/BaseNetwork/add_routes-example.csv: ")
    outfile = input("Enter full path to routes terraform file created earlier while setting up Base Network Objects: ")

    os.chdir('../CoreInfra/Networking/BaseNetwork')
    command = 'python add_routerules_to_tf.py ' + inputfile + ' ' + outfile
    os.system(command)

elif(userInput == '9'):
    inputfile = input("Enter full path to either properties file eg example/vcn-info.properties or CD3 excel file: ")
    inputcsv = input("Enter full path to input csv file containing security rules info eg example/BaseNetwork/update_seclist-example.csv: ")
    outdir = input("Enter full path to output directory created while setting up Base Network Objects: ")

    os.chdir('../CoreInfra/Networking/BaseNetwork')
    command = 'python update_seclist_to_tf.py --inputfile ' + inputfile + ' --outdir ' + outdir + ' --secrulesfile '+inputcsv
    os.system(command)

elif(userInput == '10'):
    inputComp = input("Enter Compartment Name of Networking Components: ")
    outdir = input("Enter full path to output directory: ")

    os.chdir('../CoreInfra/Networking/BaseNetwork')
    command = 'python exportSeclistToCSV.py ' + inputComp + ' ' + outdir
    os.system(command)

else:
    print("Wrong Input. Please try again..")