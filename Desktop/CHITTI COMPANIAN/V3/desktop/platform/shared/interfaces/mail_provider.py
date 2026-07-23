from typing import List

from desktop.platform.shared.interfaces.service import IService
from desktop.platform.shared.models.artifact import EmailArtifact


class IMailProvider(IService):
    """
    Abstracts specific mail backends (IMAP, Gmail API, Outlook API) for the MailCapability.
    """
    def query_mail(self, query: str) -> List[EmailArtifact]:
        ...

    def reply(self, email_id: str, content: str) -> EmailArtifact:
        ...

    def archive(self, email_id: str) -> None:
        ...
