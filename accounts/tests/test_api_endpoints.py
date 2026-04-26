from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import CustomUser
from ngo.models import NGO, Activity
from django.utils import timezone
from rest_framework.authtoken.models import Token

class APITest(TestCase):
    def setUp(self):
        # create users
        self.admin = CustomUser.objects.create_user(username='admin1', password='AdminPass123!', role='admin')
        self.employee = CustomUser.objects.create_user(username='emp1', password='EmpPass123!', role='employee')
        # tokens
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.emp_token, _ = Token.objects.get_or_create(user=self.employee)
        # client
        self.client = APIClient()
        # sample NGO and Activity
        self.ngo = NGO.objects.create(name='Helping Hands', contact_email='contact@help.org')
        self.activity = Activity.objects.create(
            title='Beach Cleanup', description='Clean the beach', location='KL',
            date=timezone.now() + timezone.timedelta(days=7),
            cut_off_datetime=timezone.now() + timezone.timedelta(days=6),
            max_slots=10,
            ngo=self.ngo,
            created_by=self.admin,
        )

    def test_admin_create_ngo(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {'name':'New NGO','contact_email':'a@b.com'}
        resp = self.client.post('/api/v1/ngos/', data)
        self.assertEqual(resp.status_code, 201)

    def test_employee_cannot_create_ngo(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.emp_token.key)
        data = {'name':'Evil NGO','contact_email':'e@evil.com'}
        resp = self.client.post('/api/v1/ngos/', data)
        self.assertIn(resp.status_code, (403, 405))

    def test_employee_register_activity(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.emp_token.key)
        data = {'activity': self.activity.id}
        resp = self.client.post('/api/v1/registrations/', data)
        self.assertEqual(resp.status_code, 201)
