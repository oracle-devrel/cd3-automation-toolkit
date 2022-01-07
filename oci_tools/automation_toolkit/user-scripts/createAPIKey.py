#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initilizing the docker container; creates pem keys.
#
# Author: Suruchi Single
# Modified by: Shruthi Subramanian
#
import os
from Cryptodome.PublicKey import RSA

def create_keys():

    # Creation of PEM Keys -
    print("Creating Public/Private API PEM Key at /root/ocswork/tenancies/keys/.......")

    keys_dir = "/root/ocswork/tenancies/keys/"
    key = RSA.generate(2048)
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)

    f = open(keys_dir+"/oci_api_private.pem", "wb")
    f.write(key.exportKey('PEM'))
    f.close()

    pubkey = key.publickey()
    f = open(keys_dir+"/oci_api_public.pem", "wb")
    f.write(pubkey.exportKey('PEM'))
    f.close()

    os.chdir(keys_dir)
    command = "chmod 400 /root/ocswork/tenancies/keys/oci_api_private.pem"
    os.system(command)

    print("=================================================================")
    print("NOTE: Make sure to add the API Public Key to the OCI Console!!!")
    print("=================================================================")

if __name__ == '__main__':
    create_keys()
