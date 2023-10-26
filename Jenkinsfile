pipeline {
    agent any
    environment {
        SSH_CREDENTIALS = credentials('odoo-deploy-server')
    }
    stages {
        stage ('Setup Environment') {
            steps {
                script {
                    def gitInfo = checkout scm
                    env.repo_name = gitInfo.GIT_URL.split('/')[-1].replace('.git', '')
                }
            }
        }

       stage('Install Ansible Role Requirements') {
            steps {
                script {
                    echo "Installing Ansible Role Requirements"
                    if (branch == 'refs/heads/master'){
                        dir('ansible') {
                            // Install the roles listed in the requirements.yml file.
                            sh 'ansible-galaxy install -r requirements.yml'
                        }
                    }
                    else {
                        echo "Skipped installing Ansible Role Requirements"
                    }
                }
            }
        }

        stage ('Ensure Docker Installed') {
            steps {
                script {
                    echo "Ensuring Docker is installed"
                    if (branch == 'refs/heads/master'){
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'sylcon-ssh-key', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml install-docker-playbook.yml --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    }
                    else {
                        echo "Skipped installing Docker"
                    }
                }
            }
        }

        stage ('Deploy') {
            steps {
                script {
                    echo "Deploying to master"
                    if (branch == 'refs/heads/master'){
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'sylcon-ssh-key', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml deploy-playbook.yml -e "env_name=master" --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    }
                    // else if (branch == 'refs/heads/staging'){
                    //     dir('ansible'){
                    //         withCredentials([sshUserPrivateKey(credentialsId: 'sylcon-ssh-key', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                    //             sh """
                    //                 ansible-playbook -i inventory.yml deploy-playbook.yml -e "env_name=staging" --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                    //             """
                    //         }
                    //     }
                    // }
                    else {
                        echo "Skipped deploying to master"
                    }
                }
            }
        }

        stage ('SSL Reverse proxy') {
            steps {
                script {
                    echo "SSL encryption setup"
                    if (branch == 'refs/heads/master'){
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'sylcon-ssh-key', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml reverse-proxy.yml --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    }
                    else {
                        echo "Skipping SSL"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def buildStatus = currentBuild.currentResult == 'SUCCESS' ? 'good' : 'danger'
                def userId = slackUserIdFromEmail(email) 

                def update_message = """*Github Repo Name*: $repo_name 

*Commit by*: <@$userId> 

*Git branch* : ${branch} 

*Commit message* : ${commit_message} 

Build status of 
${env.JOB_NAME} #${env.BUILD_NUMBER} 
(${env.BUILD_URL}) 
was *${currentBuild.currentResult}*.

*Deployed to master*"""

                if (branch != 'refs/heads/master') {
                    update_message = """NOT Deployed because the BRANCH name is ${branch}

Github Repo Name: $repo_name 

Commit by: <@$userId> 

Git branch : ${branch} 

Commit message : ${commit_message} 

Build status of 
*${env.JOB_NAME} #${env.BUILD_NUMBER} 
(${env.BUILD_URL})*
was *${currentBuild.currentResult}*."""
                }

                slackSend(color: buildStatus, message: update_message, notifyCommitters: true)
            }
        }
    }
}
