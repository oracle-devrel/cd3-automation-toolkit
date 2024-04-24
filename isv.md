<h2>Export from one Tenancy and  Create the same infra in another tenancy </h2>

Set Up the CD3 containers and connect them to Source Tenancy and Target tenancy using steps mentioned in https://oracle-devrel.github.io/cd3-automation-toolkit/install-cd3/

<h3> Identity Components </h3>
1. Export Identity Components(Compartments, Groups, Policies, Users, Network Sources)eibcccujfghnjilldhuucfgnruccnifeghrlbkvvjdec from source tenancy. 
2. There is no need to execute shell script containing the terraform import commands.
3. Use the exported excel. Make appropriate changes to Identity tabs (Compartments, Groups, Policies, Users, Network Sources) like region name as per the new tenancy.
4. Create IAM resources using this excel sheet in the new tenancy.

<h3> Network Components </h3>
1. Chose to export all Network Compnents (Option - 'Export all Network Components' under 'Network')
2. It will export the data into excel template networking tabs and also 
