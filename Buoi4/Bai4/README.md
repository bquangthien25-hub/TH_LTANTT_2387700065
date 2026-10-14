# Bài 4 – Bảo mật Web App và API

| | |
|---|---|
| **Môn học** | Lập trình An ninh thông tin |
| **Buổi** | 4 – Bảo mật Web App và API (mục 4.2, 4.4) |
| **Sinh viên** | Bùi Quang Thiện – 2387700065 |

## 1. Mục tiêu

Xây dựng hai bộ công cụ bằng Python:

- **web-vuln-scanner**: quét các lỗ hổng XSS, SQL Injection, CSRF, SSRF trên một URL và sinh báo cáo có gợi ý khắc phục.
- **jwt-security-tools**: kiểm tra tính hợp lệ của JWT, thử brute force khóa bí mật yếu, làm OAuth 2.0 client, quản lý vòng đời token và bảo vệ API bằng JWT.

Bộ công cụ được kiểm thử bằng `unittest` và `pytest`, chạy được bằng dòng lệnh và giao diện web.

## 2. Kỹ năng đạt được

| Kỹ năng | Áp dụng trong bài |
|---|---|
| Phát hiện XSS phản chiếu | `XSSScanner` gửi payload qua query string và kiểm tra payload có xuất hiện nguyên văn trong phản hồi |
| Phát hiện SQL Injection | `SQLInjectionTester` có payload theo MySQL, PostgreSQL, MSSQL, Oracle, SQLite và ghi rõ DBMS trong kết quả |
| Phát hiện CSRF | `CSRFDetector` tìm CSRF token trong HTML của trang được quét |
| Phát hiện SSRF | `SSRFTester` nhận diện tham số URL trỏ tới 127.0.0.1, localhost và dải IP private |
| Sinh báo cáo có gợi ý khắc phục | `ReportGenerator` gom kết quả, bỏ qua trang đã có CSRF token, mỗi lỗ hổng có `remediation` |
| Kiểm tra cấu trúc JWT | `JWTValidator` kiểm tra header `alg`, bắt buộc `exp` và `iat`, xác minh chữ ký, cảnh báo khóa yếu |
| Brute force khóa JWT yếu | `JWTCracker` đọc wordlist và thử các khóa song song bằng `ThreadPoolExecutor` |
| OAuth 2.0 Authorization Code | `OAuthClient` tạo URL xác thực và đổi `code` lấy token |
| Vòng đời token | `TokenManager` phát hành access token và refresh token, làm mới access token, thu hồi refresh token |
| Bảo vệ API bằng JWT | `APIGateway` (Flask) chỉ trả dữ liệu khi có Bearer token hợp lệ |
| Quản lý khóa bí mật | Khóa đọc từ biến môi trường `JWT_SECRET`, test dùng `secrets.token_urlsafe` |
| Viết unit test cho mã bảo mật | 11 test cho web scanner, 13 test cho JWT tools |

## 3. Chức năng

### 3.1 web-vuln-scanner

| Thành phần | Hàm chính | Cách hoạt động | Kết quả |
|---|---|---|---|
| `XSSScanner` | `scan(url)` | Gửi `<script>alert(1)</script>` và `'><svg/onload=alert(1)>` qua `?q=` | Payload phản chiếu nguyên văn: loại XSS, risk HIGH |
| `SQLInjectionTester` | `scan(url)` | Tìm payload trong giá trị tham số, theo từng DBMS | Loại SQL Injection, risk Critical, có `dbms` |
| `CSRFDetector` | `scan(html)` | Tìm `name="csrf_token"`, `_csrf`, `csrfmiddlewaretoken` | `csrf_protected: True` hoặc risk Medium |
| `SSRFTester` | `scan(url)` | Tìm 127.0.0.1, localhost, 10.x, 192.168.x, 172.16–31.x trong tham số | Loại SSRF, risk High |
| `ReportGenerator` | `generate(findings)` | Gom kết quả, bỏ qua `csrf_protected: True` | Danh sách lỗ hổng cho giao diện |

### 3.2 jwt-security-tools

| Thành phần | Hàm chính | Cách hoạt động |
|---|---|---|
| `JWTValidator` | `validate(token)` | Chặn `alg` không có trong danh sách (kể cả `none`), bắt buộc `exp`/`iat`, cảnh báo khóa dưới 32 byte |
| `JWTCracker` | `crack()` | Thử từng dòng trong wordlist bằng 10 luồng, trả về khóa đúng |
| `OAuthClient` | `get_auth_url(scope)`, `get_token(code)` | Tạo URL với `response_type=code`, đổi code lấy token (timeout 10 giây) |
| `TokenManager` | `generate_tokens`, `refresh_access_token`, `revoke_refresh_token` | Access token 15 phút, refresh token 24 giờ, mỗi token có `jti`, refresh token đã thu hồi không làm mới được |
| `APIGateway` | `/protected` | Đọc header `Authorization: Bearer`, trả `Access granted` hoặc 401 |

## 4. Kết quả thực hiện

### 4.1 Unit test

| Bộ test | Lệnh | Kết quả |
|---|---|---|
| web-vuln-scanner | `python -m unittest discover tests` | 11 tests, OK |
| jwt-security-tools | `pytest tests/` | 13 passed |

<img width="1394" height="444" alt="image" src="https://github.com/user-attachments/assets/0f6ef17e-9fb9-4c9d-9960-da10f2cb5ca8" />

### 4.2 Chạy chương trình chính

`web-vuln-scanner/main.py` quét một URL mẫu và in báo cáo. `jwt-security-tools/main.py` sinh token và chạy API Gateway tại cổng 5000:

```bash
export JWT_SECRET="<chuỗi bí mật từ 32 ký tự trở lên>"
python main.py
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:5000/protected
```

Kết quả: token hợp lệ trả về `{"message":"Access granted","user":"phuoc"}` (HTTP 200), token sai trả về `{"message":"Access denied"}` (HTTP 401).

### 4.3 Giao diện web

Chạy `python ui/app.py` trong `web-vuln-scanner`, mở `http://127.0.0.1:5000/` để nhập URL và chọn công cụ:

<img width="2533" height="688" alt="image" src="https://github.com/user-attachments/assets/e1e821a4-ba0d-4dc6-bdd0-46e6ffb6565c" />

Báo cáo quét trên trang mục tiêu có lỗ hổng phản chiếu. Mỗi mục có mô tả, mức độ rủi ro và gợi ý khắc phục:

<img width="2548" height="1159" alt="image" src="https://github.com/user-attachments/assets/c2ef15b7-7d29-4c38-aadf-68fb53f9a885" />

## 5. Tài liệu tham khảo

- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Server Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [RFC 7519 – JSON Web Token (JWT)](https://datatracker.ietf.org/doc/html/rfc7519)
- [RFC 7518 – JSON Web Algorithms (JWA)](https://datatracker.ietf.org/doc/html/rfc7518)
- [RFC 6749 – The OAuth 2.0 Authorization Framework](https://datatracker.ietf.org/doc/html/rfc6749)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
