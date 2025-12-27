from django.core.management.base import BaseCommand
from django.db import transaction
from myapp.models import (
    UserMaster, 
    Candidate, 
    Company, 
    Job, 
    JobApplication, 
    SavedJob, 
    JobAlert
)

class Command(BaseCommand):
    help = 'Clear all user data from database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL user data from the database!\n'
                    'Run with --confirm flag to proceed:\n'
                    'python manage.py clear_all_data --confirm'
                )
            )
            return

        self.stdout.write('🗑️  Starting data cleanup...')
        
        try:
            with transaction.atomic():
                # Delete in order to respect foreign key constraints
                
                # 1. Delete job-related data first
                job_alerts_count = JobAlert.objects.count()
                JobAlert.objects.all().delete()
                self.stdout.write(f'✅ Deleted {job_alerts_count} job alerts')
                
                saved_jobs_count = SavedJob.objects.count()
                SavedJob.objects.all().delete()
                self.stdout.write(f'✅ Deleted {saved_jobs_count} saved jobs')
                
                applications_count = JobApplication.objects.count()
                JobApplication.objects.all().delete()
                self.stdout.write(f'✅ Deleted {applications_count} job applications')
                
                jobs_count = Job.objects.count()
                Job.objects.all().delete()
                self.stdout.write(f'✅ Deleted {jobs_count} jobs')
                
                # 2. Delete user profiles
                candidates_count = Candidate.objects.count()
                Candidate.objects.all().delete()
                self.stdout.write(f'✅ Deleted {candidates_count} candidate profiles')
                
                companies_count = Company.objects.count()
                Company.objects.all().delete()
                self.stdout.write(f'✅ Deleted {companies_count} company profiles')
                
                # 3. Finally delete user accounts
                users_count = UserMaster.objects.count()
                UserMaster.objects.all().delete()
                self.stdout.write(f'✅ Deleted {users_count} user accounts')
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Successfully cleared all data!\n'
                    f'Total records deleted:\n'
                    f'  - {users_count} users\n'
                    f'  - {candidates_count} candidates\n'
                    f'  - {companies_count} companies\n'
                    f'  - {jobs_count} jobs\n'
                    f'  - {applications_count} applications\n'
                    f'  - {saved_jobs_count} saved jobs\n'
                    f'  - {job_alerts_count} job alerts\n'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error clearing data: {str(e)}')
            )
            raise