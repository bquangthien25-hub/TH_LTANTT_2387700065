# Buổi 1 – Lab 3: SecureLogger

Hệ thống ghi nhật ký ưu tiên bảo mật (mục 1.6), tích hợp với SecureValidator ở Lab 1
để ghi lại mọi lần validation qua API `POST /validate`.

## Tính năng

- Hỗ trợ đủ các cấp độ log: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log theo cấu trúc JSON
- Tự che PII: email thành `<email_masked>`, token/password thành `<token_masked>`
- Luân phiên log (tối đa 1 MB, giữ 2 bản) và nén `.gz`
- Phát hiện sửa đổi log: mỗi dòng có chữ ký SHA-256 trong `secure.log.sig`, kiểm tra bằng `verify_log_integrity()`

## Cấu trúc

```
Lab3/
├── app.py                 # Flask API POST /validate
├── requirements.txt
├── securelogger/
│   ├── __init__.py
│   └── logger.py
└── securevalidator/       # sao chép từ Lab1
```

## Chạy

```bash
cd Buoi1/Lab3
pip install -r requirements.txt
python app.py
```

Gửi request bằng Postman: **POST** `http://localhost:5000/validate`, Body chọn raw JSON:

```json
{
  "email": "phuoc@example.com",
  "url": "https://secure.com",
  "filename": "report.pdf",
  "sql": "' OR 1=1 --",
  "html": "<script>alert(1)</script>"
}
```

Response:

```json
{"email": true, "filename": true, "html": "&lt;script&gt;alert(1)&lt;/script&gt;", "sql": "1=1", "url": true}
```

`secure.log` sau request trên (email đã bị che):

```json
{"timestamp": "...Z", "level": "INFO", "message": "Validation check performed", "data": "{'email': '<email_masked>', 'url': 'https://secure.com', ...}", "results": "..."}
```

## Kiểm tra log có bị sửa

```bash
python -c "from securelogger.logger import verify_log_integrity as v; print(v())"
```

Kết quả `[]` nghĩa là log còn nguyên vẹn. Nếu có số dòng trong danh sách thì các dòng đó đã bị sửa.
