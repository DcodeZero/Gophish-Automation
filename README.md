![Link Name](https://th.bing.com/th/id/OIG3.7FdWIq65gKPpyX3G6irw?w=1024&h=1024&rs=1&pid=ImgDetMain)


# GO Auto Phish

This project automates the creation and management of phishing campaigns using the GoPhish API. The script handles template management, sending profiles, and campaign creation with advanced features such as error handling, custom headers, and rate limiting.

## Table of Contents

- [File Structure](#file-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Features](#features)
- [Logging](#logging)
- [License](#license)

## File Structure

    /GoPhish-Automation/
    │
    ├── /templates/
    │ ├── template1.txt
    │ ├── template2.txt
    │ └── template3.txt
    │
    ├── /logs/
    │ └── phishing_campaign.log
    │
    ├── config.json
    │
    └── configauto.py

- **/templates/**: Contains the email templates in `.txt` format.
- **/logs/**: Stores the log file `phishing_campaign.log`.
- **config.json**: Configuration file for the script.
- **configauto.py**: Main Python script for automating the campaign.

## Prerequisites

- Python 3.x
- GoPhish server set up and running
- API key for GoPhish

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/PhishingCampaign.git
   cd PhishingCampaign
   ```
2. Install the required Python packages:
   ``` bash
   pip install gophish
   ```
3. Set up your GoPhish server and obtain the API key.

4. Configuration

   Edit the config.json file with your GoPhish API details, SMTP profiles, group settings, and landing page configuration. The JSON structure should look something like this:

```json
{
  "api_key": "your_api_key_here",
  "host": "https://your_gophish_server_url",
  "template": {
    "is_base64": false,
    "send_all_types": false
  },
  "smtp_profiles": [
    {
      "name": "Profile1",
      "host": "smtp.example.com",
      "from_address": "phish@example.com",
      "username": "user1",
      "password": "password1",
      "ignore_cert_errors": true,
      "headers": [
        {"key": "X-Header", "value": "Foo Bar"}
      ]
    }
  ],
  "group": {
    "name": "Phishing Group",
    "targets": [
      {
        "email": "target1@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    ]
  },
  "landing_page": {
    "name": "Phishing Page",
    "html": "base64_encoded_html_here",
    "is_base64": true,
    "capture_credentials": true,
    "capture_passwords": true
  }
}
```

### Usage
1 Place your email templates in the templates/ directory. Templates should be .txt files with the following format:

    Subject: Your Subject Here
    HTML: <Base64 or plain HTML content>
2 Run the script:

    python configauto.py

The script will:

    Validate and decode Base64 content if applicable.
    Create or update email templates in GoPhish.
    Set up sending profiles, groups, and landing pages.
    Create and send campaigns with rate limiting.
    Log the process in phishing_campaign.log.

Features

    Advanced Error Handling and Logging: Detailed logging and error handling for troubleshooting.
    Dynamic Template Management: Supports both Base64 and plain text templates.
    Custom Headers: Allows adding custom headers to emails.
    Rate Limiting: Implements delays between sending emails from different SMTP profiles.
    Reply Email Handling: Sends a reply email to a specified recipient if the email is delivered or not.

Logging

    Logs are stored in /logs/phishing_campaign.log. The log file includes detailed information about the script's execution, including errors, successful operations, and campaign details.
    License

This project is licensed under the MIT License. See the LICENSE file for details.

    This `README.md` should provide clear instructions on how to set up and use the project, along with an overview of the key features and capabilities of the script.

