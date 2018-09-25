#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage: create_oci_keys.sh <clientname> <user>"
    echo "Usage: user should only be name - no special characters"
    echo "This script will create the OCI RSA keys to be uploaded in the directory ./keys"
    echo "Files created: "
    echo "    oci_<clientname>_<username>_pvt_key.pem"
    echo "    oci_<clientname>_<username>_pub_key.pem"
    echo "    oci_<clientname>_<username>_fprint.txt"
    echo "Docs found at: https://docs.us-phoenix-1.oraclecloud.com/Content/API/Concepts/apisigningkey.htm#five"
    exit -1
fi

CLIENTNAME=$1
USERNAME=$2

DIR="./keys/"
PVT_KEYNAME="$DIR"oci_"$CLIENTNAME"_"$USERNAME"_pvt_key.pem
PUB_KEYNAME="$DIR"oci_"$CLIENTNAME"_"$USERNAME"_pub_key.pem
FPRINT_NAME="$DIR"oci_"$CLIENTNAME"_"$USERNAME"_fprint.txt

echo "$PVT_KEYNAME"
mkdir ./keys



if [ ! -f $PVT_KEYNAME ]; then
	echo "Creating $PVT_KEYNAME"
	openssl genrsa -out $PVT_KEYNAME 2048
else
	echo "$PVT_KEYNAME exists"
	echo "Exiting"
	exit -1
fi
if [ ! -f $PUB_KEYNAME ]; then
	echo "Creating $PUB_KEYNAME"
	openssl rsa -pubout -in $PVT_KEYNAME -out $PUB_KEYNAME
else
	echo "$PUB_KEYNAME exists - will be overwritten using new private key"
	openssl rsa -pubout -in $PVT_KEYNAME -out $PUB_KEYNAME
fi
if [ ! -f $FPRINT_NAME ]; then
	echo "Creating $FPRINT_NAME"
	openssl rsa -pubout -outform DER -in $PVT_KEYNAME  | openssl md5 -c > $FPRINT_NAME
	chmod go-rwx $PVT_KEYNAME
else
	echo "$FPRINT_NAME exists - will be overwritten using newly created Pub key"
	openssl rsa -pubout -outform DER -in $PVT_KEYNAME  | openssl md5 -c > $FPRINT_NAME
	chmod go-rwx $PVT_KEYNAME
fi

