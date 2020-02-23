pipeline {
    agent docker
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
        stage('test') {
            steps {
                sh 'echo ========================'                
                sh 'echo running Test Stage'
                sh 'tox'
                // sh 'tox'
                // sh 'exit 1'
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
