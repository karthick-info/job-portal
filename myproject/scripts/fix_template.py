
import os
import re

file_path = r'c:\Users\DELL\Desktop\job portal\myproject\myapp\templates\myapp\job-listings.html'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix job_type syntax
    content = content.replace("job_type=='full-time'", "job_type == 'full-time'")
    content = content.replace("job_type=='part-time'", "job_type == 'part-time'")
    content = content.replace("job_type=='contract'", "job_type == 'contract'")
    content = content.replace("job_type=='internship'", "job_type == 'internship'")
    content = content.replace("job_type=='remote'", "job_type == 'remote'")
    
    # Fix experience syntax
    content = content.replace("experience=='0-1'", "experience == '0-1'")
    content = content.replace("experience=='1-3'", "experience == '1-3'")
    content = content.replace("experience=='3-5'", "experience == '3-5'")
    content = content.replace("experience=='5-10'", "experience == '5-10'")
    content = content.replace("experience=='10+'", "experience == '10+'")
    
    # Fix split company_name tag using regex to handle newlines
    # Matches {{ job.company_name [newline/spaces] }}
    content = re.sub(r'\{\{\s*job\.company_name\s*\}\}', '{{ job.company_name }}', content, flags=re.DOTALL)
    
    # Brute force replace of the specific split pattern observed
    broken_tag = '{{ job.company_name\n              }}'
    content = content.replace(broken_tag, '{{ job.company_name }}')

    # Also handle the one with spaces if indentation differs
    broken_tag_2 = '{{ job.company_name\r\n              }}'
    content = content.replace(broken_tag_2, '{{ job.company_name }}')


    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully updated job-listings.html with all fixes")
    else:
        print("No changes needed or patterns not found.")

except Exception as e:
    print(f"Error: {e}")
