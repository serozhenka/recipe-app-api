from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """ Test creating a new user with a given email """
        email = 'test@gmail.com'
        password = 'test_password'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test if user email is normalized after creation """
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='test',
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test if creating user without an email field raises ValueError """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password='test')

    def test_create_superuser(self):
        """ Test created a new superuser """
        user = get_user_model().objects.create_superuser(
            email='test@gmail.com',
            password='test_password'
        )
        self.assertTrue(user.is_superuser, True)
        self.assertTrue(user.is_staff, True)
