### To clone the repo
* Open your terminal and change the directory to the one where you want to download the git repo.
* Run the git clone command as shown below:<br/>
&nbsp; &nbsp; &nbsp; &nbsp; git clone https://github.com/oracle-devrel/cd3-automation-toolkit
* Once the cloning command completes successfully, the repo will replicate to the local directory. 

### To build an image

* Change directory to cd3-automation-toolkit(i.e. the cloned repo in your local).
* Run <i>"docker build --platform linux/amd64 -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache ."</i><br/>
<br  /><b>Note</b> : ${image_tag} should be replaced with suitable tag as per your requirements/standards.
<br  />&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;The period at the end of the docker build command is required.

### To save the image (Optional)
* Run  <i>"docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz"</i>


### To run the CD3 container and exec into it
* Run  <i>"docker run --platform linux/amd64 -it -d -v <directory_in_local_system_where_the_files_must_be_generated>:/cd3user/tenancies <image_name>:<image_tag>"</i>
* Run  <i>"docker ps"</i>
* Run  <i>"docker exec -it <container_id> bash"</i>
  
  
 