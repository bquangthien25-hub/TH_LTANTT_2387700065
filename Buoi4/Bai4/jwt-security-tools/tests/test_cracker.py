from jwt_cracker.cracker import JWTCracker
import jwt
import secrets
import tempfile

def test_crack_token():
    secret = secrets.token_urlsafe(16)
    token = jwt.encode({"sub": "test"}, secret, algorithm="HS256")

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write(f"wrongpass\n123456\n{secret}\n")
        f.seek(0)
        cracker = JWTCracker(token, f.name)
        found = cracker.crack()

    assert found == secret
