from django.test import TestCase
from django.urls import reverse


class UserRegistrationTests(TestCase):
    def test_university_registration_does_not_require_names(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'mit_org',
            'email': 'mit@example.com',
            'role': 'university',
            'institution_name': 'MIT',
            'location': 'Cambridge',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('dashboard:index'))
        self.assertFalse(response.wsgi_request.user.first_name)
        self.assertFalse(response.wsgi_request.user.last_name)

    def test_industry_registration_does_not_require_names(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'apex_org',
            'email': 'apex@example.com',
            'role': 'industry',
            'institution_name': 'Apex Technologies',
            'location': 'Chicago',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('dashboard:index'))
        self.assertFalse(response.wsgi_request.user.first_name)
        self.assertFalse(response.wsgi_request.user.last_name)

    def test_student_registration_requires_names(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'student_org',
            'email': 'student@example.com',
            'role': 'student',
            'password': 'StrongPass123',
            'confirm_password': 'StrongPass123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'first_name', 'First name is required for Student accounts.')
        self.assertFormError(response.context['form'], 'last_name', 'Last name is required for Student accounts.')
