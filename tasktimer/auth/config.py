from functools import cached_property
from pydantic_settings import BaseSettings


class CognitoSettings(BaseSettings):
    COGNITO_REGION: str = "us-east-1"
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_APP_CLIENT_ID: str = ""
    AUTH_DISABLED: bool = False

    @cached_property
    def jwks_url(self) -> str:
        return (
            f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/"
            f"{self.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        )

    @cached_property
    def issuer(self) -> str:
        return (
            f"https://cognito-idp.{self.COGNITO_REGION}.amazonaws.com/"
            f"{self.COGNITO_USER_POOL_ID}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = CognitoSettings()
