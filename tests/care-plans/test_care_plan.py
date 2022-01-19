import pytest

from core.utils.email import Email


@pytest.mark.asyncio
async def test_care_plan(ctx, aws_ctx):
    code = "9430193"
    email = Email(to="vlad.ogai+testses@nrg-soft.com", subject="Alakine Email Verification")
    email.text(f"Your verification code is: {code}")
    email.html(f"<html><body>Your verification code is: <strong>{code}</strong> </body></html>")
    email_result = email.send()
    print(email_result)
