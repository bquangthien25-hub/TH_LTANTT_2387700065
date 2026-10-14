import os
import sys

from api_gateway.gateway import APIGateway
from token_manager.manager import TokenManager

if __name__ == "__main__":
    # Khóa không được ghi trong mã nguồn: đặt bằng biến môi trường JWT_SECRET
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        sys.exit("Hãy đặt biến môi trường JWT_SECRET trước khi chạy")

    manager = TokenManager(secret)
    access_token, refresh_token = manager.generate_tokens("phuoc")

    print("Access Token:", access_token)
    print("Refresh Token:", refresh_token)

    gateway = APIGateway(secret)
    gateway.run()
