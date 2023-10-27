pipeline {
    agent any
     tools{
        jdk 'jdk17'
        nodejs 'node21'
     }
    environment {
        SSH_CREDENTIALS = credentials('odoo-deploy-server')
        SCANNER_HOME= tool 'sonar-scanner'
    }
    stages {
        
        stage('clean workspace'){
            steps{
                cleanWs()
            }
        }
   
        stage ('Setup Environment') {
            steps {
                script {
                    def gitInfo = checkout scm
                    env.repo_name = gitInfo.GIT_URL.split('/')[-1].replace('.git', '')
                }
            }
        }
        stage("Sonarqube Analysis "){
            steps{
                withSonarQubeEnv('sonar-server') {
                    sh ''' $SCANNER_HOME/bin/sonar-scanner \
                    -Dsonar.sources=./addons \
                    -Dsonar.projectName=test \
                    -Dsonar.projectKey=test '''
                }
            }
        }
        
//        stage("quality gate"){
//           steps {
//                script {
//                    waitForQualityGate abortPipeline: false, credentialsId: 'sonar-token' 
//                }
//            } 
//        }
        
        stage('Install Dependencies') {
            steps {
                sh "npm install"
            }
        }

        stage('OWASP FS SCAN') {
            steps {
                dependencyCheck additionalArguments: '--scan ./ --disableYarnAudit --disableNodeAudit', odcInstallation: 'DP-Check'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }

        stage('TRIVY FS SCAN') {
            steps {
                sh "trivy fs . > trivyfs.txt"
            }
        }

        stage('Install Ansible Role Requirements') {
            steps {
                script {
                    echo "Installing Ansible Role Requirements"
                
                    dir('ansible') {
                     // Install the roles listed in the requirements.yml file.
                    sh 'ansible-galaxy install -r requirements.yml'
                        }
                    
                   
                }
            }
        }

        stage ('Ensure Docker Installed') {
            steps {
                script {
                    echo "Ensuring Docker is installed"
                   
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'odoo-deploy-server', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml install-docker-playbook.yml --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    
                   
                }
            }
        }

        stage ('Deploy') {
            steps {
                script {
                    echo "Deploying to production"
                   
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'odoo-deploy-server', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml deploy-playbook.yml -e "env_name=master" --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    
                    // else if (branch == 'refs/heads/staging'){
                    //     dir('ansible'){
                    //         withCredentials([sshUserPrivateKey(credentialsId: 'odoo-deploy-server', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                    //             sh """
                    //                 ansible-playbook -i inventory.yml deploy-playbook.yml -e "env_name=staging" --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                    //             """
                    //         }
                    //     }
                    // }
                 
                }
            }
        }

        stage("TRIVY image scan"){
            steps{
                sh "trivy master-web:latest postgres:15 > trivyimage.txt" 
                
            }
        }


        stage ('SSL Reverse proxy') {
            steps {
                script {
                    echo "SSL encryption setup"
                   
                        dir('ansible'){
                            withCredentials([sshUserPrivateKey(credentialsId: 'odoo-deploy-server', keyFileVariable: 'SSH_KEY_PATH', usernameVariable: 'SSH_USERNAME')]) {
                                sh """
                                    ansible-playbook -i inventory.yml reverse-proxy.yml --private-key=$SSH_KEY_PATH -u $SSH_USERNAME
                                """
                            }
                        }
                    
                   
                }
            }
        }
    }
}

