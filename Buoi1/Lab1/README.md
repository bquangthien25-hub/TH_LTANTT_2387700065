# Buổi 1 – Lab 1: Thư viện xác thực đầu vào SecureValidator

> **Môn:** Lập trình An ninh thông tin
> **Bài:** 1. Cơ sở lập trình bảo mật, kiểm tra đầu vào (mục 1.2)
> **Sinh viên:** Bùi Quang Thiện – 2387700065
> **Demo trực tuyến:** https://th-ltantt-2387700065.onrender.com

---

## 1. Mục tiêu

Xây dựng thư viện Python **SecureValidator** để kiểm tra (validation) và làm sạch (sanitization)
dữ liệu đầu vào, giúp ứng dụng chống lại các lỗ hổng phổ biến trong OWASP Top 10:

| Lỗ hổng | Hàm xử lý |
|---|---|
| Injection trong email | `validate_email()` |
| SSRF (Server-Side Request Forgery) | `validate_url()` |
| Path Traversal | `validate_filename()` |
| SQL Injection | `sanitize_sql_input()` |
| XSS (Cross-Site Scripting) | `sanitize_html_input()` |

Bài lab còn yêu cầu:
- Viết test case cho từng hàm, gồm cả dữ liệu hợp lệ và dữ liệu độc hại.
- Minh hoạ kết quả xử lý qua giao diện web (Flask).
- Deploy ứng dụng lên Render.

## 2. Công nghệ sử dụng

| Thành phần | Phiên bản | Vai trò |
|---|---|---|
| Python | 3.12+ (đã test trên 3.12 và 3.14) | Ngôn ngữ chính |
| Flask | 2.3.3 | Web framework cho giao diện demo |
| gunicorn | 21.2.0 | WSGI server khi chạy production (Render) |
| unittest | có sẵn trong Python | Kiểm thử đơn vị |
| Docker | – | Đóng gói ứng dụng để deploy lên Render |

Thư viện SecureValidator chỉ dùng module có sẵn của Python (`re`, `html`, `urllib.parse`, `os`),
không phụ thuộc thư viện ngoài.

## 3. Cấu trúc thư mục

```
Lab1/
├── app.py                     # Flask app: nhận form, gọi SecureValidator, trả kết quả
├── requirements.txt           # Flask==2.3.3, gunicorn==21.2.0
├── securevalidator/           # Thư viện SecureValidator
│   ├── __init__.py            #   export 5 hàm public
│   └── core.py                #   cài đặt 5 hàm validate / sanitize
├── templates/
│   └── index.html             # Giao diện form (Pico CSS)
├── tests/
│   └── test_validators.py     # 10 unit test
├── Dockerfile                 # Image để Render build và chạy
├── .dockerignore
└── render.yaml                # Cấu hình Render Blueprint (mục 1.2.3 – bước 5)
```

## 4. Giải thích mã nguồn

### 4.1 `validate_email(email) -> bool`

```python
pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
return re.fullmatch(pattern, email) is not None
```

- Dùng **whitelist**: chỉ cho phép chữ, số, `_`, `.`, `-` ở phần tên và phần domain, và bắt buộc có đuôi domain `.xxx`.
- `re.fullmatch` so khớp **toàn bộ chuỗi**, nên nếu email bị chèn thêm ký tự lạ như `<`, `>`, `'`, `;`, dấu cách hay xuống dòng thì email sẽ bị loại.
- Chặn được các chuỗi kiểu `x@y.com<script>` và `a@b.com\nBcc: victim@x.com` (email header injection).

### 4.2 `validate_url(url) -> bool`

```python
parsed = urllib.parse.urlparse(url)
return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
```

- Chỉ chấp nhận scheme `http` và `https`. Các scheme hay bị lợi dụng trong SSRF/XSS như `file://`, `ftp://`, `gopher://`, `javascript:`, `data:` đều bị loại.
- Bắt buộc URL phải có host (`netloc`), nên chuỗi như `https://` là không hợp lệ.
- Bọc trong `try/except` để mọi lỗi phân tích URL đều trả về `False`, đúng nguyên tắc *fail securely*.

### 4.3 `validate_filename(filename) -> bool`

```python
if ".." in filename or "/" in filename or "\\" in filename:
    return False
return os.path.basename(filename) == filename
```

- Loại mọi tên file có `..`, `/` hoặc `\`, nên kẻ tấn công không thể thoát ra khỏi thư mục cho phép (ví dụ `../../etc/passwd`, `..\windows\win.ini`).
- Kiểm tra thêm `basename(filename) == filename` để bảo đảm đầu vào chỉ là tên file, không kèm đường dẫn.

### 4.4 `sanitize_sql_input(input_str) -> str`

```python
sanitized = re.sub(r"(--|;|'|\"|#)", "", input_str)
sanitized = re.sub(r"\b(OR|AND|SELECT|INSERT|DELETE|UPDATE|DROP|UNION|WHERE)\b",
                   "", sanitized, flags=re.IGNORECASE)
return sanitized.strip()
```

- **Bước 1:** xoá các ký tự dùng để thoát chuỗi hoặc bắt đầu comment trong SQL: `--`, `;`, `'`, `"`, `#`.
- **Bước 2:** xoá các từ khoá SQL nguy hiểm, không phân biệt hoa thường. `\b` giúp chỉ xoá khi đó là một từ trọn vẹn, nên các từ như `ORDER` hay `Oregon` không bị ảnh hưởng.
- Kết quả là payload `' OR 1=1 --` chỉ còn lại `1=1` vô hại.

### 4.5 `sanitize_html_input(html_str) -> str`

```python
return html.escape(html_str)
```

- Chuyển `<`, `>`, `&`, `"` và `'` thành HTML entity (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#x27;`), để trình duyệt hiển thị chúng như văn bản thay vì chạy như mã.
- `<script>alert("XSS")</script>` trở thành `&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;`.

### 4.6 `app.py` – ứng dụng web

- Route `/` nhận cả `GET` (hiện form) và `POST` (xử lý form).
- Khi `POST`, app gọi 5 hàm với 5 ô tương ứng rồi render lại `index.html` kèm kết quả.
- Template dùng Jinja2, vốn **tự escape** mọi biến khi hiển thị. Nhờ vậy giá trị người dùng nhập được hiện lại trong ô input mà không gây XSS. Đây là một lớp bảo vệ thứ hai (Defense in Depth).
- Chế độ `debug` **chỉ bật khi đặt biến môi trường `FLASK_DEBUG=1`**. Bật debug khi deploy thật sẽ làm lộ Werkzeug debugger, cho phép thực thi mã từ xa. Bandit cũng đánh lỗi này ở mức High (B201).

## 5. Cài đặt và chạy

### 5.1 Cài đặt

```bash
# Từ thư mục gốc repo
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
cd Buoi1/Lab1
pip install -r requirements.txt
```

### 5.2 Chạy unit test

```bash
python -m unittest discover tests
```

### 5.3 Chạy giao diện web

```bash
python app.py                        # http://127.0.0.1:5000
FLASK_DEBUG=1 python app.py          # nếu cần bật debug khi phát triển
```

### 5.4 Chạy bằng Docker (tuỳ chọn)

```bash
docker build -t securevalidator .
docker run -p 10000:10000 securevalidator   # http://127.0.0.1:10000
```

## 6. Kiểm thử

### 6.1 Unit test (`tests/test_validators.py`)

| # | Test | Đầu vào | Mong đợi | Loại |
|---|---|---|---|---|
| 1 | `test_validate_email_valid` | `user@example.com` | `True` | Hợp lệ |
| 2 | `test_validate_email_invalid` | `user@@example..com` | `False` | Độc hại |
| 3 | `test_validate_url_valid` | `https://example.com` | `True` | Hợp lệ |
| 4 | `test_validate_url_invalid` | `ftp://example.com` | `False` | Độc hại |
| 5 | `test_validate_filename_valid` | `report.pdf` | `True` | Hợp lệ |
| 6 | `test_validate_filename_traversal` | `../../etc/passwd` | `False` | Độc hại |
| 7 | `test_sanitize_sql_input_injection` | `' OR 1=1 --` | không còn `'`, `--`, `OR` | Độc hại |
| 8 | `test_sanitize_sql_input_safe_text` | `hello world` | giữ nguyên | Hợp lệ |
| 9 | `test_sanitize_html_input_script` | `<script>alert("XSS")</script>` | `&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;` | Độc hại |
| 10 | `test_sanitize_html_input_safe_text` | `Hello World` | giữ nguyên | Hợp lệ |

Kết quả:

```
$ python -m unittest discover tests
 Running: test_sanitize_html_input_safe_text
 Running: test_sanitize_html_input_script
 ...
 Running: test_validate_url_valid
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

### 6.2 Minh hoạ trên giao diện web

**Bộ dữ liệu hợp lệ:**

| Ô | Đầu vào | Kết quả hiển thị |
|---|---|---|
| Email | `hongphuoc@gmail.com` | Email hợp lệ |
| URL | `https://www.hutech.edu.vn` | URL hợp lệ |
| Filename | `report.pdf` | Tên file hợp lệ |
| SQL Input | `hello world` | Đã lọc: `hello world` |
| HTML Input | `Hello World` | Đã mã hóa: `Hello World` |

**Bộ dữ liệu độc hại:**

| Ô | Đầu vào | Kết quả hiển thị |
|---|---|---|
| Email | `user@@example..com` | Email không hợp lệ |
| URL | `ftp://example.com` | URL không hợp lệ |
| Filename | `../../etc/passwd` | Tên file không hợp lệ |
| SQL Input | `' OR 1=1 --` | Đã lọc: `1=1` |
| HTML Input | `<script>alert("XSS")</script>` | Đã mã hóa: `&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;` |

### 6.3 Các trường hợp bổ sung

| Hàm | Đầu vào | Kết quả |
|---|---|---|
| `validate_email` | `x@y.com<script>` | `False` |
| `validate_url` | `javascript:alert(1)` | `False` |
| `validate_url` | `https://` (thiếu host) | `False` |
| `validate_filename` | `a..b.txt` | `False` |
| `sanitize_sql_input` | `admin' OR 'a'='a` | `admin  a=a` |
| `sanitize_sql_input` | `SELECT * FROM users; DROP TABLE users` | `* FROM users  TABLE users` |
| `sanitize_html_input` | `<img src=x onerror='alert(1)'>` | `&lt;img src=x onerror=&#x27;alert(1)&#x27;&gt;` |

## 7. Deploy lên Render

Ứng dụng được deploy dưới dạng **Docker Web Service** (gói Free).

| Thiết lập | Giá trị |
|---|---|
| Repository | `bquangthien25-hub/TH_LTANTT_2387700065` |
| Branch | `main` |
| Root Directory | *(để trống)* |
| Dockerfile Path | `./Buoi1/Lab1/Dockerfile` |
| Docker Build Context Directory | `Buoi1/Lab1` |
| Instance Type | Free |

Nội dung `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-10000} app:app"]
```

Render truyền cổng qua biến môi trường `PORT`, và gunicorn lắng nghe trên `0.0.0.0:$PORT`.
Log khi deploy thành công:

```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:10000
==> Your service is live 🎉
==> Available at your primary URL https://th-ltantt-2387700065.onrender.com
```

Nếu muốn deploy theo kiểu Python runtime như tài liệu, dùng: Root Directory `Buoi1/Lab1`,
Build Command `pip install -r requirements.txt`, Start Command `gunicorn app:app`.
File `render.yaml` trong thư mục này mô tả đúng cấu hình đó.

### Ghi chú: Cloudflare chặn payload trên Render

Render đặt **Cloudflare** phía trước mọi service. Khi gửi `../../etc/passwd` hoặc
`' OR 1=1 --` lên bản deploy, Cloudflare trả về trang **"Blocked"** ngay, request không tới
được ứng dụng. Đây là ví dụ thực tế cho nguyên tắc **Defense in Depth**: một lớp WAF ở
biên mạng bảo vệ thêm cho lớp validate trong code.

Để minh hoạ lớp validate của ứng dụng trên Render, có thể dùng payload nhẹ hơn:

| Ô | Đầu vào | Kết quả |
|---|---|---|
| Filename | `../secret.txt` | Tên file không hợp lệ |
| SQL Input | `admin' OR 'a'='a` | Đã lọc: `admin  a=a` |

## 8. Hạn chế và hướng cải tiến

Thư viện được viết theo đúng yêu cầu của lab, nhưng khi kiểm thử thêm còn một số hạn chế:

| Hàm | Hạn chế | Ví dụ | Hướng cải tiến |
|---|---|---|---|
| `validate_url` | Chưa chặn địa chỉ nội bộ, nên chỉ chống được SSRF ở mức cơ bản | `http://127.0.0.1`, `http://localhost:8080` và `http://169.254.169.254/latest/meta-data` (metadata cloud) đều hợp lệ | Phân giải host rồi dùng `ipaddress` để loại loopback, private, link-local; hoặc dùng whitelist domain |
| `validate_filename` | Chuỗi rỗng và file ẩn vẫn hợp lệ | `""`, `.env` | Kiểm tra độ dài > 0, chặn tên bắt đầu bằng `.`, whitelist phần mở rộng |
| `sanitize_sql_input` | Là **blacklist**: xoá cả dữ liệu hợp lệ mà vẫn có thể bị vượt qua | `Bob or Alice` thành `Bob  Alice`, `O'Brien` thành `OBrien` | Dùng **parameterized query** (`cursor.execute("... WHERE name = ?", (name,))`). Đây là cách OWASP khuyến nghị |
| `validate_email` | Regex đơn giản, loại cả email hợp lệ có dấu `+` | `user+tag@gmail.com` là `False` | Dùng thư viện `email-validator` |
| `sanitize_html_input` | Escape toàn bộ, không cho phép bất kỳ thẻ HTML nào | – | Khi cần giữ một số thẻ an toàn, dùng `bleach` với whitelist thẻ |

## 9. Điểm đã điều chỉnh so với tài liệu hướng dẫn

1. **`app.run(debug=True)` đổi thành `debug` theo biến `FLASK_DEBUG`**: tránh để lộ debugger và tránh bị hook GitSecure (Lab 2) chặn vì Bandit B201.
2. **Test `test_sanitize_html_input_safe_text`**: bản trong tài liệu thiếu `assertEqual`, đã bổ sung.
3. **Thêm `Dockerfile`**: service Render được tạo ở chế độ Docker nên cần file này để build.

## 10. Tài liệu tham khảo

- OWASP Input Validation Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html
- OWASP SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- OWASP XSS Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP SSRF Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- Render Docs – Docker: https://render.com/docs/docker
