import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError

# RFC 7518 khuyến nghị khóa HMAC-SHA256 tối thiểu 256 bit (32 byte)
MIN_SECRET_BYTES = 32

class JWTValidator:
    def __init__(self, secret, algorithms=None):
        self.secret = secret
        self.algorithms = list(algorithms or ["HS256"])

    def validate(self, token: str):
        warnings = []
        if len(self.secret.encode()) < MIN_SECRET_BYTES:
            warnings.append(f"Khóa bí mật quá ngắn (< {MIN_SECRET_BYTES} byte), dễ bị brute force")

        try:
            header = jwt.get_unverified_header(token)
        except InvalidTokenError as e:
            return {"valid": False, "reason": str(e), "warnings": warnings}

        # Chặn alg=none và tấn công nhầm lẫn khóa (RS256 -> HS256)
        alg = header.get("alg")
        if alg not in self.algorithms:
            return {"valid": False, "warnings": warnings,
                    "reason": f"Thuật toán '{alg}' không được phép"}

        try:
            payload = jwt.decode(token, self.secret, algorithms=self.algorithms,
                                 options={"require": ["exp", "iat"]})
            return {"valid": True, "payload": payload, "warnings": warnings}
        except ExpiredSignatureError:
            return {"valid": False, "reason": "Token expired", "warnings": warnings}
        except InvalidSignatureError:
            return {"valid": False, "reason": "Invalid signature", "warnings": warnings}
        except InvalidTokenError as e:
            return {"valid": False, "reason": str(e), "warnings": warnings}
