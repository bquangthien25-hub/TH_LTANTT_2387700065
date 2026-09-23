# Buổi 1 – Lab 2: GitSecure pre-commit hook

Pre-commit hook tự động kiểm tra mã nguồn trước mỗi lần `git commit` (mục 1.4).
Nếu phát hiện vấn đề, hook sẽ chặn commit và ghi chi tiết vào `gitsecure.log`.

## Cấu trúc

```
Lab2/
├── .githooks/pre-commit       # script hook (Python)
├── pre-commit-hook-test/bad.py
└── requirements.txt           # bandit
```

## Các kiểm tra

- **Thông tin nhạy cảm:** `apikey`, `secret`, `password`, `token` bị hardcode, AWS key (`AKIA…`/`ASIA…`)
- **Quyền file:** chặn file world-writable (bỏ qua trên Windows)
- **Bandit:** quét lỗ hổng trong toàn repo và chặn khi có lỗi mức High

## Cài đặt

Chạy từ thư mục gốc của repo:

```bash
pip install -r Buoi1/Lab2/requirements.txt
git config core.hooksPath Buoi1/Lab2/.githooks
chmod +x Buoi1/Lab2/.githooks/pre-commit
```

## Kiểm tra

Sửa `Buoi1/Lab2/pre-commit-hook-test/bad.py` thành một dòng gán mật khẩu cứng, tức biến
`password` bằng chuỗi `123456` đặt trong ngoặc kép (như trang 23 của tài liệu). Sau đó chạy:

```bash
git add . && git commit -m "test"
```

Kết quả:

```
COMMIT BLOCKED by GitSecure:
 - Sensitive info found in Buoi1/Lab2/pre-commit-hook-test/bad.py: pattern password\s*=\s*['\"][^'\"]{4,}['\"]
```

Sau khi thay mật khẩu bằng biến môi trường (`os.environ.get("APP_PASSWORD")`), commit lại
sẽ in ra `GitSecure: All checks passed.`

`gitsecure.log` đã được đưa vào `.gitignore`.
