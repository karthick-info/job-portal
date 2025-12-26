"""
Script to add IT jobs across various fields to the job portal database.
Run this script from the myproject directory: python add_it_jobs.py
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import Job

# IT Jobs Data - Covering All Major IT Fields
IT_JOBS = [
    # ===== SOFTWARE DEVELOPMENT =====
    {
        'title': 'Senior Python Developer',
        'company_name': 'TechCorp Solutions',
        'description': 'We are looking for an experienced Python Developer to join our dynamic team. You will be responsible for developing scalable web applications, APIs, and backend services using Python frameworks.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹15,00,000 - ₹25,00,000 per annum',
        'requirements': 'Bachelor\'s degree in Computer Science or related field. 3+ years of Python development experience. Strong knowledge of Django/Flask frameworks.',
        'skills_required': 'Python, Django, Flask, REST APIs, PostgreSQL, Redis, Docker, Git',
        'responsibilities': 'Design and implement robust backend services. Write clean, maintainable code. Collaborate with frontend developers. Participate in code reviews.',
        'benefits': 'Health Insurance, Flexible working hours, Remote work options, Annual bonus, Learning allowance',
        'vacancies': 3,
        'is_featured': True
    },
    {
        'title': 'Full Stack JavaScript Developer',
        'company_name': 'InnovateTech',
        'description': 'Join our team as a Full Stack Developer working with modern JavaScript technologies. Build cutting-edge web applications using React and Node.js.',
        'location': 'Hyderabad, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹8,00,000 - ₹15,00,000 per annum',
        'requirements': 'Strong proficiency in JavaScript/TypeScript. Experience with React and Node.js. Understanding of RESTful APIs.',
        'skills_required': 'JavaScript, TypeScript, React, Node.js, MongoDB, Express.js, HTML5, CSS3, Git',
        'responsibilities': 'Develop responsive web applications. Build RESTful APIs. Write unit and integration tests. Optimize applications for performance.',
        'benefits': 'Medical insurance, Gym membership, Free meals, Stock options',
        'vacancies': 5,
        'is_featured': True
    },
    {
        'title': 'Java Backend Developer',
        'company_name': 'Enterprise Solutions Ltd',
        'description': 'Looking for a skilled Java Developer to work on enterprise-grade applications using Spring Boot and microservices architecture.',
        'location': 'Pune, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹12,00,000 - ₹20,00,000 per annum',
        'requirements': 'B.Tech/M.Tech in Computer Science. Strong Java fundamentals. Experience with Spring ecosystem.',
        'skills_required': 'Java, Spring Boot, Microservices, Kafka, MySQL, AWS, Docker, Kubernetes',
        'responsibilities': 'Design and develop microservices. Implement CI/CD pipelines. Ensure code quality and performance.',
        'benefits': 'Health insurance, Performance bonus, Flexible timings, WFH options',
        'vacancies': 4,
        'is_featured': False
    },
    {
        'title': 'Android Developer',
        'company_name': 'MobileFirst Apps',
        'description': 'We need a passionate Android Developer to build high-quality mobile applications. Work with the latest Android technologies and Kotlin.',
        'location': 'Mumbai, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹7,00,000 - ₹12,00,000 per annum',
        'requirements': 'Experience in Android app development. Proficiency in Kotlin. Understanding of Android SDK and Material Design.',
        'skills_required': 'Kotlin, Java, Android SDK, Jetpack Compose, Room Database, Retrofit, Firebase',
        'responsibilities': 'Develop and maintain Android applications. Collaborate with UX designers. Publish apps to Play Store.',
        'benefits': 'Learning budget, Flexible hours, Team outings',
        'vacancies': 2,
        'is_featured': False
    },
    {
        'title': 'iOS Developer',
        'company_name': 'Apple Innovations',
        'description': 'Join our iOS development team to create beautiful and performant applications for iPhone and iPad using Swift.',
        'location': 'Chennai, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹8,00,000 - ₹14,00,000 per annum',
        'requirements': 'Strong knowledge of Swift and iOS SDK. Experience with Xcode and iOS development best practices.',
        'skills_required': 'Swift, SwiftUI, UIKit, Core Data, REST APIs, Git, Xcode, CocoaPods',
        'responsibilities': 'Build iOS applications from scratch. Integrate third-party APIs. Ensure app store compliance.',
        'benefits': 'MacBook provided, Health insurance, Performance bonus',
        'vacancies': 2,
        'is_featured': False
    },
    {
        'title': 'React Native Developer',
        'company_name': 'CrossPlatform Tech',
        'description': 'Looking for a React Native developer to build cross-platform mobile applications for both iOS and Android.',
        'location': 'Delhi NCR, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹9,00,000 - ₹16,00,000 per annum',
        'requirements': 'Experience with React Native development. Strong JavaScript skills. Understanding of mobile app lifecycle.',
        'skills_required': 'React Native, JavaScript, TypeScript, Redux, REST APIs, Firebase, expo',
        'responsibilities': 'Develop cross-platform mobile apps. Maintain code quality. Collaborate with backend team.',
        'benefits': 'Remote work, Medical coverage, Annual bonus',
        'vacancies': 3,
        'is_featured': False
    },
    
    # ===== DATA SCIENCE & MACHINE LEARNING =====
    {
        'title': 'Data Scientist',
        'company_name': 'DataDriven Analytics',
        'description': 'Join our data science team to develop predictive models and derive insights from complex datasets. Work on cutting-edge ML projects.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹18,00,000 - ₹30,00,000 per annum',
        'requirements': 'Masters/PhD in Statistics, Mathematics, or Computer Science. Strong programming skills. Experience with ML frameworks.',
        'skills_required': 'Python, R, TensorFlow, PyTorch, Scikit-learn, SQL, Pandas, NumPy, Tableau',
        'responsibilities': 'Build predictive models. Analyze large datasets. Present insights to stakeholders. Deploy ML models to production.',
        'benefits': 'Research allowance, Conference sponsorship, Stock options, Premium health insurance',
        'vacancies': 2,
        'is_featured': True
    },
    {
        'title': 'Machine Learning Engineer',
        'company_name': 'AI Solutions Inc',
        'description': 'We are seeking a Machine Learning Engineer to design, build, and deploy ML models at scale. Work on NLP, Computer Vision, and recommendation systems.',
        'location': 'Hyderabad, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹20,00,000 - ₹35,00,000 per annum',
        'requirements': 'Strong background in ML/AI. Experience with deep learning frameworks. Knowledge of MLOps practices.',
        'skills_required': 'Python, TensorFlow, PyTorch, MLflow, Kubernetes, Docker, AWS SageMaker, Computer Vision, NLP',
        'responsibilities': 'Design ML pipelines. Train and optimize models. Deploy models to production. Monitor model performance.',
        'benefits': 'GPU workstations, Remote work, Learning budget, ESOPs',
        'vacancies': 3,
        'is_featured': True
    },
    {
        'title': 'Data Analyst',
        'company_name': 'Business Insights Co',
        'description': 'Looking for a Data Analyst to transform raw data into actionable business insights. Create dashboards and reports for decision-making.',
        'location': 'Mumbai, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹6,00,000 - ₹12,00,000 per annum',
        'requirements': 'Bachelor\'s degree in relevant field. Proficiency in SQL and Excel. Experience with visualization tools.',
        'skills_required': 'SQL, Excel, Power BI, Tableau, Python, Statistics, Data Visualization',
        'responsibilities': 'Analyze business data. Create reports and dashboards. Identify trends and patterns.',
        'benefits': 'Health insurance, Flexible timing, Learning opportunities',
        'vacancies': 4,
        'is_featured': False
    },
    {
        'title': 'AI Research Scientist',
        'company_name': 'DeepMind India',
        'description': 'Join our research team to push the boundaries of artificial intelligence. Work on fundamental AI research and publish papers.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '5-10',
        'salary': '₹40,00,000 - ₹70,00,000 per annum',
        'requirements': 'PhD in AI/ML or related field. Strong publication record. Expertise in deep learning.',
        'skills_required': 'PyTorch, TensorFlow, Python, Research Methodology, Deep Learning, Reinforcement Learning',
        'responsibilities': 'Conduct fundamental research. Publish papers. Mentor junior researchers. Collaborate with global teams.',
        'benefits': 'World-class research facilities, Conference travel, Stock options, Relocation support',
        'vacancies': 2,
        'is_featured': True
    },
    
    # ===== CLOUD & DEVOPS =====
    {
        'title': 'Cloud Solutions Architect',
        'company_name': 'CloudFirst Technologies',
        'description': 'Design and implement cloud architecture solutions for enterprise clients. Work with multi-cloud environments and lead cloud transformations.',
        'location': 'Pune, India',
        'job_type': 'full-time',
        'experience_required': '5-10',
        'salary': '₹25,00,000 - ₹45,00,000 per annum',
        'requirements': 'Extensive experience with AWS/Azure/GCP. Cloud certifications preferred. Strong architectural skills.',
        'skills_required': 'AWS, Azure, GCP, Terraform, CloudFormation, Docker, Kubernetes, Security, Networking',
        'responsibilities': 'Design cloud architectures. Lead migration projects. Optimize costs. Ensure security compliance.',
        'benefits': 'Certification sponsorship, Premium insurance, Remote work, Leadership training',
        'vacancies': 2,
        'is_featured': True
    },
    {
        'title': 'DevOps Engineer',
        'company_name': 'Agile Ops Solutions',
        'description': 'We are looking for a DevOps Engineer to build and maintain CI/CD pipelines, automate infrastructure, and improve deployment processes.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹15,00,000 - ₹28,00,000 per annum',
        'requirements': 'Strong Linux skills. Experience with container orchestration. Knowledge of IaC tools.',
        'skills_required': 'Docker, Kubernetes, Jenkins, GitHub Actions, Terraform, Ansible, AWS, Linux, Python, Bash',
        'responsibilities': 'Build CI/CD pipelines. Manage container orchestration. Monitor systems. Automate deployments.',
        'benefits': 'Remote work, Learning budget, Health coverage, Annual bonus',
        'vacancies': 4,
        'is_featured': False
    },
    {
        'title': 'Site Reliability Engineer (SRE)',
        'company_name': 'ScaleUp Systems',
        'description': 'Join as an SRE to ensure the reliability and performance of our distributed systems. Focus on automation, monitoring, and incident response.',
        'location': 'Hyderabad, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹18,00,000 - ₹32,00,000 per annum',
        'requirements': 'Experience with large-scale distributed systems. Strong coding skills. On-call experience.',
        'skills_required': 'Python, Go, Kubernetes, Prometheus, Grafana, ELK Stack, AWS, GCP, Terraform',
        'responsibilities': 'Ensure system reliability. Implement monitoring. Handle incidents. Conduct post-mortems.',
        'benefits': 'On-call compensation, Remote flexibility, Stock options, Learning budget',
        'vacancies': 3,
        'is_featured': False
    },
    {
        'title': 'AWS Cloud Engineer',
        'company_name': 'Amazon Web Services Partner',
        'description': 'Looking for AWS Cloud Engineers to design, deploy, and manage cloud infrastructure on AWS. Help clients with their cloud journey.',
        'location': 'Chennai, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹10,00,000 - ₹18,00,000 per annum',
        'requirements': 'AWS certifications preferred. Experience with core AWS services. Basic Linux and networking skills.',
        'skills_required': 'AWS EC2, S3, Lambda, RDS, VPC, CloudFormation, IAM, Linux, Python',
        'responsibilities': 'Deploy AWS infrastructure. Manage cloud resources. Optimize costs. Ensure security.',
        'benefits': 'AWS certification sponsorship, Health insurance, Flexible hours',
        'vacancies': 5,
        'is_featured': False
    },
    
    # ===== CYBERSECURITY =====
    {
        'title': 'Cybersecurity Analyst',
        'company_name': 'SecureNet Solutions',
        'description': 'Join our security team to protect enterprise systems from cyber threats. Monitor security events and respond to incidents.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹8,00,000 - ₹15,00,000 per annum',
        'requirements': 'Understanding of security concepts. Knowledge of SIEM tools. Security certifications are a plus.',
        'skills_required': 'SIEM, Firewalls, IDS/IPS, Network Security, Incident Response, Linux, Python',
        'responsibilities': 'Monitor security alerts. Investigate incidents. Conduct vulnerability assessments. Update security policies.',
        'benefits': 'Security certification sponsorship, Health insurance, Shift allowance',
        'vacancies': 4,
        'is_featured': False
    },
    {
        'title': 'Penetration Tester',
        'company_name': 'EthicalHack Pro',
        'description': 'We need skilled penetration testers to identify vulnerabilities in client applications and infrastructure. Think like a hacker to protect systems.',
        'location': 'Mumbai, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹15,00,000 - ₹28,00,000 per annum',
        'requirements': 'OSCP/CEH certification. Experience with penetration testing tools. Strong ethical hacking skills.',
        'skills_required': 'Burp Suite, Metasploit, Nmap, Kali Linux, Web App Security, Network Security, Python',
        'responsibilities': 'Conduct penetration tests. Write detailed reports. Recommend remediation. Stay updated on vulnerabilities.',
        'benefits': 'Bug bounty bonus, Certification support, Flexible hours, Conference attendance',
        'vacancies': 2,
        'is_featured': True
    },
    {
        'title': 'Security Engineer',
        'company_name': 'CryptoShield Tech',
        'description': 'Design and implement security solutions for our products. Work on encryption, authentication, and secure coding practices.',
        'location': 'Delhi NCR, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹18,00,000 - ₹30,00,000 per annum',
        'requirements': 'Strong background in security engineering. Experience with cryptography. Knowledge of secure SDLC.',
        'skills_required': 'Cryptography, OAuth, SAML, Security Architecture, Python, Go, AWS Security',
        'responsibilities': 'Design security solutions. Implement authentication systems. Conduct security reviews.',
        'benefits': 'Remote work, Premium insurance, Stock options, Learning budget',
        'vacancies': 2,
        'is_featured': False
    },
    
    # ===== DATABASE & BACKEND =====
    {
        'title': 'Database Administrator (DBA)',
        'company_name': 'DataCore Systems',
        'description': 'Manage and optimize database systems for high-performance applications. Work with both SQL and NoSQL databases.',
        'location': 'Pune, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹12,00,000 - ₹22,00,000 per annum',
        'requirements': 'Strong experience with database administration. Knowledge of performance tuning. Backup and recovery expertise.',
        'skills_required': 'MySQL, PostgreSQL, MongoDB, Redis, Database Optimization, Backup/Recovery, Linux, SQL',
        'responsibilities': 'Manage database systems. Optimize queries. Implement backup strategies. Ensure high availability.',
        'benefits': 'Health insurance, Performance bonus, WFH options',
        'vacancies': 2,
        'is_featured': False
    },
    {
        'title': 'Big Data Engineer',
        'company_name': 'DataLake Analytics',
        'description': 'Build and maintain big data pipelines to process and analyze large volumes of data. Work with distributed computing frameworks.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹18,00,000 - ₹32,00,000 per annum',
        'requirements': 'Experience with big data technologies. Strong programming skills. Knowledge of data warehousing.',
        'skills_required': 'Apache Spark, Hadoop, Kafka, Airflow, Python, Scala, SQL, AWS EMR, Databricks',
        'responsibilities': 'Build data pipelines. Optimize data processing. Design data architecture. Ensure data quality.',
        'benefits': 'Remote work, Learning budget, Stock options, Health coverage',
        'vacancies': 3,
        'is_featured': True
    },
    
    # ===== WEB DEVELOPMENT =====
    {
        'title': 'Frontend Developer',
        'company_name': 'Creative Web Studio',
        'description': 'Create stunning user interfaces with modern frontend technologies. Focus on responsive design and user experience.',
        'location': 'Mumbai, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹6,00,000 - ₹12,00,000 per annum',
        'requirements': 'Strong proficiency in HTML, CSS, and JavaScript. Experience with React or Vue.js.',
        'skills_required': 'React, Vue.js, HTML5, CSS3, SASS, JavaScript, TypeScript, Responsive Design',
        'responsibilities': 'Build responsive UIs. Collaborate with designers. Optimize for performance. Write clean code.',
        'benefits': 'Flexible hours, Remote work option, Learning allowance',
        'vacancies': 4,
        'is_featured': False
    },
    {
        'title': 'WordPress Developer',
        'company_name': 'Digital Agency Pro',
        'description': 'Develop custom WordPress themes and plugins for client websites. Create responsive and SEO-friendly websites.',
        'location': 'Delhi, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹4,00,000 - ₹8,00,000 per annum',
        'requirements': 'Experience with WordPress development. Knowledge of PHP. Understanding of SEO best practices.',
        'skills_required': 'WordPress, PHP, MySQL, HTML, CSS, JavaScript, Elementor, WooCommerce',
        'responsibilities': 'Develop WordPress sites. Create custom themes. Optimize for SEO. Maintain existing sites.',
        'benefits': 'Flexible timing, Health insurance, Performance bonus',
        'vacancies': 3,
        'is_featured': False
    },
    {
        'title': 'UI/UX Designer',
        'company_name': 'DesignFirst Agency',
        'description': 'Design beautiful and intuitive user interfaces. Conduct user research and create wireframes, prototypes, and final designs.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹7,00,000 - ₹14,00,000 per annum',
        'requirements': 'Portfolio showcasing UI/UX work. Proficiency in design tools. Understanding of user-centered design.',
        'skills_required': 'Figma, Adobe XD, Sketch, Wireframing, Prototyping, User Research, Design Systems',
        'responsibilities': 'Create UI designs. Conduct user research. Build prototypes. Collaborate with developers.',
        'benefits': 'Design tool licenses, Learning budget, Flexible hours',
        'vacancies': 2,
        'is_featured': False
    },
    
    # ===== QUALITY ASSURANCE =====
    {
        'title': 'QA Engineer',
        'company_name': 'Quality Tech Labs',
        'description': 'Ensure software quality through comprehensive testing. Create test plans, execute tests, and report bugs.',
        'location': 'Noida, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹5,00,000 - ₹10,00,000 per annum',
        'requirements': 'Experience with manual and automated testing. Knowledge of testing methodologies. Attention to detail.',
        'skills_required': 'Selenium, TestNG, JIRA, Postman, SQL, API Testing, Manual Testing, Agile',
        'responsibilities': 'Write test cases. Execute tests. Report bugs. Participate in agile ceremonies.',
        'benefits': 'Health insurance, Learning opportunities, Flexible timing',
        'vacancies': 5,
        'is_featured': False
    },
    {
        'title': 'Automation Test Engineer',
        'company_name': 'AutoTest Solutions',
        'description': 'Build and maintain automated test frameworks. Increase test coverage and reduce manual testing effort.',
        'location': 'Hyderabad, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹10,00,000 - ₹18,00,000 per annum',
        'requirements': 'Strong programming skills. Experience with automation frameworks. CI/CD integration experience.',
        'skills_required': 'Selenium, Python, Java, Cypress, Jest, Jenkins, Git, API Automation',
        'responsibilities': 'Build automation frameworks. Write automated tests. Integrate with CI/CD. Mentor team members.',
        'benefits': 'Remote work, Annual bonus, Health coverage, Learning budget',
        'vacancies': 3,
        'is_featured': False
    },
    
    # ===== PROJECT MANAGEMENT & BUSINESS ANALYSIS =====
    {
        'title': 'Technical Project Manager',
        'company_name': 'Agile Projects Inc',
        'description': 'Lead technical projects from inception to delivery. Manage cross-functional teams and ensure timely delivery.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '5-10',
        'salary': '₹20,00,000 - ₹35,00,000 per annum',
        'requirements': 'PMP/Scrum certification preferred. Experience managing software projects. Strong leadership skills.',
        'skills_required': 'Agile, Scrum, JIRA, Confluence, Risk Management, Stakeholder Management, Technical Knowledge',
        'responsibilities': 'Plan and track projects. Manage resources. Handle stakeholder communication. Mitigate risks.',
        'benefits': 'Leadership training, Health insurance, Performance bonus, Stock options',
        'vacancies': 2,
        'is_featured': False
    },
    {
        'title': 'Business Analyst',
        'company_name': 'Tech Consulting Group',
        'description': 'Bridge the gap between business and technology. Gather requirements, analyze processes, and propose solutions.',
        'location': 'Pune, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹10,00,000 - ₹18,00,000 per annum',
        'requirements': 'Experience in requirements gathering. Strong analytical skills. Understanding of SDLC.',
        'skills_required': 'Requirements Analysis, UML, JIRA, Agile, SQL, Process Mapping, Documentation',
        'responsibilities': 'Gather business requirements. Create documentation. Facilitate meetings. Work with dev team.',
        'benefits': 'Flexible hours, Health insurance, Learning opportunities',
        'vacancies': 3,
        'is_featured': False
    },
    {
        'title': 'Scrum Master',
        'company_name': 'Agile Transformation Co',
        'description': 'Facilitate agile practices across development teams. Coach teams on Scrum methodology and remove impediments.',
        'location': 'Chennai, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹12,00,000 - ₹22,00,000 per annum',
        'requirements': 'CSM/PSM certification. Experience as Scrum Master. Strong facilitation skills.',
        'skills_required': 'Scrum, Agile, JIRA, Confluence, Coaching, Facilitation, Conflict Resolution',
        'responsibilities': 'Facilitate scrum events. Coach team members. Remove impediments. Track metrics.',
        'benefits': 'Certification support, Remote work, Health coverage',
        'vacancies': 2,
        'is_featured': False
    },
    
    # ===== NETWORKING & INFRASTRUCTURE =====
    {
        'title': 'Network Engineer',
        'company_name': 'NetConnect Solutions',
        'description': 'Design, implement, and maintain network infrastructure. Ensure high availability and security of network systems.',
        'location': 'Delhi NCR, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹10,00,000 - ₹18,00,000 per annum',
        'requirements': 'CCNA/CCNP certification. Experience with enterprise networking. Strong troubleshooting skills.',
        'skills_required': 'Cisco, Juniper, Firewalls, VPN, TCP/IP, BGP, OSPF, Network Security, Wireshark',
        'responsibilities': 'Configure network devices. Monitor network performance. Troubleshoot issues. Implement security.',
        'benefits': 'Certification sponsorship, Health insurance, On-call allowance',
        'vacancies': 3,
        'is_featured': False
    },
    {
        'title': 'System Administrator',
        'company_name': 'IT Infrastructure Corp',
        'description': 'Manage and maintain server infrastructure. Ensure system uptime, security, and performance.',
        'location': 'Mumbai, India',
        'job_type': 'full-time',
        'experience_required': '3-5',
        'salary': '₹8,00,000 - ₹15,00,000 per annum',
        'requirements': 'Experience with Linux and Windows servers. Knowledge of virtualization. Strong scripting skills.',
        'skills_required': 'Linux, Windows Server, VMware, Active Directory, Bash, PowerShell, Backup Solutions',
        'responsibilities': 'Maintain servers. Manage user accounts. Implement backups. Monitor system health.',
        'benefits': 'Health insurance, Shift allowance, Learning budget',
        'vacancies': 3,
        'is_featured': False
    },
    
    # ===== BLOCKCHAIN & EMERGING TECH =====
    {
        'title': 'Blockchain Developer',
        'company_name': 'CryptoTech Labs',
        'description': 'Develop decentralized applications and smart contracts. Work with blockchain platforms like Ethereum and Solana.',
        'location': 'Bangalore, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹12,00,000 - ₹25,00,000 per annum',
        'requirements': 'Experience with blockchain development. Knowledge of smart contracts. Understanding of DeFi.',
        'skills_required': 'Solidity, Ethereum, Web3.js, Smart Contracts, Rust, DeFi, NFTs, JavaScript',
        'responsibilities': 'Develop smart contracts. Build dApps. Audit code for security. Integrate blockchain solutions.',
        'benefits': 'Crypto rewards, Remote work, Learning budget, Stock options',
        'vacancies': 3,
        'is_featured': True
    },
    {
        'title': 'IoT Developer',
        'company_name': 'SmartDevices Inc',
        'description': 'Build IoT solutions connecting hardware and software. Work with sensors, embedded systems, and cloud platforms.',
        'location': 'Hyderabad, India',
        'job_type': 'full-time',
        'experience_required': '1-3',
        'salary': '₹8,00,000 - ₹15,00,000 per annum',
        'requirements': 'Experience with IoT platforms. Knowledge of embedded systems. Programming skills.',
        'skills_required': 'Arduino, Raspberry Pi, MQTT, Python, C/C++, AWS IoT, Sensors, Embedded Systems',
        'responsibilities': 'Develop IoT applications. Integrate sensors. Build dashboards. Ensure connectivity.',
        'benefits': 'Hardware lab access, Learning budget, Health insurance',
        'vacancies': 2,
        'is_featured': False
    },
    
    # ===== SUPPORT & HELPDESK =====
    {
        'title': 'Technical Support Engineer',
        'company_name': 'SupportFirst Solutions',
        'description': 'Provide technical support to customers. Troubleshoot issues and ensure customer satisfaction.',
        'location': 'Gurgaon, India',
        'job_type': 'full-time',
        'experience_required': '0-1',
        'salary': '₹3,50,000 - ₹6,00,000 per annum',
        'requirements': 'Good communication skills. Basic technical knowledge. Customer service orientation.',
        'skills_required': 'Troubleshooting, Windows, Networking Basics, Ticketing Systems, Communication',
        'responsibilities': 'Handle support tickets. Troubleshoot issues. Document solutions. Escalate complex problems.',
        'benefits': 'Shift allowance, Health insurance, Training provided',
        'vacancies': 10,
        'is_featured': False
    },
    {
        'title': 'IT Helpdesk Engineer',
        'company_name': 'Corporate IT Services',
        'description': 'Support internal IT operations. Manage helpdesk tickets, configure hardware, and assist employees with IT issues.',
        'location': 'Noida, India',
        'job_type': 'full-time',
        'experience_required': '0-1',
        'salary': '₹3,00,000 - ₹5,00,000 per annum',
        'requirements': 'Basic IT knowledge. Good communication skills. Willingness to learn.',
        'skills_required': 'Windows, Office 365, Hardware Troubleshooting, Networking Basics, Active Directory',
        'responsibilities': 'Resolve helpdesk tickets. Set up workstations. Manage IT assets. Support employees.',
        'benefits': 'Training programs, Health insurance, Career growth',
        'vacancies': 8,
        'is_featured': False
    },
    
    # ===== INTERNSHIPS =====
    {
        'title': 'Software Development Intern',
        'company_name': 'TechStart Labs',
        'description': 'Join our internship program to gain hands-on experience in software development. Work on real projects with mentorship.',
        'location': 'Bangalore, India',
        'job_type': 'internship',
        'experience_required': '0-1',
        'salary': '₹15,000 - ₹25,000 per month stipend',
        'requirements': 'Currently pursuing B.Tech/M.Tech. Basic programming knowledge. Eagerness to learn.',
        'skills_required': 'Python, Java, JavaScript, Git, Data Structures, Algorithms',
        'responsibilities': 'Work on assigned projects. Learn from mentors. Participate in code reviews.',
        'benefits': 'Mentorship, Certificate, Pre-placement offer possibility',
        'vacancies': 10,
        'is_featured': False
    },
    {
        'title': 'Data Science Intern',
        'company_name': 'Analytics Academy',
        'description': 'Learn data science in a practical environment. Work with real datasets and build ML models under expert guidance.',
        'location': 'Hyderabad, India',
        'job_type': 'internship',
        'experience_required': '0-1',
        'salary': '₹20,000 - ₹30,000 per month stipend',
        'requirements': 'Basic Python and statistics knowledge. Pursuing relevant degree. Interest in ML/AI.',
        'skills_required': 'Python, Pandas, NumPy, Machine Learning Basics, SQL, Statistics',
        'responsibilities': 'Analyze datasets. Build simple models. Create visualizations. Learn from mentors.',
        'benefits': 'Learning resources, Certificate, PPO possibility',
        'vacancies': 5,
        'is_featured': False
    },
    
    # ===== REMOTE JOBS =====
    {
        'title': 'Remote Full Stack Developer',
        'company_name': 'GlobalTech Remote',
        'description': 'Work remotely as a full stack developer for international clients. Build web applications using modern technologies.',
        'location': 'Remote (India)',
        'job_type': 'remote',
        'experience_required': '3-5',
        'salary': '₹18,00,000 - ₹35,00,000 per annum',
        'requirements': 'Excellent communication skills. Self-motivated. Experience working remotely.',
        'skills_required': 'React, Node.js, Python, PostgreSQL, AWS, Docker, Git, Agile',
        'responsibilities': 'Develop full stack features. Collaborate with global team. Write documentation.',
        'benefits': 'Work from anywhere, Flexible hours, Equipment allowance, Annual meetups',
        'vacancies': 5,
        'is_featured': True
    },
    {
        'title': 'Remote DevOps Consultant',
        'company_name': 'Cloud Consulting Partners',
        'description': 'Provide DevOps consulting services remotely to multiple clients. Help organizations adopt DevOps practices.',
        'location': 'Remote (India)',
        'job_type': 'remote',
        'experience_required': '5-10',
        'salary': '₹25,00,000 - ₹50,00,000 per annum',
        'requirements': 'Expert-level DevOps skills. Excellent communication. Consulting experience preferred.',
        'skills_required': 'AWS, Azure, Kubernetes, Terraform, CI/CD, Docker, Consulting, Architecture',
        'responsibilities': 'Consult for clients. Design solutions. Implement automation. Train teams.',
        'benefits': 'Remote work, High compensation, Diverse projects, Flexible schedule',
        'vacancies': 3,
        'is_featured': True
    },
    
    # ===== CONTRACT JOBS =====
    {
        'title': 'Contract Python Developer',
        'company_name': 'Project Solutions Ltd',
        'description': '6-month contract position for an experienced Python developer to work on a data processing project.',
        'location': 'Bangalore, India',
        'job_type': 'contract',
        'experience_required': '3-5',
        'salary': '₹1,50,000 - ₹2,00,000 per month',
        'requirements': 'Strong Python skills. Available for 6-month contract. Immediate joining preferred.',
        'skills_required': 'Python, Django, FastAPI, PostgreSQL, Docker, AWS',
        'responsibilities': 'Develop backend services. Write clean code. Meet project deadlines.',
        'benefits': 'Competitive pay, Extension possibility, Flexible hours',
        'vacancies': 2,
        'is_featured': False
    },
    {
        'title': 'Contract UI Developer',
        'company_name': 'Design Agency Pro',
        'description': '3-month contract for a skilled UI developer to build responsive web interfaces for client projects.',
        'location': 'Mumbai, India',
        'job_type': 'contract',
        'experience_required': '1-3',
        'salary': '₹80,000 - ₹1,20,000 per month',
        'requirements': 'Portfolio of UI work. Available for 3-month contract. Quick learner.',
        'skills_required': 'React, HTML5, CSS3, JavaScript, Responsive Design, Git',
        'responsibilities': 'Build user interfaces. Collaborate with designers. Ensure cross-browser compatibility.',
        'benefits': 'Flexible hours, Portfolio building, Extension possibility',
        'vacancies': 3,
        'is_featured': False
    }
]


def add_jobs():
    """Add all IT jobs to the database."""
    # Calculate application deadline (30 days from now)
    default_deadline = date.today() + timedelta(days=30)
    
    jobs_created = 0
    jobs_updated = 0
    
    for job_data in IT_JOBS:
        # Set application deadline if not provided
        if 'application_deadline' not in job_data:
            job_data['application_deadline'] = default_deadline
        
        # Check if job with same title and company exists
        existing_job = Job.objects.filter(
            title=job_data['title'],
            company_name=job_data['company_name']
        ).first()
        
        if existing_job:
            # Update existing job
            for key, value in job_data.items():
                setattr(existing_job, key, value)
            existing_job.save()
            jobs_updated += 1
            print(f"Updated: {job_data['title']} at {job_data['company_name']}")
        else:
            # Create new job
            Job.objects.create(**job_data)
            jobs_created += 1
            print(f"Created: {job_data['title']} at {job_data['company_name']}")
    
    print(f"\n{'='*50}")
    print(f"Summary: {jobs_created} jobs created, {jobs_updated} jobs updated")
    print(f"Total jobs in database: {Job.objects.count()}")


if __name__ == '__main__':
    print("Adding IT jobs to the database...")
    print("="*50)
    add_jobs()
    print("\nDone!")
