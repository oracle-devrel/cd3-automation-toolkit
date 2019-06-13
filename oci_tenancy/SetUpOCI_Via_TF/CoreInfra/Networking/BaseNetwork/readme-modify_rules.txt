modify_routes_tf.py and modify_secrules_tf.py are the scripts to modify route rules and security rules respectively to OCI.

These scripts work in 2 modes: Add or Overwrite

If you want to just add the rules to existing route table or security list then dont ue overwrite flag. It will read either the input csv containing
new rules or the cd3 (sheets: AddRouteRules and AddSecRules) and generate terraform to add these rules in OCI without checking what is existing in the OCI.

Instead if you want to run in Overwrite mode then that means all rules in OCI would be replced by whatever you hae in cd3 excel file
(sheets: RouteRulesinOCI and SecRulesinOCI)

modify_routes_tf.py
--------------------
This script takes in either a csv file or CD3 excel file mentioning new route rules to be added as the input. See add_routes-example.csv under example folder.
Note- This would only add new rules to the route table. It wont check for existing rules.
Usage:

./modify_routes_tf.py <path to input csv containing rules> <path to routes tf file created earlier using create_all_tf_objects.py>
eg
./modify_routes_tf.py add-routes.csv routes.tf

Overwrite Mode:
./modify_routes_tf.py add-routes.csv routes.tf --overwrite true


modify_secrules_tf.py
------------------------------
This script takes in either a csv file or CD3 excel file mentioning new sec rules to be added as the input. See update_seclist-example.csv under example folder.


Usage:
./modify_secrules_tf.py --inputfile <path to vcn-info.properties or CD3 excel file> --outdir <output dir name being used for tf files> --secrulesfile <path to input csv containing rules>
eg
./modify_secrules_tf.py --inputfile vcn-info.properties --outdir /root/ocswork/terraform_files --secrulesfile update_seclist-adrules.csv
or
./modify_secrules_tf.py --inputfile CD3-template --outdir /root/ocswork/terraform_files --secrulesfile update_seclist-adrules.csv

Overwrite Mode:
./modify_secrules_tf.py --inputfile CD3-template --outdir /root/ocswork/terraform_files --overwrite true
