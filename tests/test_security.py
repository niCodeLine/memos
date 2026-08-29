from unittest import TestCase

from app.core.security import generate_api_token, hash_token, has_scope, verify_token


class SecurityTests(TestCase):
    def test_generated_token_has_prefix(self):
        self.assertTrue(generate_api_token().startswith("remi_"))

    def test_token_hash_verification(self):
        token = generate_api_token()
        stored = hash_token(token)

        self.assertTrue(verify_token(token, stored))
        self.assertFalse(verify_token("wrong-token", stored))

    def test_scope_check_allows_exact_scope(self):
        self.assertTrue(has_scope(["reminders:read"], "reminders:read"))

    def test_scope_check_allows_wildcard(self):
        self.assertTrue(has_scope(["*"], "reminders:write"))

    def test_scope_check_rejects_missing_scope(self):
        self.assertFalse(has_scope(["reminders:read"], "reminders:write"))
