add_routes_to_tf.py and update_seclist_to_tf_v2.0.py are the scripts to add new route rules and security rules respectively to OCI.

add_routes_to_tf.py
--------------------
This script takes in a csv file mentioning route rules as the input. See add_routes-example.txt under example folder.
Usage:

./add_routes_to_tf.py <path to input csv containing rules> <path to routes tf file created earlier using create_all_tf_objects.py>
eg
./add_routes_to_tf.py add-routes.csv routes.tf


update_seclist_to_tf_v2.0.py
------------------------------
This script takes in a csv file mentioning sec rules as the input. See update_seclist-example.csv under example folder.
Usage:
./update_seclist_to_tf_v2.0.py --inputfile <path to vcn-info.properties or CD3 excel file> --outdir <output dir name being used for tf files> --secrulesfile <path to input csv containing rules>
eg
./update_seclist_to_tf_v2.0.py --inputfile vcn-info.properties --outdir /root/ocswork/terraform_files --secrulesfile update_seclist-adrules.csv
or
./update_seclist_to_tf_v2.0.py --inputfile CD3-template.properties --outdir /root/ocswork/terraform_files --secrulesfile update_seclist-adrules.csv