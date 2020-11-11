pipeline {
    agent {
        docker {
            label 'vps'
            image "pulumi/pulumi-python:2.13.2"
        }
    }
    stages {
        stage("Install Requirements") {
            steps {
                sh "pip install -r requirements.txt"
            }
        }
        stage("Login to Pulumi") {
            steps {
                sh "pulumi login"
            }
        }
    }
}