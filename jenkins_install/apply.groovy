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
                    def parts = "${env.JOB_NAME}".split('/')
                    env.Prefix = parts[0]

                    def propertiesFileContent = readFile "$JENKINS_HOME/jenkins.properties"
                    def result = [:]
                    def currentSection = null

                    propertiesFileContent.readLines().each { line ->
                        line = line.trim()
                        if (line.startsWith("#") || line.isEmpty()) {
                        // Ignore comments and empty lines
                            return
                        }

                        def sectionMatch = line =~ /^\[(.+)\]$/
                        if (sectionMatch) {
                            currentSection = sectionMatch[0][1]
                            result[currentSection] = [:]
                        }
                        else if (currentSection) {
                            def kvMatch = line =~ /^([^=]+)=\s*(.+)$/
                            if (kvMatch) {
                                def key = kvMatch[0][1].trim()
                                def value = kvMatch[0][2].trim()
                                result[currentSection][key] = value
                            }
                        }
                    }
                    def tfortofuValue = result["${env.Prefix}"]["tf_or_tofu"]
                    env.tf_or_tofu = Eval.me(tfortofuValue)
                    def out_str = result["${env.Prefix}"]["outdir_structure"]
                    env.out_str = Eval.me(out_str)
                    if (env.out_str == 'Multiple_Outdir') {
                        // Assuming the job name format is <region_name>/job/<service_name>/job/job_name
                        env.Region = parts[2]
                        env.Service = parts[3]
                    }
                    else {
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
        // Terraform/Tofu Plan
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
                        labelledShell( label: 'Running init', script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} init -upgrade")
                        // Run Terraform/Tofu plan and capture the output
                        planOutput = labelledShell( label: 'Running plan', script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} plan -out=tfplan.out", returnStdout: true).trim()
                        // Check if the plan contains any changes
                        if (planOutput.contains('No changes.')) {
                            echo 'No changes in Plan. Skipping further stages.'
                            tf_plan = "No Changes"
                        } else {
                            // If there are changes, proceed with applying the plan
                            echo "Changes detected in Plan. Proceeding with apply. \n${planOutput}"
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
                        // Run Terraform/Tofu show and capture the output
                        // Run OPA eval
                        opaOutput = labelledShell( label: 'Evaluating plan against OPA', script: "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} show -json tfplan.out > tfplan.json && opa eval -f pretty -b /cd3user/oci_tools/cd3_automation_toolkit/user-scripts/OPA/ -i \"${WORKSPACE}/${env.Region}/${env.Service}/tfplan.json\" data.terraform.deny", returnStdout: true).trim()
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

        // Terraform/Tofu Apply
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
                        labelledShell( label: 'Running apply', script:  "cd \"${WORKSPACE}/${env.Region}/${env.Service}\" && ${toolCmd} apply --auto-approve tfplan.out")
                    }
                }
            }
        }

        // Git Commit to main
        stage('GIT Commit to main') {
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
                                 labelledShell( label: 'Performing git operations', script: '''
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
                                ''')
                            } catch (Exception e1) {
                                println(e1)
                                 labelledShell( label: 'Cleanup', script: '''
                                    set +x
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                ''')
                            }
                            labelledShell( label: 'Preparing commit', script: '''
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
                            ''')
                            status = labelledShell( label: 'git operations', script: '''
                                set +x
                                repo_name=${GIT_URL##*/}
                                cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                git pull --no-edit origin main
                                git push --porcelain origin main
                            ''', returnStatus: true)

                            while (status != 0) {
                                println("Trying again ...")
                                status = labelledShell( label: 'git operations - trying again', script: '''
                                    set +x
                                    repo_name=${GIT_URL##*/}
                                    cd ${WORKSPACE}/../${BUILD_NUMBER}/${repo_name}
                                    git config pull.rebase true
                                    git pull --no-edit origin main
                                    set -x
                                    git push --porcelain origin main
                                ''', returnStatus: true)
                            }
                            labelledShell( label: 'Cleanup', script: '''
                                set +x
                                rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                            ''')

                        } else {
                            try {
                                labelledShell( label: 'Performing git operations', script: '''
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
                                    else
                                        echo "Nothing to commit"
                                    fi

                                    cd ${WORKSPACE}/..
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                ''')
                            } catch (Exception e1) {
                                println(e1)
                                labelledShell( label: 'Cleanup', script: '''
                                    cd ${WORKSPACE}/..
                                    rm -rf ${WORKSPACE}/../${BUILD_NUMBER}
                                    exit 1
                                ''')
                            }
                        }
                    }
                }
            }
        }
    }
}