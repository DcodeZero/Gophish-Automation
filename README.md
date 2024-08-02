![Link Name](https://th.bing.com/th/id/OIG3.7FdWIq65gKPpyX3G6irw?w=1024&h=1024&rs=1&pid=ImgDetMain)


This Python script automates the creation of Gophish campaigns by reading email templates and landing page configurations from files. It uses the Gophish API to handle various components of phishing campaigns.
Features

    Read Templates: Load email templates from .txt files.
    Create/Update Resources: Automatically create or update email templates, landing pages, groups, and SMTP profiles.
    Base64 Handling: Supports both base64 encoded and plain HTML content for templates and landing pages.
    Error Handling: Handles errors gracefully during the creation and updating process.

Prerequisites

    Python 3.x
    Gophish server running and accessible
    gophish Python library installed (pip install gophish)

Configuration
config.json

Create a config.json file to store your Gophish API credentials and other configuration details. 

Template File Format

Place your template files in a templates/ directory. Each .txt file should follow this format:

```
Subject: <This will be the real title for email>
HTML: <base64 html goes here>
```

Example `template1.txt`

```
Subject: Invoice #12345 - Payment Due
HTML: PGgxPlZlcmlmaWNhdGlvbiBQYWdlPC9oMT48cD5QbGVhc2UgZW50ZXIgeW91ciBjcmVkZW50aWFscyB0byB2ZXJpZnkgZGlzY29tbWVudHM8L3A+
```

How It Works

    Load Configuration: The script reads the config.json file for Gophish API credentials and other settings.
    Read Templates: The script reads and processes the .txt files from the templates/ directory.
    Create or Update Resources:
        Groups: Create or retrieve an existing group.
        SMTP Profiles: Create or retrieve an existing SMTP profile.
        Landing Pages: Create or retrieve a landing page, decoding base64 if required.
        Templates: Create email templates with either base64 or plain HTML.
    Create Campaigns: Generate campaigns using the created templates and resources.

Troubleshooting

    Errors with Base64 Decoding: Ensure your HTML content is correctly base64 encoded.
    API Errors: Check your API credentials and Gophish server URL.
