import datetime
import uuid

import jwt

class TokenManager:
    def __init__(self, secret, algorithm="HS256", access_exp=15, refresh_exp=60*24):
        self.secret = secret
        self.algorithm = algorithm
        self.access_exp = access_exp
        self.refresh_exp = refresh_exp
        # Danh sách thu hồi (jti của refresh token). Lưu trong bộ nhớ nên mất khi tiến trình dừng.
        self._revoked = set()

    def _generate(self, payload, exp_minutes):
        now = datetime.datetime.now(datetime.timezone.utc)
        payload["iat"] = now
        payload["exp"] = now + datetime.timedelta(minutes=exp_minutes)
        payload["jti"] = str(uuid.uuid4())
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def generate_tokens(self, user_id):
        access_token = self._generate({"sub": user_id, "type": "access"}, self.access_exp)
        refresh_token = self._generate({"sub": user_id, "type": "refresh"}, self.refresh_exp)
        return access_token, refresh_token

    def refresh_access_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return None
        if payload.get("type") != "refresh" or payload.get("jti") in self._revoked:
            return None
        return self._generate({"sub": payload["sub"], "type": "access"}, self.access_exp)

    def revoke_refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return False
        jti = payload.get("jti")
        if payload.get("type") != "refresh" or not jti:
            return False
        self._revoked.add(jti)
        return True
