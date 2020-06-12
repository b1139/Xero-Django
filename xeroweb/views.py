import traceback
import datetime
from decimal import Decimal

from dateutil import tz
from django.shortcuts import render, redirect

# Create your views here.
# configure xero-python sdk client
from xero_python.accounting import AccountingApi, Invoice, Contact, Address, ContactGroup, ContactPerson, Phone, \
    CurrencyCode, LineAmountTypes, LineItem, Invoices
from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from authlib.integrations.django_client import OAuth
from xero_python.api_client.serializer import serialize_model
from xero_python.identity import IdentityApi

api_client = ApiClient(
    Configuration(
        debug=True,
        oauth2_token=OAuth2Token(
            client_id="36AC9E68979B468E971269C49614670E", # Should be changed
            client_secret="SqovsQTXLe2oohytnzZQkTqzowCac9MypcoPc40GD0Y8Wh6Z"  # Should be changed
        ),
    ),
    pool_threads=1,
)

oauth = OAuth()
xero = oauth.register(
    name="xero",
    version="2",
    client_id="36AC9E68979B468E971269C49614670E",  # Should be changed
    client_secret="SqovsQTXLe2oohytnzZQkTqzowCac9MypcoPc40GD0Y8Wh6Z", # Should be changed
    endpoint_url="https://api.xero.com/",
    authorize_url="https://login.xero.com/identity/connect/authorize",
    access_token_url="https://identity.xero.com/connect/token",
    refresh_token_url="https://identity.xero.com/connect/token",
    # scope="offline_access openid profile email",
    scope="offline_access openid profile email accounting.transactions "
          "accounting.transactions.read accounting.reports.read "
          "accounting.journals.read accounting.settings accounting.settings.read "
          "accounting.contacts accounting.contacts.read accounting.attachments "
          "accounting.attachments.read assets projects",
)

token_details = {'token': None,
                 'modified': True}


@api_client.oauth2_token_getter
def obtain_xero_oauth2_token():
    return token_details["token"]


@api_client.oauth2_token_saver
def store_xero_oauth2_token(token):
    token_details["token"] = token
    token_details['modified'] = True


def xero_token_required(function):
    def decorator(*args, **kwargs):
        xero_token = obtain_xero_oauth2_token()
        if not xero_token:
            print(xero_token)
            print("Re login ")
            return redirect("/login")

        return function(*args, **kwargs)

    return decorator

@xero_token_required
def index(request):
    try:
        print(" COmes here home")
        context = {'title': 'Xero|Invoices'}
        # return render(request, template_name='code.html', context=context)
        # api_client.refresh_oauth2_token()
        return get_invoices(request)
    except Exception as e:
        print(e)
        # return redirect("login")

@xero_token_required
def get_invoices(request):
    xero_tenant_id = get_xero_tenant_id()
    print("Tenent Id")
    print(xero_tenant_id)
    accounting_api = AccountingApi(api_client)
    print(dir(accounting_api))
    invoices = accounting_api.get_invoices(
        xero_tenant_id
    )
    print(invoices)
    code = serialize_model(invoices)
    sub_title = "Total invoices found: {}".format(len(invoices.invoices))
    context = {'title': 'Xero|Invoices',
               'code': code['Invoices'],
               'sub_title': sub_title}
    return render(request, template_name="code.html", context=context)


def login(request):
    if not obtain_xero_oauth2_token():
        response = xero.authorize_redirect(request, redirect_uri="http://localhost:8000/callback")
        return response
    return redirect("home")


def logout(request):
    store_xero_oauth2_token(None)
    return redirect("login")


def oauth_callback(request):
    try:
        response = xero.authorize_access_token(request)
    except Exception as e:
        print(e)
        raise
    # todo validate state value
    if response is None or response.get("access_token") is None:
        return "Access denied: response=%s" % response
    print(response)
    store_xero_oauth2_token(response)
    return redirect("home")


def get_xero_tenant_id():
    try:
        print("You are here get xero tenant_id")
        token = obtain_xero_oauth2_token()
        print(token)
        if not token:
            return None 
        identity_api = IdentityApi(api_client) 
        for connection in identity_api.get_connections(): 
            if connection.tenant_type == "ORGANISATION":
                return connection.tenant_id
    except Exception as e:
        traceback.print_exc()
 
@xero_token_required
def create_invoice(request):
    xero_tenant_id = get_xero_tenant_id() 
    accounting_api = AccountingApi(api_client) 
    create_invoices = Invoices(invoices=[
        Invoice(
            amount_due=Decimal("40.00"),
            amount_paid=Decimal("0.00"),
            contact=Contact(
                addresses=[],
                bank_account_details=None,
                contact_groups=[],
                contact_id="b35c5a03-1755-4b0c-95d5-a4cd8cfc3f7d",
                contact_persons=[],
                contact_status=None,
                email_address=None,
                first_name=None,
                has_attachments=None,
                has_validation_errors=None,
                is_customer=None,
                is_supplier=None,
                last_name=None,
                name=None,
                phones=[],
                purchases_tracking_categories=[],
                sales_tracking_categories=[],
                updated_date_utc=None
            ),
            currency_code=None,
            currency_rate=None,
            date=datetime.date(2019, 3, 11),
            due_date=datetime.date(2020, 12, 10),
            has_attachments=False,
            has_errors=False,
            invoice_id=None,
            invoice_number=None,
            is_discounted=None,
            line_amount_types=LineAmountTypes.EXCLUSIVE,
            line_items=[LineItem(item_code='001', quantity="500", description="NewITem", unit_amount="200", tax_type="")],
            overpayments=[],
            prepayments=[],
            reference=None,
            sent_to_contact=False,
            status="AUTHORISED",
            status_attribute_string=None,
            sub_total=None,
            total=None,
            total_tax=None,
            type="ACCREC",
            updated_date_utc=datetime.datetime(
                2019, 3, 11, 17, 58, 46, 117000, tzinfo=tz.UTC
            ),
        )
    ])
    created_invoice = accounting_api.create_invoices(xero_tenant_id, create_invoices)
    print(created_invoice)
    return redirect("home")