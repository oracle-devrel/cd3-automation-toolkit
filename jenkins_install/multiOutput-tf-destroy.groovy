/* Set the various stages of the build */
def tf_plan = "Changes"
pipeline {
    agent any
    options {
        ansiColor('xterm')
    }
    stages {
        stage('Terraform Destroy Plan') {
            when {
                expression { return env.GIT_BRANCH == 'origin/main';}
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                script {
					def jobName = env.JOB_NAME
                    def parts = jobName.split('/')

                    // Assuming the job name format is <region_name>/job/<service_name>/job/job_name
                    def regionName = parts[1]
                    def serviceName = parts[2]

                    // Set environment variables for reuse in subsequent stages
                    env.Region = regionName
                    env.Service = serviceName
        	    
                    sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform init -upgrade"
          	        //sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform plan -destroy"


                    // Run Terraform plan
                    def terraformPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\"  && terraform plan -destroy", returnStdout: true).trim()

                    // Check if the plan contains any changes
                    if (terraformPlanOutput.contains('No changes.')) {
                        echo 'No changes in Terraform plan. Skipping further stages.'
                        tf_plan = "No Changes"
                    } else {
                        // If there are changes, proceed with applying the plan
                        echo "Proceeding with destroy. \n${terraformPlanOutput}"

                    }

                }
				}
            }
        }

        /** Approval for Terraform Apply **/
        stage('Get Approval') {
            when {
              allOf{
                expression {return env.GIT_BRANCH == 'origin/main'; }
                expression {return tf_plan == "Changes" }
				expression {return currentBuild.result != "FAILURE" }
			  }
            }
            input {
                message "Do you want to perform terraform destroy?"

            }
            steps {
                echo "Approval for the Destroy Granted!"
            }
        }

        stage('Terraform Destroy') {
            when {
             allOf{
                expression {return env.GIT_BRANCH == 'origin/main'; }
                expression {return tf_plan == "Changes" }
				expression {return currentBuild.result != "FAILURE" }
			  }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
				script {
                    sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && terraform destroy --auto-approve"
                }
            }
			}
        }
    }
}
