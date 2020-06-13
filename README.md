# Xero-Django
Integrating Xero Python SDK with Django Framework

Sample Django Application Integrating https://github.com/XeroAPI/xero-python New Xero Python SDK.

# Application Flow
1. pythona manage.py runserver
2. http://localhost:8000/login  (This will check for oauth2 token availablity if not redirects to Xero Login Page
3. Input your login credential
4. Redirects you to Invoice Listing Page
5. Click on "Create Invoice" menu to create invoices (Invoice details are static)
6. Click on Logout this wil lead you to your xero login page again

# Note
Have used Free Account Client-ID & Client-Secret
Please create your own Public OAuth2.0 App and get your Client-ID & Secret

