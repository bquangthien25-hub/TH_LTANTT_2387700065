# Buổi 1 – Lab 3: Ghi nhật ký ưu tiên bảo mật – SecureLogger

> **Môn:** Lập trình An ninh thông tin
> **Bài:** 1. Cơ sở lập trình bảo mật, kiểm tra đầu vào (mục 1.6)
> **Sinh viên:** Bùi Quang Thiện – 2387700065

---

## 1. Mục tiêu

Xây dựng hệ thống ghi nhật ký **SecureLogger** với các tính năng:

| Yêu cầu | Cách cài đặt |
|---|---|
| Hỗ trợ đa cấp độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL) | Dùng module `logging` chuẩn, logger đặt ở mức `DEBUG` |
| Tự phát hiện và che thông tin định danh cá nhân (PII) | `mask_pii()` dùng regex thay email, token, mật khẩu bằng nhãn `<…_masked>` |
| Luân phiên log (log rotation) kèm nén | `RotatingFileHandler` (1 MB, giữ 2 bản) kết hợp `GZipRotator` nén `.gz` |
| Phát hiện thay đổi trái phép (tamper detection) | Mỗi dòng log có một chữ ký SHA-256 trong `secure.log.sig`; `verify_log_integrity()` đối chiếu lại |
| Ghi nhật ký theo cấu trúc JSON | `JSONFormatter` ghi mỗi dòng là một object JSON |

**Tích hợp:** dùng lại thư viện **SecureValidator** (Lab 1) và ghi log **mọi lần kiểm tra
validation** qua API `POST /validate`.

## 2. Kiến thức nền

- **PII (Personally Identifiable Information):** dữ liệu dùng để nhận diện một người như email, số CCCD, số điện thoại, địa chỉ IP. Nếu ghi thô PII vào log thì ai đọc được log cũng đọc được PII, vi phạm nguyên tắc thu thập tối thiểu và các luật bảo vệ dữ liệu (GDPR, Nghị định 13/2023/NĐ-CP).
- **Log Injection:** kẻ tấn công chèn ký tự xuống dòng hoặc ký tự điều khiển vào dữ liệu để giả mạo thêm dòng log. Ghi log dạng **JSON** giúp chống lại vì `json.dumps` escape `\n` thành `\\n`, nên mỗi sự kiện luôn chỉ chiếm đúng một dòng.
- **Tamper detection:** kẻ tấn công thường sửa hoặc xoá log để che dấu vết. Lưu mã băm của từng dòng giúp phát hiện dòng nào đã bị sửa.

## 3. Cấu trúc thư mục

```
Lab3/
├── app.py                     # Flask API POST /validate
├── requirements.txt           # Flask
├── securelogger/
│   ├── __init__.py            # export get_secure_logger
│   └── logger.py              # SecureLogger
└── securevalidator/           # Sao chép từ Lab1
    ├── __init__.py
    └── core.py
```

Khi chạy, ứng dụng tạo thêm các file sau (đã có trong `.gitignore`):

| File | Nội dung |
|---|---|
| `secure.log` | Log hiện tại, mỗi dòng là một JSON |
| `secure.log.sig` | Mã băm SHA-256 của từng dòng log, theo đúng thứ tự |
| `secure.log.1.gz`, `secure.log.2.gz` | Các bản log cũ đã được luân phiên và nén |

## 4. Giải thích mã nguồn (`securelogger/logger.py`)

### 4.1 Cấu hình

```python
LOG_FILE = "secure.log"
SIGNATURE_FILE = "secure.log.sig"
MAX_LOG_SIZE = 1024 * 1024   # 1 MB thì luân phiên
BACKUP_COUNT = 2             # giữ tối đa 2 bản nén
```

### 4.2 Che PII – `mask_pii(text)`

```python
PII_PATTERNS = {
    "email": r'[\w\.-]+@[\w\.-]+\.\w+',
    "token": r'(?i)(token|apikey|key|password)\s*=\s*["\']?[\w\-]{8,}["\']?',
}
```

Mỗi đoạn khớp mẫu được thay bằng `<email_masked>` hoặc `<token_masked>`. Ví dụ:

| Trước | Sau |
|---|---|
| `login user=an@hutech.edu.vn password=SuperSecret123 apikey='abcd1234efgh'` | `login user=<email_masked> <token_masked> <token_masked>` |

Hàm được áp dụng cho `message` và cả các trường bổ sung `data`, `results`.

### 4.3 Ghi log JSON – `JSONFormatter`

Mỗi bản ghi trở thành một dòng JSON gồm `timestamp` (UTC, chuẩn ISO 8601), `level`,
`message`, và thêm `data`, `results` nếu được truyền qua `extra=`.

### 4.4 Luân phiên và nén – `GZipRotator`

Khi `secure.log` vượt 1 MB, `RotatingFileHandler` gọi `GZipRotator`: file cũ được nén thành
`secure.log.1.gz`, xoá bản gốc, rồi ghi tiếp vào một `secure.log` mới. Nén giúp tiết kiệm dung
lượng, còn giới hạn số bản giúp tránh bị đầy ổ đĩa (một dạng tấn công từ chối dịch vụ).

### 4.5 Chữ ký và kiểm tra toàn vẹn

```python
class SecureRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def emit(self, record):
        msg = self.format(record)
        super().emit(record)       # ghi dòng log
        append_signature(msg)      # ghi SHA-256 của đúng dòng đó vào .sig
```

`verify_log_integrity()` đọc lại từng dòng trong `secure.log`, băm lại và so với dòng tương
ứng trong `secure.log.sig`, rồi trả về danh sách số dòng không khớp. Danh sách rỗng `[]`
nghĩa là log còn nguyên vẹn.

### 4.6 API – `app.py`

| Tình huống | Hành vi | Log |
|---|---|---|
| JSON hợp lệ | Chạy 5 hàm SecureValidator, trả kết quả JSON | `INFO` – "Validation check performed", kèm `data` (đã che PII) và `results` |
| Body không phải JSON | Trả `400 {"error": "Invalid JSON format"}`, không để lộ chi tiết lỗi | `WARNING` – "Invalid JSON received", kèm body gốc |

## 5. Cài đặt và chạy

```bash
# Từ thư mục gốc repo
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
cd Buoi1/Lab3
pip install -r requirements.txt
python app.py                        # http://127.0.0.1:5000
```

## 6. Kiểm thử bằng Postman

1. Tạo request mới: **POST** `http://localhost:5000/validate`
2. Tab **Body**, chọn **raw**, kiểu **JSON**:

```json
{
  "email": "phuoc@example.com",
  "url": "https://secure.com",
  "filename": "report.pdf",
  "sql": "' OR 1=1 --",
  "html": "<script>alert(1)</script>"
}
```

3. Bấm **Send**. Response:

```json
{
  "email": true,
  "filename": true,
  "html": "&lt;script&gt;alert(1)&lt;/script&gt;",
  "sql": "1=1",
  "url": true
}
```

Có thể thử tương tự bằng `curl`:

```bash
curl -X POST http://localhost:5000/validate \
     -H "Content-Type: application/json" \
     -d '{"email":"phuoc@example.com","sql":"'"'"' OR 1=1 --"}'
```

### 6.1 Nội dung `secure.log`

Email `phuoc@example.com` đã bị che thành `<email_masked>`:

```json
{"timestamp": "2026-09-23T06:20:33.624103Z", "level": "INFO", "message": "Validation check performed", "data": "{'email': '<email_masked>', 'url': 'https://secure.com', 'filename': 'report.pdf', 'sql': \"' OR 1=1 --\", 'html': '<script>alert(1)</script>'}", "results": "{'email': True, 'url': True, 'filename': True, 'sql': '1=1', 'html': '&lt;script&gt;alert(1)&lt;/script&gt;'}"}
```

Request có body không phải JSON:

```json
{"timestamp": "2026-09-23T06:20:49.345814Z", "level": "WARNING", "message": "Invalid JSON received", "data": "b'not json'"}
```

### 6.2 Nội dung `secure.log.sig`

Mỗi dòng là mã băm SHA-256 của dòng log tương ứng:

```
2e96019331797bac6e5e7e30a00ba28ad157fcc2cd90ff44f1dcdda8345c58fd
```

### 6.3 Kiểm tra phát hiện sửa log

```bash
python -c "from securelogger.logger import verify_log_integrity as v; print(v())"
# []    → log nguyên vẹn
```

Sửa tay `secure.log`, ví dụ đổi `"INFO"` thành `"DEBUG"` để giả làm kẻ tấn công xoá dấu vết, rồi chạy lại:

```
# [1]   → phát hiện dòng 1 đã bị sửa
```

## 7. Điểm đã điều chỉnh so với tài liệu hướng dẫn

| # | Vấn đề trong code gốc | Điều chỉnh |
|---|---|---|
| 1 | `emit()` gọi `format()` hai lần (một lần tự gọi, một lần trong `super().emit`), mà mỗi lần lấy `datetime.utcnow()` khác nhau. Dòng được ký và dòng được ghi lệch nhau vài micro giây nên chữ ký **không bao giờ khớp** | Lấy timestamp từ `record.created`, là thời điểm tạo bản ghi và cố định cho cả hai lần format |
| 2 | `append_signature` ghi các mã băm nối liền nhau, không xuống dòng, nên không đối chiếu được | Mỗi mã băm nằm trên một dòng |
| 3 | Chỉ ghi chữ ký, chưa có hàm kiểm tra, nên chưa thật sự "phát hiện" được việc sửa log | Thêm `verify_log_integrity()` |
| 4 | `datetime.utcnow()` đã bị đánh dấu deprecated từ Python 3.12 | Dùng `datetime.fromtimestamp(..., timezone.utc)` |
| 5 | `app.run(debug=True)` | Chỉ bật debug khi `FLASK_DEBUG=1` |

## 8. Hạn chế và hướng cải tiến

- **SHA-256 thuần không chống được kẻ tấn công có quyền ghi cả hai file:** họ có thể sửa log rồi tính lại mã băm. Nên dùng **HMAC-SHA256** với khoá bí mật lưu ngoài máy chủ log, hoặc **hash chain** (mỗi mã băm gồm cả mã băm dòng trước) để phát hiện cả việc xoá dòng.
- **Che PII còn hạn chế:** mới che email và token/password. Nên bổ sung số điện thoại, số CCCD, số thẻ, địa chỉ IP. Mẫu `token` cũng che nhầm mọi khoá có chữ `key`.
- **Không che trường `sql` và `html`:** dữ liệu độc hại vẫn được ghi nguyên văn. Điều này hữu ích cho điều tra, nhưng người xem log bằng công cụ web cần escape khi hiển thị.
- **Luân phiên log và file `.sig`:** sau khi luân phiên, file `.sig` vẫn giữ chữ ký của log cũ. `verify_log_integrity()` chỉ đối chiếu phần chữ ký cuối tương ứng với `secure.log` hiện tại. Nên luân phiên cả file `.sig`.
- **Quyền file log:** trên máy chủ thật nên đặt quyền `600` và chỉ cho tài khoản chạy ứng dụng ghi vào log.

## 9. Tài liệu tham khảo

- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP Log Injection: https://owasp.org/www-community/attacks/Log_Injection
- Python `logging.handlers`: https://docs.python.org/3/library/logging.handlers.html
