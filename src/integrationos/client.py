import httpx
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from .resource import PassthroughResourceImpl, UnifiedResourceImpl
from .types.models import *

T = TypeVar('T', bound=BaseModel)

class ResourceFactory(Generic[T]):
    def __init__(self, client: httpx.AsyncClient, resource_name: str, model_class: Type[T]):
        self.client = client
        self.resource_name = resource_name
        self.model_class = model_class

    def __call__(self, connection_key: str) -> UnifiedResourceImpl[T]:
        return UnifiedResourceImpl(
            client=self.client,
            connection_key=connection_key,
            resource_name=self.resource_name,
            model_class=self.model_class
        )

class PassthroughFactory:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    def __call__(self, connection_key: str) -> PassthroughResourceImpl[Any]:
        return PassthroughResourceImpl(
            client=self.client,
            connection_key=connection_key,
            resource_name='',
            model_class=dict  # Using dict as the model class since passthrough returns raw data
        )

class IntegrationOS:
    def __init__(self, api_key: str, base_url: str = "https://api.integrationos.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'x-integrationos-secret': self.api_key,
                'Content-Type': 'application/json',
            }
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    @property
    def passthrough(self) -> PassthroughFactory:
        return PassthroughFactory(self.client)

    
    @property
    def events(self) -> ResourceFactory[Events]:
        return ResourceFactory(self.client, 'events', Events)
    
    @property
    def calendars(self) -> ResourceFactory[Calendars]:
        return ResourceFactory(self.client, 'calendars', Calendars)
    
    @property
    def threads(self) -> ResourceFactory[Threads]:
        return ResourceFactory(self.client, 'threads', Threads)
    
    @property
    def drafts(self) -> ResourceFactory[Drafts]:
        return ResourceFactory(self.client, 'drafts', Drafts)
    
    @property
    def drives(self) -> ResourceFactory[Drives]:
        return ResourceFactory(self.client, 'drives', Drives)
    
    @property
    def folders(self) -> ResourceFactory[Folders]:
        return ResourceFactory(self.client, 'folders', Folders)
    
    @property
    def files(self) -> ResourceFactory[Files]:
        return ResourceFactory(self.client, 'files', Files)
    
    @property
    def recordings(self) -> ResourceFactory[Recordings]:
        return ResourceFactory(self.client, 'recordings', Recordings)
    
    @property
    def transcripts(self) -> ResourceFactory[Transcripts]:
        return ResourceFactory(self.client, 'transcripts', Transcripts)
    
    @property
    def tables(self) -> ResourceFactory[Tables]:
        return ResourceFactory(self.client, 'tables', Tables)
    
    @property
    def databases(self) -> ResourceFactory[Databases]:
        return ResourceFactory(self.client, 'databases', Databases)
    
    @property
    def attributes(self) -> ResourceFactory[Attributes]:
        return ResourceFactory(self.client, 'attributes', Attributes)
    
    @property
    def records(self) -> ResourceFactory[Records]:
        return ResourceFactory(self.client, 'records', Records)
    
    @property
    def objects(self) -> ResourceFactory[Objects]:
        return ResourceFactory(self.client, 'objects', Objects)
    
    @property
    def modifierGroups(self) -> ResourceFactory[ModifierGroups]:
        return ResourceFactory(self.client, 'modifier-groups', ModifierGroups)
    
    @property
    def locations(self) -> ResourceFactory[Locations]:
        return ResourceFactory(self.client, 'locations', Locations)
    
    @property
    def webhooks(self) -> ResourceFactory[Webhooks]:
        return ResourceFactory(self.client, 'webhooks', Webhooks)
    
    @property
    def priceRules(self) -> ResourceFactory[PriceRules]:
        return ResourceFactory(self.client, 'price-rules', PriceRules)
    
    @property
    def discounts(self) -> ResourceFactory[Discounts]:
        return ResourceFactory(self.client, 'discounts', Discounts)
    
    @property
    def chats(self) -> ResourceFactory[Chats]:
        return ResourceFactory(self.client, 'chats', Chats)
    
    @property
    def messages(self) -> ResourceFactory[Messages]:
        return ResourceFactory(self.client, 'messages', Messages)
    
    @property
    def conversations(self) -> ResourceFactory[Conversations]:
        return ResourceFactory(self.client, 'conversations', Conversations)
    
    @property
    def taxRates(self) -> ResourceFactory[TaxRates]:
        return ResourceFactory(self.client, 'tax-rates', TaxRates)
    
    @property
    def creditNotes(self) -> ResourceFactory[CreditNotes]:
        return ResourceFactory(self.client, 'credit-notes', CreditNotes)
    
    @property
    def expenses(self) -> ResourceFactory[Expenses]:
        return ResourceFactory(self.client, 'expenses', Expenses)
    
    @property
    def transactions(self) -> ResourceFactory[Transactions]:
        return ResourceFactory(self.client, 'transactions', Transactions)
    
    @property
    def accounts(self) -> ResourceFactory[Accounts]:
        return ResourceFactory(self.client, 'accounts', Accounts)
    
    @property
    def purchaseOrders(self) -> ResourceFactory[PurchaseOrders]:
        return ResourceFactory(self.client, 'purchase-orders', PurchaseOrders)
    
    @property
    def refunds(self) -> ResourceFactory[Refunds]:
        return ResourceFactory(self.client, 'refunds', Refunds)
    
    @property
    def payments(self) -> ResourceFactory[Payments]:
        return ResourceFactory(self.client, 'payments', Payments)
    
    @property
    def bills(self) -> ResourceFactory[Bills]:
        return ResourceFactory(self.client, 'bills', Bills)
    
    @property
    def vendors(self) -> ResourceFactory[Vendors]:
        return ResourceFactory(self.client, 'vendors', Vendors)
    
    @property
    def balanceSheets(self) -> ResourceFactory[BalanceSheets]:
        return ResourceFactory(self.client, 'balance-sheets', BalanceSheets)
    
    @property
    def incomeStatements(self) -> ResourceFactory[IncomeStatements]:
        return ResourceFactory(self.client, 'income-statements', IncomeStatements)
    
    @property
    def invoices(self) -> ResourceFactory[Invoices]:
        return ResourceFactory(self.client, 'invoices', Invoices)
    
    @property
    def journalEntries(self) -> ResourceFactory[JournalEntries]:
        return ResourceFactory(self.client, 'journal-entries', JournalEntries)
    
    @property
    def invoiceItems(self) -> ResourceFactory[InvoiceItems]:
        return ResourceFactory(self.client, 'invoice-items', InvoiceItems)
    
    @property
    def tickets(self) -> ResourceFactory[Tickets]:
        return ResourceFactory(self.client, 'tickets', Tickets)
    
    @property
    def candidates(self) -> ResourceFactory[Candidates]:
        return ResourceFactory(self.client, 'candidates', Candidates)
    
    @property
    def contacts(self) -> ResourceFactory[Contacts]:
        return ResourceFactory(self.client, 'contacts', Contacts)
    
    @property
    def jobs(self) -> ResourceFactory[Jobs]:
        return ResourceFactory(self.client, 'jobs', Jobs)
    
    @property
    def tasks(self) -> ResourceFactory[Tasks]:
        return ResourceFactory(self.client, 'tasks', Tasks)
    
    @property
    def products(self) -> ResourceFactory[Products]:
        return ResourceFactory(self.client, 'products', Products)
    
    @property
    def orders(self) -> ResourceFactory[Orders]:
        return ResourceFactory(self.client, 'orders', Orders)
    
    @property
    def opportunities(self) -> ResourceFactory[Opportunities]:
        return ResourceFactory(self.client, 'opportunities', Opportunities)
    
    @property
    def users(self) -> ResourceFactory[Users]:
        return ResourceFactory(self.client, 'users', Users)
    
    @property
    def categories(self) -> ResourceFactory[Categories]:
        return ResourceFactory(self.client, 'categories', Categories)
    
    @property
    def notes(self) -> ResourceFactory[Notes]:
        return ResourceFactory(self.client, 'notes', Notes)
    
    @property
    def leads(self) -> ResourceFactory[Leads]:
        return ResourceFactory(self.client, 'leads', Leads)
    
    @property
    def companies(self) -> ResourceFactory[Companies]:
        return ResourceFactory(self.client, 'companies', Companies)
    
    @property
    def customers(self) -> ResourceFactory[Customers]:
        return ResourceFactory(self.client, 'customers', Customers)
    