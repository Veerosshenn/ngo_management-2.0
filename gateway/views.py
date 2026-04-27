import os

import json
import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


def _svc_urls():
    return {
        "user": os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/"),
        "ngo": os.environ.get("NGO_SERVICE_URL", "http://127.0.0.1:8003").rstrip("/"),
        "reg": os.environ.get("REG_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/"),
    }


def _copy_auth_headers(request):
    headers = {}
    auth = request.headers.get("Authorization")
    if auth:
        headers["Authorization"] = auth
    # allow session cookie passthrough if you demo session auth locally
    cookie = request.headers.get("Cookie")
    if cookie:
        headers["Cookie"] = cookie
    return headers


@csrf_exempt
def proxy(request, service: str, path: str = ""):
    """
    Topic 11.2: API Gateway proxy.
    Example:
      /api/v1/gw/ngo/ngos/  ->  http://NGO_SERVICE_URL/api/v1/ngos/
    """
    svc = _svc_urls().get(service)
    if not svc:
        return JsonResponse({"detail": "Unknown service."}, status=404)

    target = f"{svc}/api/v1/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=target,
            headers={**_copy_auth_headers(request), "Accept": request.headers.get("Accept", "*/*")},
            params=request.GET,
            data=request.body if request.body else None,
            timeout=20,
        )
    except requests.RequestException as e:
        return JsonResponse({"detail": f"Service unavailable: {e.__class__.__name__}"}, status=502)

    content_type = resp.headers.get("Content-Type", "application/json")
    return HttpResponse(resp.content, status=resp.status_code, content_type=content_type)


@csrf_exempt
def register_orchestrated(request):
    """
    Topic 11.2: Example orchestrated flow.
    POST /api/v1/gateway/register/  { "activity_id": 123 }
    - Confirms user is employee (User Service)
    - Checks slot availability (NGO Service)
    - Creates registration (Registration Service)
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    try:
        payload = request.body.decode("utf-8") if request.body else "{}"
        data = json.loads(payload) if payload else {}
    except Exception:
        return JsonResponse({"detail": "Invalid JSON."}, status=400)

    activity_id = data.get("activity_id")
    if not activity_id:
        return JsonResponse({"detail": "activity_id is required."}, status=400)

    urls = _svc_urls()
    headers = {**_copy_auth_headers(request), "Content-Type": "application/json", "Accept": "application/json"}

    # 1) role check
    me = requests.get(f"{urls['user']}/api/v1/users/me/", headers=headers, timeout=10)
    if me.status_code != 200:
        return HttpResponse(me.content, status=me.status_code, content_type=me.headers.get("Content-Type", "application/json"))
    me_json = me.json()
    if not me_json.get("is_employee"):
        return JsonResponse({"detail": "Employees only."}, status=403)

    # 2) slot check
    avail = requests.get(f"{urls['ngo']}/api/v1/activities/{activity_id}/availability/", headers=headers, timeout=10)
    if avail.status_code != 200:
        return HttpResponse(
            avail.content, status=avail.status_code, content_type=avail.headers.get("Content-Type", "application/json")
        )
    if not avail.json().get("available"):
        return JsonResponse({"detail": "No slots available."}, status=400)

    # 3) create registration
    reg = requests.post(f"{urls['reg']}/api/v1/registrations/", headers=headers, json={"activity": activity_id}, timeout=10)
    return HttpResponse(reg.content, status=reg.status_code, content_type=reg.headers.get("Content-Type", "application/json"))

