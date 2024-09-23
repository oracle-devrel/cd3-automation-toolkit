import jenkins.model.Jenkins
import hudson.model.Cause
import com.cloudbees.hudson.plugins.folder.*

def parseProperties(fileContent) {
    def result = [:]
    def currentSection = null

    fileContent.eachLine { line ->
        line = line.trim()

        if (line.startsWith("#") || line.isEmpty()) {
            // Ignore comments and empty lines
            return
        }

        def sectionMatch = line =~ /^\[(.+)\]$/
        if (sectionMatch) {
            currentSection = sectionMatch[0][1]
            result[currentSection] = [:]
        } else if (currentSection) {
            def kvMatch = line =~ /^([^=]+)=\s*(.+)$/
            if (kvMatch) {
                def key = kvMatch[0][1].trim()
                def value = kvMatch[0][2].trim()
                result[currentSection][key] = value
            }
        }
    }

    return result
}

def tfApplyJobName = "apply"
def tfDestroyJobName = "destroy"

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

Jenkins jenkins = Jenkins.instance
def JENKINS_HOME = System.getenv("JENKINS_HOME")

def propertiesFileContent = new File("$JENKINS_HOME/jenkins.properties")

def result = [:]
def currentSection = null

propertiesFileContent.eachLine { line ->
        line = line.trim()

        if (line.startsWith("#") || line.isEmpty()) {
            // Ignore comments and empty lines
            return
        }

        def sectionMatch = line =~ /^\[(.+)\]$/
        if (sectionMatch) {
            currentSection = sectionMatch[0][1]
            result[currentSection] = [:]
        } else if (currentSection) {
            def kvMatch = line =~ /^([^=]+)=\s*(.+)$/
            if (kvMatch) {
                def key = kvMatch[0][1].trim()
                def value = kvMatch[0][2].trim()
                result[currentSection][key] = value
            }
        }
}


// Iterate over each section and print its properties
result.each { sectionName, sectionData ->
        git_url = Eval.me(sectionData['git_url'])
        regions = Eval.me(sectionData['regions'])
        outdir_structure = Eval.me(sectionData['outdir_structure'])
        services = sectionData['services'] ? Eval.me(sectionData['services']) : false

// Create jobs for each configuration
jenkins.with {
    Folder ost = getItem(sectionName) ?: createProject(Folder.class, sectionName)

    def jobName = "${sectionName}" + "/" + "setUpOCI"

	def job = jenkins.getItemByFullName(jobName)

    if (job == null) {
        createJob(ost, "setUpOCI", createJobXml('setUpOCI.groovy', git_url))
        ost.getItem("setUpOCI").scheduleBuild2(0)
    }
  
    Folder tf = ost.getItem("terraform_files") ?: ost.createProject(Folder.class, "terraform_files")


    Folder global = tf.getItem("global") ?: tf.createProject(Folder.class, "global")
    Folder rpc = global.getItem("rpc") ?: global.createProject(Folder.class, "rpc")

    rpc.getItem("apply")?:createJob(rpc, tfApplyJobName, createJobXml('apply.groovy', git_url))
    rpc.getItem("destroy")?:createJob(rpc, tfDestroyJobName, createJobXml('destroy.groovy', git_url))

    for (reg in regions) {
        Folder folder = tf.getItem(reg) ?: tf.createProject(Folder.class, reg)

        if (outdir_structure == "Single_Outdir") {
            folder.getItem("apply")?:createJob(folder, tfApplyJobName, createJobXml('apply.groovy', git_url))
            folder.getItem("destroy")?:createJob(folder, tfDestroyJobName, createJobXml('destroy.groovy', git_url))
        }

        if (outdir_structure == "Multiple_Outdir" && services) {
            for (svc in services) {
                Folder svcFolder = folder.getItem(svc) ?: folder.createProject(Folder.class, svc)
                svcFolder.getItem("apply")?:createJob(svcFolder, tfApplyJobName, createJobXml('apply.groovy', git_url))
                svcFolder.getItem("destroy")?:createJob(svcFolder, tfDestroyJobName, createJobXml('destroy.groovy', git_url))
             }
        }
    }
}
}

// Reload Jenkins configuration
Jenkins.instance.reload()
println "Jenkins configuration reloaded."
