#!groovy
@Library('cop-pipeline-step') _

def buildNotification(String status) {
    slackSend(status)
}

pipeline {
    agent any

    parameters {
        booleanParam(
            name: 'DEPLOY_TO_TEST',
            defaultValue: false,
        )
    }

    options {
        ansiColor 'xterm'
        buildDiscarder logRotator(daysToKeepStr: '14', numToKeepStr: '50')
        timestamps()
    }

    stages {

        stage('Build') {
            steps {
                buildNotification("Start")
                addShortText(text: "Branch: ${BRANCH_NAME}")
                script {
                    ...build something...
                }
            }
        }

        stage('Test') {
            steps {
                junit(testResults: 'reports/${BUILD_NUMBER}/*.junit.xml')
            }
        }

        stage('Deploy: Test') {
            when {
                anyOf {
                    branch 'develop'
                    expression { return params.DEPLOY_TO_TEST }
                }
            }
            failFast true
            parallel {
                stage ('AWS Global') {
                    steps {
                        ...deploy to AWS Global...
                    }
                }
                stage ('AWS GC') {
                    agent {
                        label "ec2-ondemand-agent-cn"
                    }
                    steps {
                        ...deploy to AWS China...
                    }
                }
            }
        }
    }

    post {
        success {
            buildNotification("SUCCESS")
        }
        unsuccessful {
            buildNotification("FAILED")
        }
    }

}
