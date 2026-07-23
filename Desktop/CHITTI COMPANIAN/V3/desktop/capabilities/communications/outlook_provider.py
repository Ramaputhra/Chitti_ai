"""
Microsoft Outlook Provider

Provides email functionality via Microsoft Graph API.
Supports:
- Reading emails
- Sending emails
- Managing folders
- Calendar integration
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import msal
    import requests
    HAS_MSAL = True
except ImportError:
    HAS_MSAL = False

from desktop.platform.shared.interfaces.service import ServiceState
from desktop.platform.shared.models.health import ProviderHealth
from desktop.platform.shared.interfaces.capability import ICapability
from desktop.platform.shared.models.capability import CapabilityDescriptor
from desktop.platform.shared.models.execution import ExecutionContext, ExecutionResult, ExecutionStatus
from desktop.platform.shared.models.tool import ToolDescriptor, ToolParameter
from desktop.platform.shared.models.ai import ToolInvocation


logger = logging.getLogger(__name__)


@dataclass
class OutlookEmail:
    """Represents an Outlook email."""
    id: str
    subject: str
    sender: str
    recipient: str
    body: str
    received_at: datetime
    is_read: bool
    has_attachments: bool
    categories: List[str]


@dataclass
class OutlookCalendarEvent:
    """Represents a calendar event."""
    id: str
    subject: str
    start: datetime
    end: datetime
    location: str
    attendees: List[str]
    is_online_meeting: bool


class OutlookProvider(ICapability):
    """
    Microsoft Outlook provider using Microsoft Graph API.
    Provides email and calendar functionality.
    """
    
    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        tenant_id: str = "common",
        account_email: str = ""
    ):
        self._state = ServiceState.STOPPED
        self._client_id = client_id
        self._client_secret = client_secret
        self._tenant_id = tenant_id
        self._account_email = account_email
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._msal_app = None
        self._graph_url = "https://graph.microsoft.com/v1.0"
        
        if HAS_MSAL and client_id and client_secret:
            self._initialize_msal()
    
    def _initialize_msal(self) -> None:
        """Initialize MSAL application."""
        if not HAS_MSAL:
            logger.warning("MSAL not installed. Outlook will be unavailable.")
            return
        
        self._msal_app = msal.ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}"
        )
    
    @property
    def name(self) -> str:
        return "OutlookProvider"
    
    @property
    def state(self) -> ServiceState:
        return self._state
    
    def initialize(self) -> None:
        """Initialize the provider."""
        if self._msal_app:
            self._acquire_token()
            self._state = ServiceState.RUNNING
            logger.info("OutlookProvider initialized")
        else:
            self._state = ServiceState.STOPPED
            logger.warning("OutlookProvider not configured")
    
    def shutdown(self) -> None:
        """Shutdown the provider."""
        self._state = ServiceState.STOPPED
        self._access_token = None
        logger.info("OutlookProvider shutdown")
    
    def _acquire_token(self) -> bool:
        """Acquire access token via client credentials flow."""
        if not self._msal_app:
            return False
        
        result = self._msal_app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" in result:
            self._access_token = result["access_token"]
            logger.info("Acquired Microsoft Graph access token")
            return True
        
        logger.error(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
        return False
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make a request to Microsoft Graph API."""
        if not self._access_token:
            if not self._acquire_token():
                return None
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self._graph_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json() if response.text else {}
            elif response.status_code == 401:
                # Token expired, try to refresh
                if self._acquire_token():
                    return self._make_request(method, endpoint, data, params)
            else:
                logger.error(f"Graph API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def discover_tools(self) -> List[ToolDescriptor]:
        """Return available tools."""
        return [
            ToolDescriptor(
                name="outlook_list_emails",
                description="List emails from inbox",
                parameters=[
                    ToolParameter(name="folder", type="string", required=False,
                                 description="Folder name (default: inbox)"),
                    ToolParameter(name="count", type="integer", required=False,
                                 description="Number of emails to fetch (default: 10)")
                ]
            ),
            ToolDescriptor(
                name="outlook_send_email",
                description="Send an email",
                parameters=[
                    ToolParameter(name="to", type="string", required=True,
                                 description="Recipient email address"),
                    ToolParameter(name="subject", type="string", required=True,
                                 description="Email subject"),
                    ToolParameter(name="body", type="string", required=True,
                                 description="Email body content"),
                    ToolParameter(name="cc", type="string", required=False,
                                 description="CC recipients (comma separated)"),
                    ToolParameter(name="bcc", type="string", required=False,
                                 description="BCC recipients (comma separated)")
                ]
            ),
            ToolDescriptor(
                name="outlook_read_email",
                description="Read a specific email",
                parameters=[
                    ToolParameter(name="email_id", type="string", required=True,
                                 description="ID of the email to read")
                ]
            ),
            ToolDescriptor(
                name="outlook_search_emails",
                description="Search emails",
                parameters=[
                    ToolParameter(name="query", type="string", required=True,
                                 description="Search query (e.g., 'from:john subject:meeting')")
                ]
            ),
            ToolDescriptor(
                name="outlook_mark_read",
                description="Mark email as read",
                parameters=[
                    ToolParameter(name="email_id", type="string", required=True,
                                 description="ID of the email to mark as read")
                ]
            ),
            ToolDescriptor(
                name="outlook_list_events",
                description="List calendar events",
                parameters=[
                    ToolParameter(name="start_time", type="string", required=False,
                                 description="Start time (ISO format)"),
                    ToolParameter(name="end_time", type="string", required=False,
                                 description="End time (ISO format)")
                ]
            ),
            ToolDescriptor(
                name="outlook_create_event",
                description="Create a calendar event",
                parameters=[
                    ToolParameter(name="subject", type="string", required=True,
                                 description="Event subject/title"),
                    ToolParameter(name="start", type="string", required=True,
                                 description="Start time (ISO format)"),
                    ToolParameter(name="end", type="string", required=True,
                                 description="End time (ISO format)"),
                    ToolParameter(name="body", type="string", required=False,
                                 description="Event description"),
                    ToolParameter(name="location", type="string", required=False,
                                 description="Event location"),
                    ToolParameter(name="attendees", type="string", required=False,
                                 description="Comma separated email addresses")
                ]
            )
        ]
    
    def validate(self, invocation: ToolInvocation) -> bool:
        """Validate the invocation."""
        return invocation.tool_name in [t.name for t in self.discover_tools()]
    
    async def execute(self, invocation: ToolInvocation, context: ExecutionContext) -> ExecutionResult:
        """Execute the Outlook operation."""
        try:
            tool_name = invocation.tool_name
            params = invocation.parameters or {}
            
            if tool_name == "outlook_list_emails":
                result = self._list_emails(
                    params.get("folder", "inbox"),
                    params.get("count", 10)
                )
            elif tool_name == "outlook_send_email":
                result = self._send_email(
                    to=params.get("to", ""),
                    subject=params.get("subject", ""),
                    body=params.get("body", ""),
                    cc=params.get("cc"),
                    bcc=params.get("bcc")
                )
            elif tool_name == "outlook_read_email":
                result = self._read_email(params.get("email_id", ""))
            elif tool_name == "outlook_search_emails":
                result = self._search_emails(params.get("query", ""))
            elif tool_name == "outlook_mark_read":
                result = self._mark_as_read(params.get("email_id", ""))
            elif tool_name == "outlook_list_events":
                result = self._list_events(
                    params.get("start_time"),
                    params.get("end_time")
                )
            elif tool_name == "outlook_create_event":
                result = self._create_event(
                    subject=params.get("subject", ""),
                    start=params.get("start", ""),
                    end=params.get("end", ""),
                    body=params.get("body", ""),
                    location=params.get("location", ""),
                    attendees=params.get("attendees", "")
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Unknown tool: {tool_name}"
                )
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message="Operation completed",
                data=result
            )
            
        except Exception as e:
            logger.error(f"Outlook error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=str(e)
            )
    
    def _list_emails(self, folder: str = "inbox", count: int = 10) -> Dict[str, Any]:
        """List emails from a folder."""
        folder_map = {
            "inbox": "Inbox",
            "sent": "Sent Items",
            "drafts": "Drafts",
            "deleted": "Deleted Items",
            "junk": "Junk Email"
        }
        
        folder_name = folder_map.get(folder.lower(), folder)
        
        result = self._make_request(
            "GET",
            f"/me/mailFolders/{folder_name}/messages",
            params={"$top": count, "$select": "id,subject,from,toRecipients,receivedDateTime,isRead,hasAttachments"}
        )
        
        if result is None:
            return {"error": "Failed to fetch emails"}
        
        emails = []
        for msg in result.get("value", []):
            emails.append({
                "id": msg.get("id"),
                "subject": msg.get("subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                "to": [r.get("emailAddress", {}).get("address", "") for r in msg.get("toRecipients", [])],
                "received_at": msg.get("receivedDateTime"),
                "is_read": msg.get("isRead", True),
                "has_attachments": msg.get("hasAttachments", False)
            })
        
        return {"emails": emails, "folder": folder, "count": len(emails)}
    
    def _send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email."""
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": addr.strip()}}
                    for addr in to.split(",")
                ]
            },
            "saveToSentItems": "true"
        }
        
        if cc:
            message["message"]["ccRecipients"] = [
                {"emailAddress": {"address": addr.strip()}}
                for addr in cc.split(",")
            ]
        
        if bcc:
            message["message"]["bccRecipients"] = [
                {"emailAddress": {"address": addr.strip()}}
                for addr in bcc.split(",")
            ]
        
        result = self._make_request("POST", "/me/sendMail", data=message)
        
        if result is None:
            return {"error": "Failed to send email"}
        
        return {"sent": True, "to": to, "subject": subject}
    
    def _read_email(self, email_id: str) -> Dict[str, Any]:
        """Read a specific email."""
        result = self._make_request(
            "GET",
            f"/me/messages/{email_id}",
            params={"$select": "id,subject,from,toRecipients,body,receivedDateTime,isRead,hasAttachments,categories"}
        )
        
        if result is None:
            return {"error": "Email not found"}
        
        return {
            "id": result.get("id"),
            "subject": result.get("subject"),
            "from": result.get("from", {}).get("emailAddress", {}).get("address", ""),
            "to": [r.get("emailAddress", {}).get("address", "") for r in result.get("toRecipients", [])],
            "body": result.get("body", {}).get("content", ""),
            "received_at": result.get("receivedDateTime"),
            "is_read": result.get("isRead", True),
            "has_attachments": result.get("hasAttachments", False),
            "categories": result.get("categories", [])
        }
    
    def _search_emails(self, query: str) -> Dict[str, Any]:
        """Search emails."""
        result = self._make_request(
            "GET",
            "/me/messages",
            params={"$search": query, "$top": 20}
        )
        
        if result is None:
            return {"error": "Search failed"}
        
        emails = []
        for msg in result.get("value", []):
            emails.append({
                "id": msg.get("id"),
                "subject": msg.get("subject"),
                "from": msg.get("from", {}).get("emailAddress", {}).get("address", ""),
                "received_at": msg.get("receivedDateTime"),
                "snippet": msg.get("bodyPreview", "")[:100]
            })
        
        return {"emails": emails, "query": query, "count": len(emails)}
    
    def _mark_as_read(self, email_id: str) -> Dict[str, Any]:
        """Mark email as read."""
        result = self._make_request(
            "PATCH",
            f"/me/messages/{email_id}",
            data={"isRead": True}
        )
        
        if result is None:
            return {"error": "Failed to mark as read"}
        
        return {"marked": True, "email_id": email_id}
    
    def _list_events(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """List calendar events."""
        params = {"$orderby": "start/dateTime", "$top": 20}
        
        if start_time and end_time:
            params["$filter"] = f"start/dateTime ge '{start_time}' and end/dateTime le '{end_time}'"
        
        result = self._make_request("GET", "/me/calendar/events", params=params)
        
        if result is None:
            return {"error": "Failed to fetch events"}
        
        events = []
        for event in result.get("value", []):
            events.append({
                "id": event.get("id"),
                "subject": event.get("subject"),
                "start": event.get("start", {}).get("dateTime"),
                "end": event.get("end", {}).get("dateTime"),
                "location": event.get("location", {}).get("displayName", ""),
                "attendees": [
                    a.get("emailAddress", {}).get("address", "")
                    for a in event.get("attendees", [])
                ],
                "is_online_meeting": event.get("isOnlineMeeting", False)
            })
        
        return {"events": events, "count": len(events)}
    
    def _create_event(
        self,
        subject: str,
        start: str,
        end: str,
        body: str = "",
        location: str = "",
        attendees: str = ""
    ) -> Dict[str, Any]:
        """Create a calendar event."""
        event = {
            "subject": subject,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
            "body": {"contentType": "Text", "content": body}
        }
        
        if location:
            event["location"] = {"displayName": location}
        
        if attendees:
            event["attendees"] = [
                {"emailAddress": {"address": email.strip(), "name": ""}, "type": "required"}
                for email in attendees.split(",")
            ]
        
        result = self._make_request("POST", "/me/calendar/events", data=event)
        
        if result is None:
            return {"error": "Failed to create event"}
        
        return {
            "created": True,
            "event_id": result.get("id"),
            "subject": subject,
            "start": start
        }
    
    def describe(self) -> CapabilityDescriptor:
        """Return capability descriptor."""
        return CapabilityDescriptor(
            id="outlook",
            version="1.0.0",
            name="Microsoft Outlook",
            description="Email and calendar via Microsoft Graph API",
            category="communications",
            tags=["email", "outlook", "calendar", "microsoft"]
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy" if self._access_token else "unavailable",
            "configured": bool(self._msal_app),
            "authenticated": bool(self._access_token)
        }
