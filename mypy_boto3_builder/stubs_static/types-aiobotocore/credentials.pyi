"""
Type annotations for aiobotocore.credentials module.

Copyright 2025 Vlad Emelianov
"""

import logging
from typing import Any

from aiobotocore.client import AioBaseClient
from aiobotocore.config import AioConfig as AioConfig
from aiobotocore.session import AioSession
from aiobotocore.utils import AioContainerMetadataFetcher as AioContainerMetadataFetcher
from aiobotocore.utils import AioInstanceMetadataFetcher as AioInstanceMetadataFetcher
from botocore.credentials import (
    AssumeRoleCredentialFetcher,
    AssumeRoleProvider,
    AssumeRoleWithWebIdentityProvider,
    BaseAssumeRoleCredentialFetcher,
    BotoProvider,
    CachedCredentialFetcher,
    CanonicalNameCredentialSourcer,
    ConfigProvider,
    ContainerProvider,
    CredentialResolver,
    Credentials,
    EnvProvider,
    InstanceMetadataProvider,
    OriginalEC2Provider,
    ProcessProvider,
    ProfileProviderBuilder,
    ReadOnlyCredentials,
    RefreshableCredentials,
    SharedCredentialProvider,
    SSOProvider,
)
from botocore.tokens import SSOTokenProvider
from botocore.utils import SSOTokenLoader

logger: logging.Logger

def create_credential_resolver(
    session: AioSession,
    cache: Any | None = ...,
    region_name: str | None = ...,
) -> AioCredentialResolver: ...

class AioProfileProviderBuilder(ProfileProviderBuilder): ...

async def get_credentials(session: AioSession) -> AioCredentials | None: ...
def create_assume_role_refresher(client: AioBaseClient, params: Any) -> Any: ...
def create_mfa_serial_refresher(actual_refresh: Any) -> Any: ...
def create_aio_mfa_serial_refresher(actual_refresh: Any) -> Any: ...

class AioCredentials(Credentials):
    async def get_frozen_credentials(self) -> ReadOnlyCredentials: ...  # type: ignore[override]

class AioRefreshableCredentials(RefreshableCredentials):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    @property  # type: ignore[override]
    def access_key(self) -> str: ...
    @access_key.setter
    def access_key(self, value: str) -> None: ...
    @property  # type: ignore[override]
    def secret_key(self) -> str: ...
    @secret_key.setter
    def secret_key(self, value: str) -> None: ...
    @property  # type: ignore[override]
    def token(self) -> str: ...
    @token.setter
    def token(self, value: str) -> None: ...
    async def get_frozen_credentials(self) -> ReadOnlyCredentials: ...  # type: ignore[override]

class AioDeferredRefreshableCredentials(AioRefreshableCredentials):
    method: Any
    def __init__(self, refresh_using: Any, method: Any, time_fetcher: Any = ...) -> None: ...
    def refresh_needed(self, refresh_in: Any | None = ...) -> bool: ...

class AioCachedCredentialFetcher(CachedCredentialFetcher):
    async def fetch_credentials(self) -> Any: ...  # type: ignore[override]

class AioBaseAssumeRoleCredentialFetcher(
    BaseAssumeRoleCredentialFetcher, AioCachedCredentialFetcher
): ...
class AioAssumeRoleCredentialFetcher(
    AssumeRoleCredentialFetcher, AioBaseAssumeRoleCredentialFetcher
): ...

class AioAssumeRoleWithWebIdentityCredentialFetcher(AioBaseAssumeRoleCredentialFetcher):
    def __init__(
        self,
        client_creator: Any,
        web_identity_token_loader: Any,
        role_arn: str,
        extra_args: Any | None = ...,
        cache: Any | None = ...,
        expiry_window_seconds: Any | None = ...,
    ) -> None: ...

class AioProcessProvider(ProcessProvider):
    def __init__(self, *args: Any, popen: Any = ..., **kwargs: Any) -> None: ...
    async def load(self) -> AioCredentials: ...  # type: ignore[override]

class AioInstanceMetadataProvider(InstanceMetadataProvider):
    async def load(self) -> AioRefreshableCredentials: ...  # type: ignore[override]

class AioEnvProvider(EnvProvider):
    async def load(self) -> Any: ...  # type: ignore[override]

class AioOriginalEC2Provider(OriginalEC2Provider):
    async def load(self) -> AioCredentials: ...  # type: ignore[override]

class AioSharedCredentialProvider(SharedCredentialProvider):
    async def load(self) -> AioCredentials: ...  # type: ignore[override]

class AioConfigProvider(ConfigProvider):
    async def load(self) -> AioCredentials: ...  # type: ignore[override]

class AioBotoProvider(BotoProvider):
    async def load(self) -> AioCredentials: ...  # type: ignore[override]

class AioAssumeRoleProvider(AssumeRoleProvider):
    async def load(self) -> AioDeferredRefreshableCredentials: ...  # type: ignore[override]

class AioAssumeRoleWithWebIdentityProvider(AssumeRoleWithWebIdentityProvider):
    async def load(self) -> AioDeferredRefreshableCredentials: ...  # type: ignore[override]

class AioCanonicalNameCredentialSourcer(CanonicalNameCredentialSourcer):
    async def source_credentials(self, source_name: str) -> Any: ...  # type: ignore[override]

class AioContainerProvider(ContainerProvider):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    async def load(self) -> AioRefreshableCredentials: ...  # type: ignore[override]

class AioCredentialResolver(CredentialResolver):
    async def load_credentials(self) -> Any: ...  # type: ignore[override]

class AioSSOCredentialFetcher(AioCachedCredentialFetcher):
    def __init__(
        self,
        start_url: str,
        sso_region: str,
        role_name: str,
        account_id: str,
        client_creator: Any,
        token_loader: SSOTokenLoader | None = ...,
        cache: Any | None = ...,
        expiry_window_seconds: Any | None = ...,
        token_provider: SSOTokenProvider | None = ...,
        sso_session_name: str | None = ...,
    ) -> None: ...

class AioSSOProvider(SSOProvider):
    async def load(self) -> AioDeferredRefreshableCredentials: ...  # type: ignore[override]
