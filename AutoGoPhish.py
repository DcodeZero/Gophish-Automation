import os
import base64
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from gophish import Gophish
from gophish.models import Template, Campaign, Group, SMTP, Page

# Configure logging
logging.basicConfig(filename='phishing_campaign.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s')

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

# Function to decode base64 content
def decode_base64(encoded_content):
    try:
        return base64.b64decode(encoded_content).decode('utf-8')
    except Exception as e:
        logging.error(f"Failed to decode base64 content: {e}")
        return None

# Function to check if content is valid base64
def is_base64_encoded(content):
    try:
        base64.b64decode(content, validate=True)
        return True
    except Exception:
        return False

# Function to process template content
def process_template_content(content, is_base64):
    lines = content.split('\n')
    if len(lines) < 2:
        raise ValueError("Template content is missing required lines.")
    subject = lines[0].replace('Subject:', '').strip()
    html_content = lines[1].replace('HTML:', '').strip()
    if is_base64:
        return subject, decode_base64(html_content)
    else:
        if is_base64_encoded(html_content):
            logging.info(f"Skipping base64 encoded template: {subject}")
            return None, None
        return subject, html_content

# Function to create or update email templates in GoPhish
def create_or_update_templates(api, directory, is_base64):
    template_ids = []
    existing_templates = {template.name: template for template in api.templates.get()}

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), 'r') as file:
                content = file.read()
                try:
                    subject, html_content = process_template_content(content, is_base64)
                    
                    if html_content is None:
                        # Skip invalid or unwanted template
                        continue

                    if subject in existing_templates:
                        # Update existing template
                        template = existing_templates[subject]
                        template.html = html_content
                        updated_template = api.templates.put(template)
                        if updated_template.id:
                            logging.info(f"Template updated successfully: {updated_template}")
                            template_ids.append(updated_template)
                        else:
                            logging.error(f"Failed to update template: {updated_template}")
                    else:
                        # Create new template
                        template = Template(
                            name=subject,
                            subject=subject,
                            text="",  # Assuming no plain text provided, or you can adjust as needed
                            html=html_content
                        )
                        created_template = api.templates.post(template)
                        if created_template.id:
                            logging.info(f"Template created successfully: {created_template}")
                            template_ids.append(created_template)
                        else:
                            logging.error(f"Failed to create template: {created_template}")

                except Exception as e:
                    logging.error(f"Error processing template file {filename}: {e}")
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
        logging.info(f"Group already exists: {group}")
        return group.id
    else:
        group = Group(
            name=config['group']['name'],
            targets=config['group']['targets']
        )
        created_group = api.groups.post(group)
        if created_group.id:
            logging.info(f"Group created successfully: {created_group}")
            return created_group.id
        else:
            logging.error(f"Failed to create group: {created_group}")
            return None

# Function to find an existing sending profile by name
def find_sending_profile_by_name(api, name):
    sending_profiles = api.smtp.get()
    for profile in sending_profiles:
        if profile.name == name:
            return profile
    return None

# Function to create or get a sending profile
def get_or_create_sending_profile(api, profile_config):
    sending_profile = find_sending_profile_by_name(api, profile_config['name'])
    if sending_profile:
        logging.info(f"Sending profile already exists: {sending_profile}")
        return sending_profile.id
    else:
        smtp = SMTP(
            name=profile_config['name'],
            interface_type="SMTP",
            host=profile_config['host'],
            from_address=profile_config['from_address'],
            username=profile_config['username'],
            password=profile_config['password'],
            ignore_cert_errors=profile_config['ignore_cert_errors'],
            headers=profile_config.get('headers', [])  # Add custom headers
        )
        created_smtp = api.smtp.post(smtp)
        if created_smtp.id:
            logging.info(f"Sending profile created successfully: {created_smtp}")
            return created_smtp.id
        else:
            logging.error(f"Failed to create sending profile: {created_smtp}")
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
        logging.info(f"Landing page already exists: {landing_page}")
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
            logging.info(f"Landing page created successfully: {created_page}")
            return created_page.id
        else:
            logging.error(f"Failed to create landing page: {created_page}")
            return None

# Get or create resources
recipients_group_id = get_or_create_group(api, config)
smtp_ids = [get_or_create_sending_profile(api, profile) for profile in config['smtp_profiles']]
landing_page_id = get_or_create_landing_page(api, config)

# Function to send a reply email
def send_reply_email(smtp_details, to_address, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_details['from_address']
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_details['host'], 587)
        server.starttls()
        server.login(smtp_details['username'], smtp_details['password'])
        text = msg.as_string()
        server.sendmail(smtp_details['from_address'], to_address, text)
        server.quit()

        logging.info(f"Reply email sent to {to_address} with subject '{subject}'")
    except Exception as e:
        logging.error(f"Failed to send reply email: {e}")

# Function to create a campaign
def create_campaign(api, template, recipients_group_id, smtp_ids, landing_page_id):
    try:
        group = api.groups.get(recipients_group_id)
        page = api.pages.get(landing_page_id)
        
        for smtp_id in smtp_ids:
            smtp = api.smtp.get(smtp_id)
            campaign = Campaign(
                name=f"Campaign with template {template.subject}",
                template=template,
                page=page,
                smtp=smtp,
                groups=[group],
                url="https://example.com"  # Change to the actual URL if needed
            )
            created_campaign = api.campaigns.post(campaign)
            if created_campaign.id:
                logging.info(f"Campaign created successfully with template {template.subject}")

                # Send a reply email after the campaign is sent
                recipient_email = config['recipient_email']
                reply_subject = f"Re: {template.subject}"
                reply_body = "This is a reply email confirming the campaign was sent."
                send_reply_email({
                    'from_address': smtp.from_address,
                    'host': smtp.host,
                    'username': smtp.username,
                    'password': smtp.password,
                }, recipient_email, reply_subject, reply_body)

                # Rate limiting: Wait for 2-3 minutes before sending the next campaign
                time.sleep(120)  # 2-minute delay

            else:
                logging.error(f"Failed to create campaign: {created_campaign}")

    except Exception as e:
        logging.error(f"An error occurred while creating the campaign: {e}")

# Create campaigns using the templates
for template in create_or_update_templates(api, 'templates/', config['template']['is_base64']):
    create_campaign(api, template, recipients_group_id, smtp_ids, landing_page_id)
