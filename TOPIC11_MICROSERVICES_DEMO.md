# Topic 11 Microservices Demo (Local)

This repo can be demonstrated as **3 microservices + 1 API Gateway** by running 4 Django processes with different settings modules.

## Services
- **API Gateway**: `http://127.0.0.1:8000`
- **User Service**: `http://127.0.0.1:8001`
- **Registration Service**: `http://127.0.0.1:8002`
- **NGO Service**: `http://127.0.0.1:8003`

## Start commands (PowerShell)
Open 4 terminals in the project root and run:

```powershell
python manage.py runserver 8001 --settings ngo_management.settings_user_service
python manage.py runserver 8003 --settings ngo_management.settings_ngo_service
python manage.py runserver 8002 --settings ngo_management.settings_registration_service
python manage.py runserver 8000 --settings ngo_management.settings_gateway_service
```

## API Gateway routes
The gateway exposes:

- **Proxy**:
  - `GET/POST/... /api/v1/gw/user/<path>` → forwards to User Service `/api/v1/<path>`
  - `GET/POST/... /api/v1/gw/ngo/<path>` → forwards to NGO Service `/api/v1/<path>`
  - `GET/POST/... /api/v1/gw/reg/<path>` → forwards to Registration Service `/api/v1/<path>`

- **Orchestrated example**:
  - `POST /api/v1/gateway/register/` body `{ "activity_id": 123 }`
  - Flow:
    - calls **User Service** `/api/v1/users/me/` (role check)
    - calls **NGO Service** `/api/v1/activities/<id>/availability/` (slot check)
    - calls **Registration Service** `/api/v1/registrations/` (create)

## Auth for demo (Token)
1. Obtain token from **User Service**:
   - `POST http://127.0.0.1:8001/api/v1/auth/token/`
2. Call gateway endpoints with header:
   - `Authorization: Token <token>`

## Notes (coursework)
For speed, these services reuse the same database and codebase, but they run as **independent processes** and communicate using **REST calls** through the gateway.

