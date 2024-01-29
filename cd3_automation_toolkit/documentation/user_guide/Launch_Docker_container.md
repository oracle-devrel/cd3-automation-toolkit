# Launch the Container
To ease the execution of toolkit, we have provided the steps to build an image which encloses the code base and its package dependencies. Follow the steps provided below  to clone the repo, build the image and finally launch the container.
<br>

## Clone the repo
* Open your terminal and navigate to the directory where you plan to download the Git repo.
* Run the git clone command as shown below:<br/>
&nbsp; &nbsp; &nbsp; &nbsp; ```git clone https://github.com/oracle-devrel/cd3-automation-toolkit```
* Once the cloning command is executed successfully, the repo will replicate to the local directory. 

## Build an image

* Change directory to 'cd3-automation-toolkit'(i.e. the cloned repo in your local).
* Run ```docker build --platform linux/amd64 -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache .```<br/>
<br  /><b>Note</b> : ${image_tag} should be replaced with suitable tag as per your requirements/standards. eg v2024.1.0
<br  />&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;The period (.) at the end of the docker build command is required.

## Save the image (Optional)
* Run  ```docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz```

## Run the container alongwith VPN (Applicable for VPN users only)
* Connect to the VPN.
* Make sure you are using version **1.9** for **Rancher deskop**, if not please install the latest.
* Make sure to Enable **Networking Tunnel** under Rancher settings as shown in the screenshot below,
  
     <img width="746" alt="image" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103548537/22e71261-63dc-4218-a3f6-9ef98df820e2">
     
* Login to the CD3 docker container using next section and set the proxies(if any) which helps to connect internet from the container.

## Run the container
* Run  ```docker run --platform linux/amd64 -it -p <port_number_in_local_system>:8443 -d -v <directory_in_local_system_where_the_files_must_be_generated>:/cd3user/tenancies <image_name>:<image_tag>```
  
  Eg for Mac: ```docker run --platform linux/amd64 -it -p 8443:8443 -d -v /Users/mount_path:/cd3user/tenancies cd3toolkit:v2024.1.0```

  Eg for Windows: ```docker run --platform linux/amd64 -it -p 8443:8443 -d -v D:/mount_path:/cd3user/tenancies cd3toolkit:v2024.1.0```
> <b>Note:</b>  Mac users need to make sure to create mount directory only under /Users folder to avoid any permission issues.

* Run  ```docker ps```

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/prerequisites.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
