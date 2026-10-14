from token_manager.manager import TokenManager
import jwt
import secrets

def test_token_creation_and_refresh():
    key = secrets.token_urlsafe(32)
    manager = TokenManager(key)
    access, refresh = manager.generate_tokens("user1")

    payload = jwt.decode(access, key, algorithms=["HS256"])
    assert payload["sub"] == "user1"
    assert payload["type"] == "access"

    new_access = manager.refresh_access_token(refresh)
    assert new_access is not None

def test_revoked_refresh_token_cannot_refresh():
    manager = TokenManager(secrets.token_urlsafe(32))
    _, refresh = manager.generate_tokens("user1")

    assert manager.revoke_refresh_token(refresh) is True
    assert manager.refresh_access_token(refresh) is None

def test_access_token_cannot_be_used_to_refresh():
    manager = TokenManager(secrets.token_urlsafe(32))
    access, _ = manager.generate_tokens("user1")
    assert manager.refresh_access_token(access) is None

def test_refresh_with_wrong_signature_returns_none():
    _, refresh = TokenManager(secrets.token_urlsafe(32)).generate_tokens("user1")
    assert TokenManager(secrets.token_urlsafe(32)).refresh_access_token(refresh) is None
