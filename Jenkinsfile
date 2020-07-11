pipeline {
    agent { label 'docker' }
    environment {
        TEST_VAR1 = 'true'
        TEST_VAR2 = 'sqlite'
        //AWS_ACCESS_KEY_ID     = credentials('jenkins-aws-secret-key-id')
        //AWS_SECRET_ACCESS_KEY = credentials('jenkins-aws-secret-access-key')
    }
    stages {
        stage('build') {
            steps {
                sh 'echo ========================'
                sh 'echo running Build Stage'
                sh 'python --version'
                sh 'whoami'
                sh 'hostname'
                sh 'pwd'
                sh 'ls -l'
                sh 'printenv'
                sh 'echo ========================'
                // sh 'curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python'
                // sh 'poetry -V'
                sh 'groups'
            }
        }
        stage('lint') {
            steps {
                sh 'echo ========================'
                sh 'echo running Lint Stage, pylint src step'
                sh 'tox -e lint'
                // sh 'exit 1'
            }
        }
        stage('test-unit') {
            steps {
                sh 'echo ========================'
                sh 'echo running Test Stage, Unit-Tests step'
                sh 'tox -e unit'
                // sh 'exit 1'
            }
        }
        stage('test-integration') {
            steps {
                sh 'echo ========================'
                sh 'echo running Test Stage, Integration-Tests step'
                sh 'tox -e integration'
            }
        }
        stage('deploy') {
            steps {
                sh 'echo ========================='
                sh 'echo running Deploy Stage'
            }
        }
    }
    post {
        always {
            echo 'This will always run'
        }
    }
}
