from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import CustomUser
from ngo.models import Activity, NGO
from registration.models import Registration
from registration.services import RegistrationService


class RegistrationServiceUnitTests(TestCase):
    def setUp(self):
        self.employee = CustomUser.objects.create_user(
            username="emp_unit",
            password="EmpUnit123!",
            role="employee",
        )
        self.ngo = NGO.objects.create(
            name="Unit NGO",
            contact_email="unit@ngo.test",
            website="https://unit.example",
            description="Unit test NGO",
        )
        self.activity = Activity.objects.create(
            title="Unit Activity",
            description="Unit test activity",
            location="Penang",
            date=timezone.now() + timedelta(days=2),
            cut_off_datetime=timezone.now() + timedelta(days=1),
            max_slots=2,
            ngo=self.ngo,
        )

    def test_register_user_successfully_creates_active_registration(self):
        reg = RegistrationService.register_user(self.employee, self.activity.id)
        self.assertEqual(reg.status, "active")
        self.assertEqual(reg.employee, self.employee)
        self.assertEqual(reg.activity, self.activity)
        self.assertEqual(Registration.objects.filter(employee=self.employee, activity=self.activity).count(), 1)

    def test_register_user_duplicate_active_registration_raises_error(self):
        RegistrationService.register_user(self.employee, self.activity.id)
        with self.assertRaisesMessage(ValueError, "already registered"):
            RegistrationService.register_user(self.employee, self.activity.id)

    def test_register_user_raises_error_when_activity_full(self):
        self.activity.max_slots = 1
        self.activity.save(update_fields=["max_slots"])
        other = CustomUser.objects.create_user(
            username="emp_other",
            password="EmpOther123!",
            role="employee",
        )
        RegistrationService.register_user(other, self.activity.id)
        with self.assertRaisesMessage(ValueError, "fully booked"):
            RegistrationService.register_user(self.employee, self.activity.id)

    def test_register_user_raises_error_when_cutoff_passed(self):
        self.activity.cut_off_datetime = timezone.now() - timedelta(minutes=1)
        self.activity.save(update_fields=["cut_off_datetime"])
        with self.assertRaisesMessage(ValueError, "cut-off date has passed"):
            RegistrationService.register_user(self.employee, self.activity.id)

    def test_register_user_reactivates_cancelled_registration(self):
        reg = Registration.objects.create(
            employee=self.employee,
            activity=self.activity,
            status="cancelled",
        )
        returned = RegistrationService.register_user(self.employee, self.activity.id)
        reg.refresh_from_db()
        self.assertEqual(reg.id, returned.id)
        self.assertEqual(reg.status, "active")


class RegistrationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = CustomUser.objects.create_user(
            username="emp_api",
            password="EmpApi123!",
            role="employee",
        )
        self.admin = CustomUser.objects.create_user(
            username="admin_api",
            password="AdminApi123!",
            role="admin",
        )
        self.emp_token, _ = Token.objects.get_or_create(user=self.employee)
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.ngo = NGO.objects.create(
            name="API NGO",
            contact_email="api@ngo.test",
            website="https://api.example",
            description="API test NGO",
        )
        self.activity = Activity.objects.create(
            title="API Activity",
            description="API test activity",
            location="KL",
            date=timezone.now() + timedelta(days=3),
            cut_off_datetime=timezone.now() + timedelta(days=2),
            max_slots=5,
            ngo=self.ngo,
        )

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_employee_can_create_registration(self):
        self._auth(self.emp_token.key)
        resp = self.client.post("/api/v1/registrations/", {"activity": self.activity.id}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Registration.objects.filter(employee=self.employee, activity=self.activity).count(), 1)

    def test_admin_cannot_create_registration(self):
        self._auth(self.admin_token.key)
        resp = self.client.post("/api/v1/registrations/", {"activity": self.activity.id}, format="json")
        self.assertEqual(resp.status_code, 403)

    def test_cancel_by_activity_marks_status_cancelled(self):
        reg = Registration.objects.create(employee=self.employee, activity=self.activity, status="active")
        self._auth(self.emp_token.key)
        resp = self.client.delete(f"/api/v1/registrations/by-activity/{self.activity.id}/")
        self.assertEqual(resp.status_code, 200)
        reg.refresh_from_db()
        self.assertEqual(reg.status, "cancelled")
