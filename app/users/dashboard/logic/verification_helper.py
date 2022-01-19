from abc import ABC, abstractmethod

from fastapi import Request

from app.context import get_current_workspace
from app.tenant_workspaces.model_db import Workspace
from core.config import get_app_config
from core.utils.aws import get_sns
from core.utils.db import register_tenant_connection
from core.utils.email import Email


class VerificationHelper(ABC):

    @abstractmethod
    async def lookup_workspace(self, username: str, request: Request):
        pass

    @abstractmethod
    def send_code_to_user(self, username: str, subject_title: str, message_text: str,
                          **kwargs):
        pass


class EmailHelper(VerificationHelper):

    async def lookup_workspace(self, username: str, request: Request):
        # This is hardcoded but should be changed to a real lookup
        wks: Workspace = await get_current_workspace(request)

        cfg = get_app_config()
        await register_tenant_connection(cfg, wks.tenant_db_1, "tenant-db-basic-data")
        await register_tenant_connection(cfg, wks.tenant_db_2, "tenant-db-personal-data")
        return wks

    def send_code_to_user(self, username: str, subject_title: str,
                          message_text: str, **kwargs):
        """kwargs сan have html message if it needs
        :message_html"""
        print("[VERIFY-EMAIL] Sending email")
        email = Email(to=username, subject=subject_title)
        email.text(message_text)
        if "message_html" in kwargs:
            email.html(kwargs["message_html"])

        email_result = email.send()
        print(email_result)
        print("[VERIFY-EMAIL] Email sent.")


class PhoneHelper(VerificationHelper):

    async def lookup_workspace(self, username: str, request: Request):
        wks: Workspace = await get_current_workspace(request)

        cfg = get_app_config()
        await register_tenant_connection(cfg, wks.tenant_db_1, "tenant-db-basic-data")
        await register_tenant_connection(cfg, wks.tenant_db_2, "tenant-db-personal-data")
        return wks

    def send_code_to_user(self, username: str, subject_title: str, message_text: str,
                          **kwargs):
        print("[VERIFY-PHONE] Sending SMS")
        result = get_sns().publish(
            PhoneNumber=username,
            Message=message_text
        )

        print(result)
        print("[VERIFY-PHONE] SMS sent.")
