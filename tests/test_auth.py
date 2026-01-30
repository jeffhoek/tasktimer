import os
import unittest
from unittest.mock import patch, MagicMock

# Set environment variables before importing auth modules
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["COGNITO_REGION"] = "us-east-1"
os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_testpool"
os.environ["COGNITO_APP_CLIENT_ID"] = "test-client-id"

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from jose import jwt
import time


class TestAuthDependency(unittest.TestCase):
    """Tests for the get_current_user dependency"""

    def setUp(self):
        # Import fresh to pick up env vars
        from tasktimer.auth.dependencies import get_current_user
        from tasktimer.auth.models import AuthenticatedUser

        self.app = FastAPI()

        @self.app.get("/protected")
        async def protected_route(user: AuthenticatedUser = Depends(get_current_user)):
            return {"user_id": user.user_id, "email": user.email}

        self.client = TestClient(self.app)

    @patch("tasktimer.auth.dependencies.settings")
    def test_auth_disabled_returns_mock_user(self, mock_settings):
        """When AUTH_DISABLED=true, return mock user without token"""
        mock_settings.AUTH_DISABLED = True

        response = self.client.get("/protected")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], "dev-user-001")
        self.assertEqual(data["email"], "dev@localhost")

    @patch("tasktimer.auth.dependencies.settings")
    def test_missing_token_returns_401(self, mock_settings):
        """When auth enabled and no token provided, return 401"""
        mock_settings.AUTH_DISABLED = False

        response = self.client.get("/protected")

        self.assertEqual(response.status_code, 401)
        self.assertIn("Missing authorization header", response.json()["detail"])

    @patch("tasktimer.auth.dependencies.settings")
    @patch("tasktimer.auth.dependencies.decode_and_validate_token")
    def test_valid_token_returns_user(self, mock_decode, mock_settings):
        """When valid token provided, return authenticated user"""
        mock_settings.AUTH_DISABLED = False
        mock_decode.return_value = {
            "sub": "cognito-user-uuid-123",
            "email": "test@example.com",
        }

        response = self.client.get(
            "/protected",
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], "cognito-user-uuid-123")
        self.assertEqual(data["email"], "test@example.com")

    @patch("tasktimer.auth.dependencies.settings")
    @patch("tasktimer.auth.dependencies.decode_and_validate_token")
    def test_invalid_token_returns_401(self, mock_decode, mock_settings):
        """When invalid token provided, return 401"""
        from jose import JWTError

        mock_settings.AUTH_DISABLED = False
        mock_decode.side_effect = JWTError("Token expired")

        response = self.client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid token", response.json()["detail"])

    @patch("tasktimer.auth.dependencies.settings")
    @patch("tasktimer.auth.dependencies.decode_and_validate_token")
    def test_token_missing_sub_returns_401(self, mock_decode, mock_settings):
        """When token has no sub claim, return 401"""
        mock_settings.AUTH_DISABLED = False
        mock_decode.return_value = {"email": "test@example.com"}  # Missing 'sub'

        response = self.client.get(
            "/protected",
            headers={"Authorization": "Bearer token-without-sub"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("Token missing subject claim", response.json()["detail"])


class TestJWKSCaching(unittest.TestCase):
    """Tests for JWKS caching behavior"""

    def setUp(self):
        from tasktimer.auth.cognito import clear_jwks_cache

        clear_jwks_cache()

    @patch("tasktimer.auth.cognito.requests.get")
    def test_jwks_is_cached(self, mock_get):
        """JWKS should be fetched once and cached"""
        from tasktimer.auth.cognito import get_jwks, clear_jwks_cache

        clear_jwks_cache()

        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "key1"}]}
        mock_get.return_value = mock_response

        # First call should fetch
        result1 = get_jwks()
        self.assertEqual(result1, {"keys": [{"kid": "key1"}]})
        self.assertEqual(mock_get.call_count, 1)

        # Second call should use cache
        result2 = get_jwks()
        self.assertEqual(result2, {"keys": [{"kid": "key1"}]})
        self.assertEqual(mock_get.call_count, 1)  # Still 1, not 2

    @patch("tasktimer.auth.cognito.requests.get")
    def test_cache_can_be_cleared(self, mock_get):
        """Cache should be clearable for testing"""
        from tasktimer.auth.cognito import get_jwks, clear_jwks_cache

        clear_jwks_cache()

        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "key1"}]}
        mock_get.return_value = mock_response

        get_jwks()
        self.assertEqual(mock_get.call_count, 1)

        clear_jwks_cache()

        get_jwks()
        self.assertEqual(mock_get.call_count, 2)  # Fetched again after clear


class TestCognitoConfig(unittest.TestCase):
    """Tests for Cognito configuration"""

    def test_jwks_url_format(self):
        """JWKS URL should be correctly formatted"""
        from tasktimer.auth.config import CognitoSettings

        config = CognitoSettings(
            COGNITO_REGION="us-west-2",
            COGNITO_USER_POOL_ID="us-west-2_abc123",
        )

        expected = (
            "https://cognito-idp.us-west-2.amazonaws.com/"
            "us-west-2_abc123/.well-known/jwks.json"
        )
        self.assertEqual(config.jwks_url, expected)

    def test_issuer_format(self):
        """Issuer should be correctly formatted"""
        from tasktimer.auth.config import CognitoSettings

        config = CognitoSettings(
            COGNITO_REGION="us-west-2",
            COGNITO_USER_POOL_ID="us-west-2_abc123",
        )

        expected = "https://cognito-idp.us-west-2.amazonaws.com/us-west-2_abc123"
        self.assertEqual(config.issuer, expected)


if __name__ == "__main__":
    unittest.main()
