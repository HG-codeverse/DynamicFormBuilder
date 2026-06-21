DynamicFormBuilder

A Flask-based Dynamic Form Builder that allows users to create custom forms, add fields dynamically, collect responses, export data, and share forms using public links and QR codes.

Features
Form Management
Create forms with title and description
View all forms from a central dashboard
Duplicate existing forms
Delete forms
Stop and resume form submissions
Dynamic Form Builder
Add fields dynamically
Delete fields
Supported field types:
Text
Email
Number
Textarea
Dropdown
Radio Buttons
Checkboxes
Mark fields as required
Public Form Sharing
Generate public form links
Share forms without exposing admin controls
QR Code generation for easy mobile access
Response Collection
Submit responses through public forms
Store responses in SQLite database
View collected responses
Export responses as CSV
Database
SQLite database backend
Forms table
Fields table
Responses table
Tech Stack
Python
Flask
SQLite
HTML
CSS
Jinja2 Templates
QRCode
Pillow
Project Structure
DynamicFormBuilder/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── dashboard.html
│   ├── create_form.html
│   ├── builder.html
│   ├── preview.html
│   ├── public_form.html
│   ├── responses.html
│   └── success.html
│
└── static/


Main Workflow
Create a new form
Add fields using Form Builder
Copy public link or QR code
Share with users
Collect responses
View responses
Export responses as CSV
Future Improvements
User authentication
Edit existing fields
Edit form details
Response analytics dashboard
PDF export
Email notifications
Custom themes




