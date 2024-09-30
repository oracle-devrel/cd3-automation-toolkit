import jenkins.model.Jenkins
import hudson.model.Cause
import com.cloudbees.hudson.plugins.folder.*

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

  	def jobName = "${sectionName}" + "/" + "setUpOCI"
	def job = jenkins.getItemByFullName(jobName)
    def build = job.getBuildByNumber(1)
    if (build != null) {
        while (build.isBuilding()) {
            sleep(5000)  // Sleep for 5 seconds before checking again
        }
        build.delete()
    } 
}
