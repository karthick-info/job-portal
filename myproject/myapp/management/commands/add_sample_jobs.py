from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import UserMaster, Company, Job
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Add sample job listings to the database'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Adding sample job listings...')
        
        try:
            with transaction.atomic():
                # Create sample companies first
                companies_data = [
                    {
                        'email': 'hr@techcorp.com',
                        'company_name': 'TechCorp Solutions',
                        'firstname': 'Sarah',
                        'lastname': 'Johnson',
                        'city': 'San Francisco',
                        'state': 'California'
                    },
                    {
                        'email': 'careers@innovatetech.com', 
                        'company_name': 'InnovateTech',
                        'firstname': 'Michael',
                        'lastname': 'Chen',
                        'city': 'New York',
                        'state': 'New York'
                    },
                    {
                        'email': 'jobs@digitalstudio.com',
                        'company_name': 'Digital Studio',
                        'firstname': 'Emily',
                        'lastname': 'Davis',
                        'city': 'Austin',
                        'state': 'Texas'
                    },
                    {
                        'email': 'hiring@cloudtech.com',
                        'company_name': 'CloudTech Systems',
                        'firstname': 'David',
                        'lastname': 'Wilson',
                        'city': 'Seattle',
                        'state': 'Washington'
                    },
                    {
                        'email': 'talent@startuplab.com',
                        'company_name': 'StartupLab',
                        'firstname': 'Lisa',
                        'lastname': 'Brown',
                        'city': 'Boston',
                        'state': 'Massachusetts'
                    }
                ]
                
                companies = []
                for comp_data in companies_data:
                    # Create user account for company
                    user = UserMaster.objects.create(
                        email=comp_data['email'],
                        password='company123',  # Simple password for demo
                        otp=0,
                        role='company',
                        is_active=True,
                        is_verified=True
                    )
                    
                    # Create company profile
                    company = Company.objects.create(
                        user_id=user,
                        firstname=comp_data['firstname'],
                        lastname=comp_data['lastname'],
                        company_name=comp_data['company_name'],
                        city=comp_data['city'],
                        state=comp_data['state'],
                        contact='(555) 123-4567',
                        address=f"123 Business St, {comp_data['city']}, {comp_data['state']}"
                    )
                    companies.append(company)
                
                # Create sample jobs
                jobs_data = [
                    {
                        'title': 'Senior Software Engineer',
                        'description': 'We are looking for an experienced software engineer to join our dynamic team. You will be responsible for developing scalable web applications and working with cutting-edge technologies.',
                        'location': 'San Francisco, CA',
                        'job_type': 'full-time',
                        'experience_required': '3-5',
                        'salary': '$120,000 - $150,000',
                        'skills_required': 'Python, Django, React, PostgreSQL, AWS',
                        'requirements': 'Bachelor\'s degree in Computer Science or related field. 3+ years of experience in web development. Strong problem-solving skills.',
                        'responsibilities': 'Design and develop web applications, collaborate with cross-functional teams, write clean and maintainable code, participate in code reviews.',
                        'benefits': 'Health insurance, 401k matching, flexible work hours, remote work options',
                        'vacancies': 2,
                        'is_featured': True,
                        'company_index': 0
                    },
                    {
                        'title': 'Frontend Developer',
                        'description': 'Join our creative team as a Frontend Developer and help build amazing user experiences. We work with modern frameworks and prioritize clean, responsive design.',
                        'location': 'New York, NY',
                        'job_type': 'full-time',
                        'experience_required': '1-3',
                        'salary': '$80,000 - $100,000',
                        'skills_required': 'JavaScript, React, HTML5, CSS3, TypeScript',
                        'requirements': 'Strong knowledge of modern JavaScript frameworks. Experience with responsive design. Portfolio of previous work required.',
                        'responsibilities': 'Develop user interfaces, optimize applications for speed and scalability, collaborate with designers and backend developers.',
                        'benefits': 'Health insurance, dental coverage, professional development budget, flexible PTO',
                        'vacancies': 1,
                        'is_featured': True,
                        'company_index': 1
                    },
                    {
                        'title': 'UX/UI Designer',
                        'description': 'We\'re seeking a talented UX/UI Designer to create intuitive and visually appealing digital experiences. You\'ll work closely with our product team to design user-centered solutions.',
                        'location': 'Austin, TX',
                        'job_type': 'full-time',
                        'experience_required': '1-3',
                        'salary': '$70,000 - $90,000',
                        'skills_required': 'Figma, Adobe Creative Suite, Sketch, Prototyping, User Research',
                        'requirements': 'Bachelor\'s degree in Design or related field. Strong portfolio demonstrating UX/UI design skills. Experience with design systems.',
                        'responsibilities': 'Create wireframes and prototypes, conduct user research, design user interfaces, collaborate with development teams.',
                        'benefits': 'Creative workspace, design conference budget, health insurance, stock options',
                        'vacancies': 1,
                        'is_featured': False,
                        'company_index': 2
                    },
                    {
                        'title': 'DevOps Engineer',
                        'description': 'Looking for a DevOps Engineer to help streamline our development and deployment processes. You\'ll work with cloud infrastructure and automation tools.',
                        'location': 'Seattle, WA',
                        'job_type': 'full-time',
                        'experience_required': '3-5',
                        'salary': '$110,000 - $140,000',
                        'skills_required': 'AWS, Docker, Kubernetes, Jenkins, Terraform, Linux',
                        'requirements': '3+ years of DevOps experience. Strong knowledge of cloud platforms. Experience with CI/CD pipelines.',
                        'responsibilities': 'Manage cloud infrastructure, automate deployment processes, monitor system performance, ensure security best practices.',
                        'benefits': 'Comprehensive health coverage, retirement plan, learning stipend, remote work flexibility',
                        'vacancies': 1,
                        'is_featured': True,
                        'company_index': 3
                    },
                    {
                        'title': 'Data Scientist',
                        'description': 'Join our data team to extract insights from complex datasets and build predictive models. You\'ll work on exciting projects that drive business decisions.',
                        'location': 'Boston, MA',
                        'job_type': 'full-time',
                        'experience_required': '1-3',
                        'salary': '$90,000 - $120,000',
                        'skills_required': 'Python, R, SQL, Machine Learning, Statistics, Pandas, Scikit-learn',
                        'requirements': 'Master\'s degree in Data Science, Statistics, or related field. Experience with machine learning algorithms. Strong analytical skills.',
                        'responsibilities': 'Analyze large datasets, build predictive models, create data visualizations, present findings to stakeholders.',
                        'benefits': 'Health insurance, professional development, conference attendance, flexible schedule',
                        'vacancies': 2,
                        'is_featured': False,
                        'company_index': 4
                    },
                    {
                        'title': 'Product Manager',
                        'description': 'We\'re looking for a Product Manager to lead product strategy and work with cross-functional teams to deliver exceptional products to our customers.',
                        'location': 'San Francisco, CA',
                        'job_type': 'full-time',
                        'experience_required': '3-5',
                        'salary': '$130,000 - $160,000',
                        'skills_required': 'Product Strategy, Agile, Analytics, User Research, Roadmap Planning',
                        'requirements': '3+ years of product management experience. Strong analytical and communication skills. Experience with agile methodologies.',
                        'responsibilities': 'Define product roadmap, gather requirements, work with engineering teams, analyze product metrics, conduct user research.',
                        'benefits': 'Equity package, health insurance, unlimited PTO, professional development budget',
                        'vacancies': 1,
                        'is_featured': True,
                        'company_index': 0
                    },
                    {
                        'title': 'Marketing Specialist',
                        'description': 'Join our marketing team to help grow our brand and reach new customers. You\'ll work on digital marketing campaigns and content creation.',
                        'location': 'Remote',
                        'job_type': 'full-time',
                        'experience_required': '1-3',
                        'salary': '$60,000 - $80,000',
                        'skills_required': 'Digital Marketing, Content Creation, SEO, Social Media, Google Analytics',
                        'requirements': 'Bachelor\'s degree in Marketing or related field. Experience with digital marketing tools. Creative mindset.',
                        'responsibilities': 'Create marketing campaigns, manage social media, write content, analyze campaign performance, collaborate with design team.',
                        'benefits': 'Remote work, health insurance, marketing tool subscriptions, flexible hours',
                        'vacancies': 1,
                        'is_featured': False,
                        'company_index': 1
                    },
                    {
                        'title': 'Backend Developer',
                        'description': 'We need a skilled Backend Developer to build robust APIs and server-side applications. You\'ll work with modern technologies and scalable architectures.',
                        'location': 'Austin, TX',
                        'job_type': 'full-time',
                        'experience_required': '1-3',
                        'salary': '$85,000 - $110,000',
                        'skills_required': 'Node.js, Python, MongoDB, PostgreSQL, REST APIs, GraphQL',
                        'requirements': '2+ years of backend development experience. Strong knowledge of databases. Experience with API design.',
                        'responsibilities': 'Develop server-side applications, design APIs, optimize database queries, ensure application security.',
                        'benefits': 'Health coverage, 401k matching, learning budget, team outings',
                        'vacancies': 2,
                        'is_featured': False,
                        'company_index': 2
                    },
                    {
                        'title': 'Mobile App Developer',
                        'description': 'Looking for a Mobile App Developer to create amazing mobile experiences. You\'ll work on both iOS and Android applications using modern frameworks.',
                        'location': 'Seattle, WA',
                        'job_type': 'contract',
                        'experience_required': '1-3',
                        'salary': '$70 - $90 per hour',
                        'skills_required': 'React Native, Flutter, iOS, Android, JavaScript, Dart',
                        'requirements': 'Experience with cross-platform mobile development. Published apps in app stores preferred. Strong UI/UX sense.',
                        'responsibilities': 'Develop mobile applications, optimize app performance, work with designers, test on multiple devices.',
                        'benefits': 'Flexible contract terms, remote work options, competitive hourly rate',
                        'vacancies': 1,
                        'is_featured': False,
                        'company_index': 3
                    },
                    {
                        'title': 'Cybersecurity Analyst',
                        'description': 'Join our security team to protect our systems and data. You\'ll monitor threats, implement security measures, and respond to incidents.',
                        'location': 'Boston, MA',
                        'job_type': 'full-time',
                        'experience_required': '3-5',
                        'salary': '$95,000 - $125,000',
                        'skills_required': 'Network Security, Incident Response, SIEM, Penetration Testing, Risk Assessment',
                        'requirements': 'Bachelor\'s degree in Cybersecurity or related field. Security certifications preferred. Experience with security tools.',
                        'responsibilities': 'Monitor security events, conduct risk assessments, implement security policies, respond to incidents.',
                        'benefits': 'Security training budget, health insurance, certification reimbursement, flexible work',
                        'vacancies': 1,
                        'is_featured': False,
                        'company_index': 4
                    }
                ]
                
                jobs_created = 0
                for job_data in jobs_data:
                    company = companies[job_data['company_index']]
                    
                    # Set application deadline (30 days from now)
                    deadline = date.today() + timedelta(days=30)
                    
                    Job.objects.create(
                        company=company,
                        title=job_data['title'],
                        company_name=company.company_name,
                        description=job_data['description'],
                        location=job_data['location'],
                        job_type=job_data['job_type'],
                        experience_required=job_data['experience_required'],
                        salary=job_data['salary'],
                        requirements=job_data['requirements'],
                        skills_required=job_data['skills_required'],
                        responsibilities=job_data['responsibilities'],
                        benefits=job_data['benefits'],
                        vacancies=job_data['vacancies'],
                        application_deadline=deadline,
                        is_active=True,
                        is_featured=job_data['is_featured']
                    )
                    jobs_created += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Successfully created sample data!\n'
                        f'📊 Summary:\n'
                        f'  - {len(companies)} companies created\n'
                        f'  - {jobs_created} job listings created\n'
                        f'  - {sum(1 for job in jobs_data if job["is_featured"])} featured jobs\n'
                        f'\n🎉 Your website now has sample job listings!'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {str(e)}')
            )
            raise