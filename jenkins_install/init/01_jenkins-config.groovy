import com.cloudbees.hudson.plugins.folder.*
//import org.jenkinsci.plugins.workflow.job.WorkflowJob
import jenkins.model.Jenkins

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

for (os in outdir_structure) {

        def ost = jenkins.getItem("terraform_files")
        if (ost == null) {
                ost = jenkins.createProject(Folder.class,"terraform_files")
               
	def global = ost.getItem("global")
	if (global == null) {
		global = ost.createProject(Folder.class, "global")
		
	def rpc = global.getItem("rpc")
	if (rpc == null) {
		rpc = global.createProject(Folder.class, "rpc")
		
	def tfGlobRpcXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>multiOutput.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
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

                                def tfGlobRpcDestroyXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>multiOutput-tf-destroy.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
                                </hudson.plugins.git.UserRemoteConfig>
                        </userRemoteConfigs>
                        <branches>
                                <hudson.plugins.git.BranchSpec>
                                        <name>main</name>
                                </hudson.plugins.git.BranchSpec>
                        </branches>
                        <configVersion>2</configVersion>
                        <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                        <gitTool>Default</gitTool>
                </scm>
        </definition>
</flow-definition>
"""
                                                def tfGlobRpcXmlStream = new ByteArrayInputStream(tfGlobRpcXml.getBytes())
                                                job1 = rpc.createProjectFromXML(tfApplyJobName, tfGlobRpcXmlStream)
                                                def tfGlobRpcDestroyXmlStream = new ByteArrayInputStream(tfGlobRpcDestroyXml.getBytes())
                                                job2 = rpc.createProjectFromXML(tfDestroyJobName, tfGlobRpcDestroyXmlStream)
			
	}	
}	
		
        for (reg in regions) {
                def folder = ost.getItem(reg)
                if (folder == null) {
                        folder = ost.createProject(Folder.class, reg)
                        if (os == "Single_Outdir"){
                                def tfApplyXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>singleOutput.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
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

                        def tfDestroyXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>singleOutput-tf-destroy.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
                                </hudson.plugins.git.UserRemoteConfig>
                        </userRemoteConfigs>
                        <branches>
                                <hudson.plugins.git.BranchSpec>
                                        <name>main</name>
                                </hudson.plugins.git.BranchSpec>
                        </branches>
                        <configVersion>2</configVersion>
                        <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                        <gitTool>Default</gitTool>
                </scm>
        </definition>
</flow-definition>
"""

                                def tfApplyxmlStream = new ByteArrayInputStream(tfApplyXml.getBytes())
                                job1 = folder.createProjectFromXML(tfApplyJobName, tfApplyxmlStream)
                                def tfDestroyxmlStream = new ByteArrayInputStream(tfDestroyXml.getBytes())
                                job2 = folder.createProjectFromXML(tfDestroyJobName, tfDestroyxmlStream)

                        }
                        if (os == "Multiple_Outdir"){
                                for (svc in services) {
                                        def svobjt = folder.getItem(svc)
                                        if (svobjt == null) {
                                                svobjt = folder.createProject(Folder.class, svc)
                                                 def tfApplyXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>multiOutput.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
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

                                def tfDestroyXml =
"""\
<flow-definition>
        <actions/>
        <description/>
        <keepDependencies>false</keepDependencies>
        <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition">
                <scriptPath>multiOutput-tf-destroy.groovy</scriptPath>
                <lightweight>false</lightweight>
                <scm class="hudson.plugins.git.GitSCM">
                        <userRemoteConfigs>
                                <hudson.plugins.git.UserRemoteConfig>
                                        <url>${git_url}</url>
                                </hudson.plugins.git.UserRemoteConfig>
                        </userRemoteConfigs>
                        <branches>
                                <hudson.plugins.git.BranchSpec>
                                        <name>main</name>
                                </hudson.plugins.git.BranchSpec>
                        </branches>
                        <configVersion>2</configVersion>
                        <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
                        <gitTool>Default</gitTool>
                </scm>
        </definition>
</flow-definition>
"""
                                                def tfApplyxmlStream = new ByteArrayInputStream(tfApplyXml.getBytes())
                                                job1 = svobjt.createProjectFromXML(tfApplyJobName, tfApplyxmlStream)
                                                def tfDestroyxmlStream = new ByteArrayInputStream(tfDestroyXml.getBytes())
                                                job2 = svobjt.createProjectFromXML(tfDestroyJobName, tfDestroyxmlStream)
                                        }
                                }
                        }
                }
        }
    }

}