pipeline {
    agent {
        docker {
            label 'vps'
            image "deepakkt/pulumi-do:python"
            args '-u root'
        }
    }
    environment {
        PULUMI_ACCESS_TOKEN = credentials('pulumi-access-token')
    }
    stages {
        stage("Login to Pulumi") {
            steps {
                sh "pulumi login"
            }
        }
    }
}