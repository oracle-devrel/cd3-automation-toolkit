import jenkins.model.Jenkins
import com.cloudbees.hudson.plugins.folder.*


Jenkins jenkins = Jenkins.instance
def JENKINS_HOME = System.getenv("JENKINS_HOME")
File file = new File("$JENKINS_HOME/jenkins.properties")
file.withReader { reader ->
     while ((line = reader.readLine()) != null) {
          if (line.startsWith('git_url')) {
            git_url = Eval.me(line.split("=")[1])
        }
          if (line.startsWith('regions')) {
            regions = Eval.me(line.split("=")[1])
        }
          if (line.startsWith('outdir_structure')) {
            outdir_structure = Eval.me(line.split("=")[1])
        }
          if (line.startsWith('services')) {
            services = Eval.me(line.split("=")[1])
        }
      }
 }

def tfApplyJobName = "terraform-apply"
def tfDestroyJobName = "terraform-destroy"

// Function to create job XML
def createJobXml(scriptPath, gitUrl) {
    return """
    <flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
            <scriptPath>${scriptPath}</scriptPath>
            <lightweight>false</lightweight>
            <scm class="hudson.plugins.git.GitSCM">
                <userRemoteConfigs>
                    <hudson.plugins.git.UserRemoteConfig>
                        <url>${gitUrl}</url>
                    </hudson.plugins.git.UserRemoteConfig>
                </userRemoteConfigs>
                <branches>
                    <hudson.plugins.git.BranchSpec>
                        <name>develop</name>
                    </hudson.plugins.git.BranchSpec>
                </branches>
                <configVersion>2</configVersion>
                <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                <gitTool>Default</gitTool>
            </scm>
        </definition>
    </flow-definition>
    """
}

// Function to create Jenkins job
def createJob(parent, jobName, xml) {
    def jobXmlStream = new ByteArrayInputStream(xml.getBytes())
    parent.createProjectFromXML(jobName, jobXmlStream)
}

// Create jobs for each configuration
jenkins.with {
    Folder ost = getItem("terraform_files") ?: createProject(Folder.class, "terraform_files")

    for (os in outdir_structure) {
        Folder global = ost.getItem("global") ?: ost.createProject(Folder.class, "global")
        Folder rpc = global.getItem("rpc") ?: global.createProject(Folder.class, "rpc")

        createJob(rpc, tfApplyJobName, createJobXml('tf-apply.groovy', git_url))
        createJob(rpc, tfDestroyJobName, createJobXml('tf-destroy.groovy', git_url))
        for (reg in regions) {
        Folder folder = ost.getItem(reg) ?: ost.createProject(Folder.class, reg)

        if (os == "Single_Outdir") {
            createJob(folder, tfApplyJobName, createJobXml('tf-apply.groovy', git_url))
            createJob(folder, tfDestroyJobName, createJobXml('tf-destroy.groovy', git_url))
        }

        if (os == "Multiple_Outdir" && services) {
            for (svc in services) {
                Folder svcFolder = folder.getItem(svc) ?: folder.createProject(Folder.class, svc)
                createJob(svcFolder, tfApplyJobName, createJobXml('tf-apply.groovy', git_url))
                createJob(svcFolder, tfDestroyJobName, createJobXml('tf-destroy.groovy', git_url))
            }
        }
    }
}
}
