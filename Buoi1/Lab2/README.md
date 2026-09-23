# Buổi 1 – Lab 2: Bảo mật trước khi commit – GitSecure

> **Môn:** Lập trình An ninh thông tin
> **Bài:** 1. Cơ sở lập trình bảo mật, kiểm tra đầu vào (mục 1.4)
> **Sinh viên:** Bùi Quang Thiện – 2387700065

---

## 1. Mục tiêu

Thiết kế và triển khai **GitSecure**, một Git **pre-commit hook** tự động kiểm tra mã nguồn
trước mỗi lần `git commit`, để phát hiện và **chặn** rủi ro bảo mật trước khi mã được đưa vào repository.

### Yêu cầu chức năng

| Yêu cầu | Cách GitSecure đáp ứng |
|---|---|
| Quét thông tin nhạy cảm (API key, mật khẩu, token hardcode) | `scan_sensitive()` dùng 5 regex |
| Phát hiện thông tin định danh bị cài cứng | Các mẫu `password`, `secret`, `token`, AWS Access Key |
| Quét lỗ hổng cơ bản bằng Bandit | `run_bandit()` quét cả repo, chặn khi có lỗi mức High |
| Kiểm tra quyền truy cập file | `check_permissions()` chặn file world-writable |
| Kiểm tra tuân thủ giấy phép | Chưa cài đặt (xem mục 8) |

### Yêu cầu kỹ thuật

- Tự động **ngăn commit** (`exit 1`) khi phát hiện bất kỳ vấn đề nào.
- Ghi chi tiết các phát hiện vào tệp log **`gitsecure.log`**.

## 2. Kiến thức nền

**Git hook** là script được Git tự chạy tại một thời điểm nhất định. **pre-commit** chạy
*trước khi* commit được tạo. Nếu script trả về mã thoát khác 0, Git **huỷ commit**.

```
git add  →  git commit  →  [pre-commit hook]  →  exit 0: tạo commit
                                              →  exit 1: COMMIT BLOCKED
```

Mặc định hook nằm trong `.git/hooks/`, thư mục này không được đưa lên repo. Lab dùng
`git config core.hooksPath` để trỏ Git tới thư mục hook **nằm trong repo**, nhờ vậy hook
được quản lý phiên bản và chia sẻ được cho cả nhóm.

## 3. Cấu trúc thư mục

```
Lab2/
├── .githooks/
│   └── pre-commit             # Script GitSecure (Python, có quyền thực thi)
├── pre-commit-hook-test/
│   └── bad.py                 # File mẫu để thử hook
└── requirements.txt           # bandit
```

File log `gitsecure.log` được tạo ở **thư mục gốc repo** (nơi Git chạy hook) và đã được thêm vào `.gitignore`.

## 4. Giải thích mã nguồn (`.githooks/pre-commit`)

### 4.1 Shebang

```python
#!/usr/bin/env python3
```

Dòng đầu tiên cho hệ điều hành biết phải chạy file bằng Python 3. Thiếu dòng này, hoặc
file không có quyền thực thi, thì Git sẽ không chạy được hook.

### 4.2 Mẫu thông tin nhạy cảm – `SENSITIVE_PATTERNS`

| Regex | Phát hiện |
|---|---|
| `apikey\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]` | API key dài từ 16 ký tự |
| `secret\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]` | Secret dài từ 8 ký tự |
| `password\s*=\s*['\"][^'\"]{4,}['\"]` | Mật khẩu gán cứng dài từ 4 ký tự |
| `token\s*=\s*['\"][A-Za-z0-9]{10,}['\"]` | Token dài từ 10 ký tự |
| `(AKIA\|ASIA)[A-Z0-9]{16}` | AWS Access Key ID |

Các mẫu được so khớp **không phân biệt hoa thường** (`re.IGNORECASE`).

### 4.3 Các hàm kiểm tra

| Hàm | Chức năng |
|---|---|
| `log(msg)` | Ghi một dòng `[thời gian] nội dung` vào `gitsecure.log` |
| `scan_sensitive(file_path)` | Đọc file, trả về thông báo nếu khớp một mẫu nhạy cảm |
| `check_permissions(file_path)` | Dùng `os.stat` kiểm tra bit `S_IWOTH` (ai cũng ghi được, ví dụ quyền 777). Bỏ qua trên Windows vì Windows không dùng quyền kiểu Unix |
| `run_bandit()` | Chạy `bandit -r . -x ./.venv` và chặn nếu kết quả có lỗi mức **High**. Nếu chưa cài Bandit thì cũng chặn và nhắc cài |
| `main()` | Lấy danh sách file đã `git add` (`git diff --cached --name-only`), chạy các kiểm tra trên từng file, chạy Bandit, rồi in kết quả, ghi log và `sys.exit(1)` nếu có phát hiện |

## 5. Cài đặt

Chạy tất cả lệnh từ **thư mục gốc repo**:

```bash
# 1. Cài Bandit (nên dùng venv)
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r Buoi1/Lab2/requirements.txt

# 2. Gắn hook vào Git
git config core.hooksPath Buoi1/Lab2/.githooks

# 3. Cấp quyền thực thi (Linux/macOS/Git Bash)
chmod +x Buoi1/Lab2/.githooks/pre-commit
```

`core.hooksPath` là cấu hình **cục bộ** của từng bản clone, nên sau khi clone repo sang máy
khác phải chạy lại bước 2. Venv phải được kích hoạt khi commit để hook tìm thấy lệnh `bandit`.

## 6. Kiểm thử

### 6.1 Trường hợp 1: commit chứa mật khẩu cứng (bị chặn)

Sửa `Buoi1/Lab2/pre-commit-hook-test/bad.py` thành một dòng gán mật khẩu cứng, tức biến
`password` bằng chuỗi `123456` đặt trong ngoặc kép (như trang 23 của tài liệu). Sau đó chạy:

```bash
git add Buoi1/Lab2/pre-commit-hook-test/bad.py
git commit -m "test"
```

Kết quả:

```
COMMIT BLOCKED by GitSecure:
 - Sensitive info found in Buoi1/Lab2/pre-commit-hook-test/bad.py: pattern password\s*=\s*['\"][^'\"]{4,}['\"]
```

Nội dung `gitsecure.log`:

```
[2026-09-23 13:40:06.586857] Sensitive info found in pre-commit-hook-test/bad.py: pattern password\s*=\s*['\"][^'\"]{4,}['\"]
```

### 6.2 Trường hợp 2: đã xoá mật khẩu (được commit)

Thay mật khẩu cứng bằng biến môi trường, đây là cách làm đúng:

```python
import os
password = os.environ.get("APP_PASSWORD")
```

```bash
git add . && git commit -m "[add] ..."
```

Kết quả:

```
GitSecure: All checks passed.
[main 70a8cc0] [add] lab 1: secure validator, githooks, secure logger
```

### 6.3 Trường hợp 3: file world-writable (bị chặn)

```bash
chmod 777 Buoi1/Lab2/pre-commit-hook-test/bad.py
git add . && git commit -m "test"
#  - File Buoi1/Lab2/pre-commit-hook-test/bad.py is world-writable!
chmod 644 Buoi1/Lab2/pre-commit-hook-test/bad.py   # cách khắc phục
```

### 6.4 Trường hợp 4: Bandit phát hiện lỗi mức High (bị chặn)

Ví dụ trong code Flask có `app.run(debug=True)` (Bandit B201, mức High):

```
COMMIT BLOCKED by GitSecure:
 - Bandit: High severity issues found.
```

Vì vậy các app trong repo chỉ bật debug qua biến môi trường `FLASK_DEBUG=1`.

### 6.5 Hook tự bảo vệ chính tài liệu

Khi viết README này, hook đã **chặn commit** vì trong README có dòng ví dụ gán mật khẩu cứng
giống hệt `bad.py`. Hook quét mọi file được commit, kể cả tài liệu, nên phần ví dụ ở mục 6.1
được mô tả bằng lời thay vì ghi nguyên văn.

## 7. Điểm đã điều chỉnh so với tài liệu hướng dẫn

| # | Vấn đề trong code gốc | Điều chỉnh |
|---|---|---|
| 1 | Kiểm tra `"SEVERITY: High" in result.stdout`, nhưng Bandit in ra `Severity: High`, nên **không bao giờ khớp** và Bandit không chặn được gì | So khớp bằng regex **không phân biệt hoa thường** |
| 2 | `bandit -r .` quét cả thư mục `.venv`, chậm và báo lỗi của thư viện bên thứ ba | Thêm `-x ./.venv` |
| 3 | `check_permissions` trả `False` trên Windows | Trả `None` để thống nhất với các hàm khác |
| 4 | Shebang `#!/usr/bin/env python` | Đổi thành `python3` vì nhiều bản Linux không có lệnh `python` |

## 8. Hạn chế và hướng cải tiến

- **Chưa kiểm tra giấy phép (license compliance):** có thể dùng `pip-licenses` để liệt kê giấy phép của các thư viện trong `requirements.txt` và chặn những giấy phép không được phép (ví dụ GPL trong dự án đóng).
- **`scan_sensitive` chỉ báo mẫu đầu tiên khớp** trong mỗi file và không kèm số dòng. Có thể quét từng dòng để báo đủ và chính xác hơn.
- **Regex dễ bị bỏ sót**, ví dụ khi mật khẩu nằm trong dict hoặc JSON (`"password": "..."`). Nên kết hợp công cụ chuyên dụng như **Gitleaks**, **detect-secrets** hoặc **TruffleHog**.
- **Hook phía client có thể bị bỏ qua** bằng `git commit --no-verify`. Cần thêm lớp kiểm tra phía server (GitHub Actions, secret scanning, pre-receive hook).
- Bandit quét **cả repo** ở mỗi lần commit. Với repo lớn, nên chỉ quét các file `.py` đã được stage.

## 9. Tài liệu tham khảo

- Git Hooks: https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks
- Bandit: https://bandit.readthedocs.io
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- Gitleaks: https://github.com/gitleaks/gitleaks
