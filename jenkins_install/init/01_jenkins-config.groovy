import jenkins.model.*
import com.cloudbees.hudson.plugins.folder.*
import java.io.ByteArrayInputStream
import java.nio.file.Files
import java.nio.file.StandardCopyOption

// Read the Jenkins instance
Jenkins jenkins = Jenkins.getInstance()

// Read the properties file
def JENKINS_HOME = System.getenv("JENKINS_HOME")
File file = new File("$JENKINS_HOME/jenkins.properties")

// Parse the properties file into profiles first.
def profiles = [:]
def currentProfile = ""
file.readLines('UTF-8').each { line ->
    if (line.startsWith('[')) {
        currentProfile = line.replace('[', '').replace(']', '').trim()
        profiles[currentProfile] = [:]
    } else if (line.contains('=')) {
        def parts = line.split('=')
        profiles[currentProfile][parts[0].trim()] = Eval.me(parts[1].trim())
    }
}

// Function to create job XML
def createJobXml(scriptPath, gitUrl, tf_or_tofu) {
    return """
    <flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <properties/>
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

// Function to create Jenkins job if it does not exist
def createJobIfNotExists(parent, jobName, xml) {
    def job = parent.getItem(jobName)
    if (job == null) {
        def jobXmlStream = new ByteArrayInputStream(xml.getBytes())
        parent.createProjectFromXML(jobName, jobXmlStream)
    } else {
        println "Job already exists: ${jobName}"
    }
}

// Create jobs for each profile
profiles.each { profileName, profile ->
    // Create profile folder
    Folder profileFolder = jenkins.getItem(profileName) ?: jenkins.createProject(Folder.class, profileName)
    Folder tfFolder = profileFolder.getItem("terraform_files") ?: profileFolder.createProject(Folder.class, "terraform_files")

    // Create global and rpc folders
    Folder globalFolder = tfFolder.getItem("global") ?: tfFolder.createProject(Folder.class, "global")
    Folder rpcFolder = globalFolder.getItem("rpc") ?: globalFolder.createProject(Folder.class, "rpc")

    // Create jobs in rpc folder
    createJobIfNotExists(rpcFolder, "apply", createJobXml('apply.groovy', profile.git_url, profile.tf_or_tofu))
    createJobIfNotExists(rpcFolder, "destroy", createJobXml('destroy.groovy', profile.git_url, profile.tf_or_tofu))

    profile.regions.each { region ->
        Folder regionFolder = tfFolder.getItem(region) ?: tfFolder.createProject(Folder.class, region)

        if (profile.outdir_structure.contains("Multiple_Outdir") && profile.services) {
            profile.services.each { service ->
                Folder serviceFolder = regionFolder.getItem(service) ?: regionFolder.createProject(Folder.class, service)

                createJobIfNotExists(serviceFolder, "apply", createJobXml('apply.groovy', profile.git_url, profile.tf_or_tofu))
                createJobIfNotExists(serviceFolder, "destroy", createJobXml('destroy.groovy', profile.git_url, profile.tf_or_tofu))
            }
        } else {
            createJobIfNotExists(regionFolder, "apply", createJobXml('apply.groovy', profile.git_url, profile.tf_or_tofu))
            createJobIfNotExists(regionFolder, "destroy", createJobXml('destroy.groovy', profile.git_url, profile.tf_or_tofu))
        }
    }
     // Move setupoci directory to the correct location. Default is not picked up in UI.
    def setupociSrcPath = "$JENKINS_HOME/jobs/${profileName}/setupoci"
    def setupociDestPath = "$JENKINS_HOME/jobs/${profileName}/jobs/setupoci"

    def setupociSrcDir = new File(setupociSrcPath)
    def setupociDestDir = new File(setupociDestPath)

    if (setupociSrcDir.exists()) {
        Files.move(setupociSrcDir.toPath(), setupociDestDir.toPath(), StandardCopyOption.REPLACE_EXISTING)
       // println "Moved directory from ${setupociSrcDir} to ${setupociDestDir}"
    }
}

// Reload Jenkins configuration
Jenkins.instance.reload()
println "Jenkins configuration reloaded."

