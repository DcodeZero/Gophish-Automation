import os
import base64
import json
from gophish import Gophish
from gophish.models import Template, Campaign, Group, SMTP, Page

# Load configuration from the config.json file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load configuration
config = load_config('config.json')

# Define your GoPhish API key and server URL from the configuration
API_KEY = config['api_key']
HOST = config['host']

# Initialize the GoPhish API client
api = Gophish(API_KEY, host=HOST, verify=False)

# Function to read templates from a directory
def read_templates(directory):
    templates = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                templates.append(file.read())
    return templates

# Function to decode base64 content
def decode_base64(encoded_content):
    try:
        return base64.b64decode(encoded_content).decode('utf-8')
    except Exception as e:
        print(f"Failed to decode base64 content: {e}")
        return None

# Function to detect if content is base64 or plain text
def detect_content_type(content, is_base64):
    if is_base64:
        return decode_base64(content)
    else:
        return content

# Function to create email templates in GoPhish
def create_templates(api, templates_content):
    template_ids = []
    for content in templates_content:
        try:
            # Split the content into components
            lines = content.split('\n')
            subject = lines[0].replace('Subject:', '').strip()
            html_content = lines[1].replace('HTML:', '').strip()
            
            # Detect content type
            processed_html = detect_content_type(html_content, config['template']['is_base64'])
            
            # Create the email template with the subject as its name
            template = Template(
                name=subject,
                subject=subject,
                text="",  # Assuming no plain text provided, or you can adjust as needed
                html=processed_html
            )
            created_template = api.templates.post(template)
            if created_template.id:
                print(f"Template created successfully: {created_template}")
                template_ids.append(created_template)
            else:
                print(f"Failed to create template: {created_template}")
        except Exception as e:
            print(f"Error parsing template content: {e}")
    return template_ids

# Function to find an existing group by name
def find_group_by_name(api, name):
    groups = api.groups.get()
    for group in groups:
        if group.name == name:
            return group
    return None

# Function to create or get a group
def get_or_create_group(api, config):
    group = find_group_by_name(api, config['group']['name'])
    if group:
        print(f"Group already exists: {group}")
        return group.id
    else:
        group = Group(
            name=config['group']['name'],
            targets=config['group']['targets']
        )
        created_group = api.groups.post(group)
        if created_group.id:
            print(f"Group created successfully: {created_group}")
            return created_group.id
        else:
            print(f"Failed to create group: {created_group}")
            return None

# Function to find an existing sending profile by name
def find_sending_profile_by_name(api, name):
    sending_profiles = api.smtp.get()
    for profile in sending_profiles:
        if profile.name == name:
            return profile
    return None

# Function to create or get a sending profile
def get_or_create_sending_profile(api, config):
    sending_profile = find_sending_profile_by_name(api, config['smtp']['name'])
    if sending_profile:
        print(f"Sending profile already exists: {sending_profile}")
        return sending_profile.id
    else:
        smtp = SMTP(
            name=config['smtp']['name'],
            interface_type="SMTP",
            host=config['smtp']['host'],
            from_address=config['smtp']['from_address'],
            username=config['smtp']['username'],
            password=config['smtp']['password'],
            ignore_cert_errors=config['smtp']['ignore_cert_errors']
        )
        created_smtp = api.smtp.post(smtp)
        if created_smtp.id:
            print(f"Sending profile created successfully: {created_smtp}")
            return created_smtp.id
        else:
            print(f"Failed to create sending profile: {created_smtp}")
            return None

# Function to find an existing landing page by name
def find_landing_page_by_name(api, name):
    landing_pages = api.pages.get()
    for page in landing_pages:
        if page.name == name:
            return page
    return None

# Function to create or get a landing page
def get_or_create_landing_page(api, config):
    landing_page = find_landing_page_by_name(api, config['landing_page']['name'])
    if landing_page:
        print(f"Landing page already exists: {landing_page}")
        return landing_page.id
    else:
        html_content = config['landing_page']['html']
        processed_html = decode_base64(html_content) if config['landing_page']['is_base64'] else html_content
        
        page = Page(
            name=config['landing_page']['name'],
            html=processed_html,
            capture_credentials=config['landing_page']['capture_credentials'],
            capture_passwords=config['landing_page']['capture_passwords']
        )
        created_page = api.pages.post(page)
        if created_page.id:
            print(f"Landing page created successfully: {created_page}")
            return created_page.id
        else:
            print(f"Failed to create landing page: {created_page}")
            return None

# Get or create resources
recipients_group_id = get_or_create_group(api, config)
smtp_id = get_or_create_sending_profile(api, config)
landing_page_id = get_or_create_landing_page(api, config)

# Function to create a campaign
def create_campaign(api, template, recipients_group_id, smtp_id, landing_page_id):
    try:
        group = api.groups.get(recipients_group_id)
        smtp = api.smtp.get(smtp_id)
        page = api.pages.get(landing_page_id)
        
        campaign = Campaign(
            name=f"Campaign with template {template.subject}",
            template=template,
            page=page,
            smtp=smtp,
            groups=[group],
            url="http://example.com"  # Change to the actual URL if needed
        )
        created_campaign = api.campaigns.post(campaign)
        if created_campaign.id:
            print(f"Campaign created successfully with template {template.subject}")
        else:
            print(f"Failed to create campaign: {created_campaign}")
    except Exception as e:
        print(f"An error occurred while creating the campaign: {e}")

# Create campaigns using the templates
for template in create_templates(api, read_templates('templates/')):
    create_campaign(api, template, recipients_group_id, smtp_id, landing_page_id)
