# Buổi 1 – Lab 1: SecureValidator

Thư viện Python kiểm tra và làm sạch dữ liệu đầu vào (mục 1.2), kèm giao diện web Flask.
Có deploy lên Render.

**Demo:** https://th-ltantt-2387700065.onrender.com

## Cấu trúc

```
Lab1/
├── app.py                    # Flask app: form nhập liệu và hiển thị kết quả
├── requirements.txt          # Flask, gunicorn
├── securevalidator/
│   ├── __init__.py
│   └── core.py               # 5 hàm validate / sanitize
├── templates/index.html
├── tests/test_validators.py  # 10 unit test
├── Dockerfile                # dùng khi deploy Render
└── render.yaml
```

## Các hàm

| Hàm | Mục đích |
|---|---|
| `validate_email(email)` | Kiểm tra định dạng email, chống chèn mã |
| `validate_url(url)` | Chỉ cho phép `http`/`https` có host, chống SSRF cơ bản |
| `validate_filename(filename)` | Chặn `..`, `/`, `\` để chống path traversal |
| `sanitize_sql_input(input_str)` | Loại bỏ ký tự và từ khoá SQL nguy hiểm |
| `sanitize_html_input(html_str)` | Escape HTML để chống XSS |

## Chạy

```bash
cd Buoi1/Lab1
pip install -r requirements.txt
python -m unittest discover tests   # Ran 10 tests ... OK
python app.py                       # http://127.0.0.1:5000
```

## Kết quả kiểm thử

| Đầu vào | Kết quả |
|---|---|
| `hongphuoc@gmail.com` | Email hợp lệ |
| `user@@example..com` | Email không hợp lệ |
| `https://www.hutech.edu.vn` | URL hợp lệ |
| `ftp://example.com` | URL không hợp lệ |
| `report.pdf` | Tên file hợp lệ |
| `../../etc/passwd` | Tên file không hợp lệ |
| `' OR 1=1 --` | Đã lọc: `1=1` |
| `<script>alert("XSS")</script>` | `&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;` |

**Ghi chú khi chạy trên Render:** Cloudflare đứng trước Render nên chặn luôn các payload
`../../etc/passwd` và `' OR 1=1 --` trước khi tới app (trang "Blocked"). Đây là một lớp
bảo vệ bổ sung theo nguyên tắc Defense in Depth. Để minh hoạ trên Render, có thể dùng
`../secret.txt` và `admin' OR 'a'='a`.

## Deploy Render

| Field | Value |
|---|---|
| Root Directory | `Buoi1/Lab1` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
