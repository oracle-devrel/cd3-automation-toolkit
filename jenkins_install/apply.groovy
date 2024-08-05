def tf_plan = "Changes"

pipeline {
    agent any
    options {
        ansiColor('xterm')
    }

    stages {
        stage('Set Environment Variables') {
            steps {
                script {
                    def jobName = env.JOB_NAME
                    def fileContent = readFile "${JENKINS_HOME}/jenkins.properties"
                    // Split file content into lines
                    def lines = fileContent.readLines()
                    // Process each line to extract variable name and value
                    def variables = [:]
                    lines.each { line ->
                        def parts = line.split('=')
                        if (parts.size() == 2) {
                            variables[parts[0].trim()] = parts[1].trim()
                        }
                    }
                    println "Variables: ${variables}"

                     if (variables.containsKey('tf_or_tofu')) {
                      // Strip quotes from tf_or_tofu value
                       def tfortofuValue = variables['tf_or_tofu'].replaceAll(/^"|"$/, '')
                       env.tf_or_tofu = tfortofuValue
                     } else {
                       println "tfortofu param not found in the properties file"
                     }


                    def variableOds = variables['outdir_structure'].toString().replaceAll("\\[|\\]", '').replaceAll('"', '')
                    env.out_str = "${variableOds}"
                    def parts = jobName.split('/')
                    if (env.out_str == 'Multiple_Outdir') {
                        // Assuming the job name format is <region_name>/job/<service_name>/job/job_name
                        env.Region = parts[2]
                        env.Service = parts[3]
                    } else {
                        // Assuming the job name format is <region_name>/job/job_name
                        env.Region = parts[2]
                        env.Service = ''
                        if (env.Region == 'global') {
                            env.Service = 'rpc'
                        }
                    }
                }
            }
        }

        stage('Plan') {
            when {
                expression {
                    return env.GIT_BRANCH == 'origin/develop';
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def toolCmd = env.tf_or_tofu == 'terraform' ? 'terraform' : 'tofu'
                        sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} init -upgrade"
                        // Run Terraform plan and capture the output
                        terraformPlanOutput = sh(script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} plan -out=tfplan.out", returnStdout: true).trim()
                        // Check if the plan contains any changes
                        if (terraformPlanOutput.contains('No changes.')) {
                            echo 'No changes in Terraform plan. Skipping further stages.'
                            tf_plan = "No Changes"
                        } else {
                            // If there are changes, proceed with applying the plan
                            echo "Changes detected in Terraform plan. Proceeding with apply. \n${terraformPlanOutput}"
                        }
                    }
                }
            }
        }

        // OPA Stage
        stage('OPA') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def toolCmd = env.tf_or_tofu == 'terraform' ? 'terraform' : 'tofu'
                        // Run Terraform show and capture the output
                        sh "set +x && cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} show -json tfplan.out > tfplan.json"
                        // Run OPA eval
                        opaOutput = sh(script: "opa eval -f pretty -b /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA/ -i \"${WORKSPACE}/${env.Region}/${env.Service}/tfplan.json\" data.terraform.deny", returnStdout: true).trim()
                        if (opaOutput == '[]') {
                            echo "No OPA rules are violated. Proceeding with the next stage."
                        } else {
                            echo "OPA Output:\n${opaOutput}"
                            unstable(message: "OPA Rules are violated.")
                        }
                    }
                }
            }
        }

        // Get Approval
        stage('Get Approval') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            options {
                timeout(time: 1440, unit: 'MINUTES') // 24 hours timeout
            }

            steps {
                script {
                    input message: "Do you want to apply the plan?"
                    echo "Approval for the Apply Granted!"
                }
            }
        }

        // Terraform Apply
        stage('Apply') {
            when {
                allOf {
                    expression { return env.GIT_BRANCH == 'origin/develop' }
                    expression { return tf_plan == "Changes" }
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        def toolCmd = env.tf_or_tofu == 'terraform' ? 'terraform' : 'tofu'
                        sh "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} apply --auto-approve tfplan.out"
                    }
                }
            }
        }

        // Git Commit to main
        stage('Git Commit to main') {
            when {
                allOf {
                    expression { return currentBuild.result != "ABORTED" }
                    expression { return currentBuild.result != "FAILURE" }
                }
            }

            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    script {
                        if (env.out_str == 'Multiple_Outdir') {
                            try {
                                sh '''
                                    set +x
                                    mkdir -p ${WORKSPACE}/../${BUILD_NUMBER}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}
                                    git clone ${GIT_URL}
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git checkout main
                                    reg=`echo ${JOB_NAME}| cut -d "/" -f3`
                                    service=`echo ${JOB_NAME}| cut -d "/" -f4`
                                    copy_path=${reg}/${service}
                                    cp -r ${WORKSPACE}/${copy_path}/* ${copy_path}/
                                    git add ${copy_path}*
                                '''
                            } catch (Exception e1) {
                                println(e1)
                                sh '''
                                    set +x
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                '''
                            }
                            sh '''
                                set +x
                                repo_name=${GIT_URL##*/}
                                reg=`echo ${JOB_NAME}| cut -d "/" -f3`
                                service=`echo ${JOB_NAME}| cut -d "/" -f4`
                                cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                git_status=`git status --porcelain`
                                if [[ $git_status ]]; then
                                git commit -m "commit for apply build - ${BUILD_NUMBER} for ${reg}/${service}"
                                else
                                    echo "Nothing to commit"
                                fi
                            '''
                            status = sh(script: '''
                                set +x
                                repo_name=${GIT_URL##*/}
                                cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                git pull --no-edit origin main
                                git push --porcelain origin main
                            ''', returnStatus: true)

                            while (status != 0) {
                                println("Trying again ...")
                                status = sh(script: '''
                                    set +x
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git config pull.rebase true
                                    git pull --no-edit origin main
                                    set -x
                                    git push --porcelain origin main
                                ''', returnStatus: true)
                            }
                            sh '''
                                set +x
                                rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                            '''

                        } else {
                            try {
                                sh '''
                                    set +x
                                    mkdir -p ${WORKSPACE}/../${BUILD_NUMBER}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}
                                    git clone ${GIT_URL}
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git checkout main
                                    reg=`echo ${JOB_NAME}| cut -d "/" -f3`
                                    copy_path=${reg}
                                    cp -r ${WORKSPACE}/${copy_path}/* ${copy_path}/
                                    git add ${copy_path}*
                                    git_status=`git status --porcelain`
                                    if [[ $git_status ]]; then
                                        git commit -m "commit for apply build - ${BUILD_NUMBER} for ${reg}"
                                        git config pull.rebase true
                                        git pull --no-edit origin main
                                        git push origin main
                                    else {
                                        echo "Nothing to commit"
                                    }
                                    cd ${WORKSPACE}/..
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                '''
                            } catch (Exception e1) {
                                println(e1)
                                sh '''
                                    cd ${WORKSPACE}/..
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                '''
                            }
                        }
                    }
                }
            }
        }
    }
}