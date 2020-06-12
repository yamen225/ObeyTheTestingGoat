from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.authentication import PasswordlessAuthenticateBackend
from accounts.models import Token
User = get_user_model()


class AuthenticateTest(TestCase):

    def test_returns_None_if_no_such_token(self):
        result = PasswordlessAuthenticateBackend().authenticate(
            'no-such-token'
        )
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        email = 'tdd@example.com'
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticateBackend().authenticate(uid=token.uid)
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        email = 'tdd@example.com'
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticateBackend().authenticate(uid=token.uid)
        self.assertEqual(user, existing_user)

    def test_gets_user_by_email(self):
        User.objects.create(email="another@example.com")
        desired_user = User.objects.create(email='tdd@example.com')
        found_user = PasswordlessAuthenticateBackend().get_user(
            'tdd@example.com'
        )
        self.assertEqual(found_user, desired_user)

    def test_returns_None_if_no_user_with_that_email(self):
        self.assertIsNone(
            PasswordlessAuthenticateBackend().get_user('tdd@example.com')
        )
