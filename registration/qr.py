import base64
import io

import qrcode
from django.core.signing import TimestampSigner


signer = TimestampSigner(salt="registration-checkin")


def make_checkin_token(registration_id: int, employee_id: int, activity_id: int) -> str:
    payload = f"{registration_id}:{employee_id}:{activity_id}"
    return signer.sign(payload)


def make_qr_png_base64(data: str) -> str:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

