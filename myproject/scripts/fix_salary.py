from myapp.models import Job

jobs = Job.objects.all()
for job in jobs:
    if job.salary:
        # Replace problematic characters
        new_salary = job.salary.replace('₹', 'INR ').replace('???', 'INR ')
        if new_salary != job.salary:
            job.salary = new_salary
            job.save()
            print(f'Fixed: {job.title}')

print(f'Total jobs: {Job.objects.count()}')
