from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

import json

from session.tests import get_user, User, PASSWORD_TEST

class MyProfileTest(TestCase):
    def setUp(self):
        self.user = get_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get(self):
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data, {
            'email': self.user.email,
            'username': self.user.username
        })

    def test_update(self):
        response = self.client.put('/api/me/', {'email': 'dracks@dracks.drk', 'username': 'dalek'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.username, "dalek")

    def test_patch_password(self):
        response = self.client.patch('/api/me/', {'new-password': '123456!a', 'password': '123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertFalse(user.check_password('123456!ab'), "Check with incorrect password")

        response = self.client.patch('/api/me/', {'new-password': '123456!ab', 'password': PASSWORD_TEST}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password('123456!ab'), "Check with correct password")

    def test_not_logged(self):
        client = APIClient()
        response = client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)