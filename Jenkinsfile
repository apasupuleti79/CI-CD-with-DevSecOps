pipeline {
    agent any
    
    environment {
        // Application Configuration
        APP_NAME = 'my-devsecops-app'
        APP_VERSION = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'your-registry.com'
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${APP_NAME}:${APP_VERSION}"
        
        // Security Tools Configuration
        SONARQUBE_SERVER = 'SonarQube'
        OWASP_ZAP_URL = 'http://localhost:8080'
        
        // Deployment Configuration
        STAGING_NAMESPACE = 'staging'
        PRODUCTION_NAMESPACE = 'production'
        
        // Credentials
        DOCKER_CREDENTIALS = 'docker-registry-credentials'
        K8S_CREDENTIALS = 'kubernetes-credentials'
        SONAR_TOKEN = 'sonarqube-token'
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out source code..."
                    checkout scm
                    
                    // Set build information
                    currentBuild.displayName = "#${BUILD_NUMBER} - ${APP_NAME}"
                    currentBuild.description = "DevSecOps Pipeline for ${APP_NAME}"
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    echo "🏗️ Building application..."
                    
                    // Install dependencies and build
                    sh '''
                        echo "Installing dependencies..."
                        pip install -r requirements.txt
                        
                        echo "Running application build..."
                        python setup.py build
                    '''
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    echo "🧪 Running unit tests..."
                    
                    sh '''
                        # Run unit tests with coverage
                        python -m pytest tests/ --cov=src --cov-report=xml --cov-report=html --junitxml=test-results.xml
                    '''
                    
                    // Publish test results
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverage adapters: [
                        coberturaAdapter('coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('SAST - Static Security Analysis') {
            parallel {
                stage('SonarQube Analysis') {
                    steps {
                        script {
                            echo "🔍 Running SonarQube static analysis..."
                            
                            withSonarQubeEnv(SONARQUBE_SERVER) {
                                sh '''
                                    sonar-scanner \
                                        -Dsonar.projectKey=${APP_NAME} \
                                        -Dsonar.projectName=${APP_NAME} \
                                        -Dsonar.projectVersion=${APP_VERSION} \
                                        -Dsonar.sources=src \
                                        -Dsonar.tests=tests \
                                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                                        -Dsonar.python.xunit.reportPath=test-results.xml
                                '''
                            }
                        }
                    }
                }
                
                stage('Bandit Security Scan') {
                    steps {
                        script {
                            echo "🛡️ Running Bandit security scan..."
                            
                            sh '''
                                # Install bandit if not available
                                pip install bandit
                                
                                # Run bandit security scan
                                bandit -r src/ -f json -o bandit-report.json || true
                                bandit -r src/ -f txt -o bandit-report.txt || true
                            '''
                            
                            // Archive security reports
                            archiveArtifacts artifacts: 'bandit-report.*', allowEmptyArchive: true
                        }
                    }
                }
                
                stage('Safety Dependency Check') {
                    steps {
                        script {
                            echo "📦 Checking dependencies for vulnerabilities..."
                            
                            sh '''
                                # Install safety
                                pip install safety
                                
                                # Check for known vulnerabilities
                                safety check --json --output safety-report.json || true
                                safety check --output safety-report.txt || true
                            '''
                            
                            archiveArtifacts artifacts: 'safety-report.*', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    echo "🚪 Waiting for SonarQube Quality Gate..."
                    
                    timeout(time: 5, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }
        }
        
        stage('OWASP Dependency Check') {
            steps {
                script {
                    echo "🔐 Running OWASP Dependency Check..."
                    
                    dependencyCheck additionalArguments: '''
                        --scan ./
                        --format XML
                        --format HTML
                        --format JSON
                        --prettyPrint
                    ''', odcInstallation: 'OWASP-Dependency-Check'
                    
                    dependencyCheckPublisher pattern: 'dependency-check-report.xml'
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    
                    // Build Docker image
                    def dockerImage = docker.build("${DOCKER_IMAGE}", "./docker")
                    
                    // Tag the image
                    dockerImage.tag("latest")
                    dockerImage.tag("${APP_VERSION}")
                }
            }
        }
        
        stage('Container Security Scan') {
            steps {
                script {
                    echo "🔒 Scanning Docker image for vulnerabilities..."
                    
                    sh '''
                        # Install trivy if not available
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy..."
                            wget -qO- https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz | tar xz
                            sudo mv trivy /usr/local/bin/
                        fi
                        
                        # Scan the Docker image
                        trivy image --format json --output trivy-report.json ${DOCKER_IMAGE} || true
                        trivy image --format table --output trivy-report.txt ${DOCKER_IMAGE} || true
                    '''
                    
                    archiveArtifacts artifacts: 'trivy-report.*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Push Docker Image') {
            steps {
                script {
                    echo "📤 Pushing Docker image to registry..."
                    
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS, 
                                                    usernameVariable: 'DOCKER_USER', 
                                                    passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo $DOCKER_PASS | docker login ${DOCKER_REGISTRY} -u $DOCKER_USER --password-stdin
                            docker push ${DOCKER_IMAGE}
                            docker push ${DOCKER_REGISTRY}/${APP_NAME}:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                script {
                    echo "🚀 Deploying to staging environment..."
                    
                    withCredentials([kubeconfigFile(credentialsId: K8S_CREDENTIALS, variable: 'KUBECONFIG')]) {
                        sh '''
                            # Update Kubernetes manifests with new image
                            sed -i "s|IMAGE_TAG|${APP_VERSION}|g" k8s/staging/deployment.yaml
                            
                            # Apply Kubernetes manifests
                            kubectl apply -f k8s/staging/ -n ${STAGING_NAMESPACE}
                            
                            # Wait for deployment to be ready
                            kubectl rollout status deployment/${APP_NAME} -n ${STAGING_NAMESPACE} --timeout=300s
                        '''
                    }
                }
            }
        }
        
        stage('DAST - Dynamic Security Testing') {
            steps {
                script {
                    echo "🎯 Running OWASP ZAP DAST scan..."
                    
                    // Get staging application URL
                    def stagingUrl = sh(
                        script: "kubectl get service ${APP_NAME} -n ${STAGING_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'",
                        returnStdout: true
                    ).trim()
                    
                    if (stagingUrl) {
                        sh """
                            # Run ZAP baseline scan
                            docker run -t owasp/zap2docker-stable zap-baseline.py \
                                -t http://${stagingUrl} \
                                -J zap-report.json \
                                -r zap-report.html || true
                        """
                        
                        archiveArtifacts artifacts: 'zap-report.*', allowEmptyArchive: true
                    } else {
                        echo "⚠️ Could not determine staging URL, skipping DAST scan"
                    }
                }
            }
        }
        
        stage('Security Report') {
            steps {
                script {
                    echo "📊 Generating consolidated security report..."
                    
                    sh '''
                        # Create security report directory
                        mkdir -p security-reports
                        
                        # Copy all security reports
                        cp bandit-report.* security-reports/ 2>/dev/null || true
                        cp safety-report.* security-reports/ 2>/dev/null || true
                        cp trivy-report.* security-reports/ 2>/dev/null || true
                        cp zap-report.* security-reports/ 2>/dev/null || true
                        cp dependency-check-report.* security-reports/ 2>/dev/null || true
                        
                        # Generate summary report
                        python security/generate_security_report.py
                    '''
                    
                    archiveArtifacts artifacts: 'security-reports/**', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'security-reports',
                        reportFiles: 'security-summary.html',
                        reportName: 'Security Report'
                    ])
                }
            }
        }
        
        stage('Approval for Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "⏳ Waiting for approval to deploy to production..."
                    
                    def userInput = input(
                        id: 'productionDeploy',
                        message: 'Deploy to production?',
                        parameters: [
                            choice(choices: ['Deploy', 'Abort'], 
                                  description: 'Choose action', 
                                  name: 'action')
                        ]
                    )
                    
                    if (userInput != 'Deploy') {
                        error("Production deployment aborted by user")
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🎯 Deploying to production environment..."
                    
                    withCredentials([kubeconfigFile(credentialsId: K8S_CREDENTIALS, variable: 'KUBECONFIG')]) {
                        sh '''
                            # Update Kubernetes manifests with new image
                            sed -i "s|IMAGE_TAG|${APP_VERSION}|g" k8s/production/deployment.yaml
                            
                            # Apply Kubernetes manifests
                            kubectl apply -f k8s/production/ -n ${PRODUCTION_NAMESPACE}
                            
                            # Wait for deployment to be ready
                            kubectl rollout status deployment/${APP_NAME} -n ${PRODUCTION_NAMESPACE} --timeout=600s
                        '''
                    }
                }
            }
        }
        
        stage('Post-Deployment Monitoring') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "📈 Setting up post-deployment monitoring..."
                    
                    sh '''
                        # Run health checks
                        python monitoring/health_check.py --environment production
                        
                        # Set up alerts
                        python monitoring/setup_alerts.py --deployment ${APP_VERSION}
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🧹 Cleaning up workspace..."
                
                // Clean up Docker images
                sh '''
                    docker rmi ${DOCKER_IMAGE} || true
                    docker rmi ${DOCKER_REGISTRY}/${APP_NAME}:latest || true
                    docker system prune -f || true
                '''
                
                // Archive logs and reports
                archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
            }
        }
        
        success {
            script {
                echo "✅ Pipeline completed successfully!"
                
                // Send success notification
                emailext (
                    subject: "✅ DevSecOps Pipeline Success - ${APP_NAME} v${APP_VERSION}",
                    body: """
                        <h2>DevSecOps Pipeline Completed Successfully</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${APP_VERSION}</p>
                        <p><strong>Build Number:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Branch:</strong> ${BRANCH_NAME}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        
                        <h3>Security Scan Results:</h3>
                        <p>All security scans have been completed. Please review the security report for detailed findings.</p>
                    """,
                    to: "${env.CHANGE_AUTHOR_EMAIL ?: 'team@company.com'}",
                    mimeType: 'text/html'
                )
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Send failure notification
                emailext (
                    subject: "❌ DevSecOps Pipeline Failed - ${APP_NAME} v${APP_VERSION}",
                    body: """
                        <h2>DevSecOps Pipeline Failed</h2>
                        <p><strong>Application:</strong> ${APP_NAME}</p>
                        <p><strong>Version:</strong> ${APP_VERSION}</p>
                        <p><strong>Build Number:</strong> ${BUILD_NUMBER}</p>
                        <p><strong>Branch:</strong> ${BRANCH_NAME}</p>
                        <p><strong>Build URL:</strong> <a href="${BUILD_URL}">${BUILD_URL}</a></p>
                        <p><strong>Console Output:</strong> <a href="${BUILD_URL}console">${BUILD_URL}console</a></p>
                        
                        <h3>Failure Details:</h3>
                        <p>Please check the build logs for detailed error information.</p>
                    """,
                    to: "${env.CHANGE_AUTHOR_EMAIL ?: 'team@company.com'}",
                    mimeType: 'text/html'
                )
            }
        }
        
        unstable {
            script {
                echo "⚠️ Pipeline completed with warnings!"
            }
        }
    }
}
