from jwt_validator.validator import JWTValidator
import jwt
import datetime
import secrets

def generate_token(secret, alg="HS256", exp_minutes=5):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {"sub": "test", "iat": now,
               "exp": now + datetime.timedelta(minutes=exp_minutes)}
    return jwt.encode(payload, secret, algorithm=alg)

def test_valid_token():
    secret = secrets.token_urlsafe(32)
    token = generate_token(secret)
    validator = JWTValidator(secret)
    result = validator.validate(token)
    assert result["valid"] is True
    assert result["payload"]["sub"] == "test"
    assert result["warnings"] == []

def test_invalid_signature():
    token = generate_token(secrets.token_urlsafe(32))
    validator = JWTValidator(secrets.token_urlsafe(32))
    result = validator.validate(token)
    assert result["valid"] is False

def test_weak_secret_is_warned():
    secret = "short"
    validator = JWTValidator(secret)
    result = validator.validate(generate_token(secret))
    assert result["valid"] is True
    assert any("quá ngắn" in w for w in result["warnings"])

def test_alg_none_is_rejected():
    token = jwt.encode({"sub": "test", "exp": 9999999999, "iat": 0},
                       key=None, algorithm="none")
    result = JWTValidator(secrets.token_urlsafe(32)).validate(token)
    assert result["valid"] is False
    assert "không được phép" in result["reason"]

def test_expired_token_is_rejected():
    secret = secrets.token_urlsafe(32)
    token = generate_token(secret, exp_minutes=-1)
    result = JWTValidator(secret).validate(token)
    assert result["valid"] is False
    assert result["reason"] == "Token expired"
