# Bài 5 – Phân tích và kiểm thử bảo mật

| | |
|---|---|
| **Môn học** | Lập trình An ninh thông tin |
| **Buổi** | 5 – Phân tích và kiểm thử bảo mật (mục 5.1 – 5.4) |
| **Sinh viên** | Bùi Quang Thiện – 2387700065 |

## 1. Mục tiêu

Xây dựng hai công cụ bằng Python:

- **sast-tool**: phân tích tĩnh (SAST) mã nguồn Python bằng cây cú pháp AST, so khớp mẫu và flake8. Kết quả xuất theo định dạng SARIF 2.1.0.
- **dast-tool**: giám sát tiến trình khi đang chạy (CPU, bộ nhớ, file mở, kết nối mạng), chạy lệnh trong thư mục cách ly và phơi kết quả qua API Flask.

## 2. Kỹ năng đạt được

| Kỹ năng | Áp dụng trong bài |
|---|---|
| Phân tích cây cú pháp (AST) | `ASTAnalyzer` duyệt `ast.walk()` để tìm lời gọi `eval()` |
| Pattern Matching | `VulnPatternMatcher` dùng regex tìm mật khẩu hardcode và `import pickle` |
| Hệ thống luật có thể mở rộng | `SecurityRuleEngine` đọc `rules/default_rules.json` và gán mức độ nghiêm trọng |
| Đánh giá chất lượng mã | `CodeQualityChecker` chạy flake8 và chuẩn hoá kết quả về cùng định dạng |
| Xuất báo cáo chuẩn | `SarifReporter` tạo file SARIF 2.1.0 bằng `sarif-om` |
| Giám sát tiến trình | `RuntimeMonitor` dùng `psutil` để lấy CPU, RSS và danh sách file đang mở |
| Phát hiện bất thường bộ nhớ | `MemoryAnalyzer` kiểm tra `gc.garbage` và giá trị vượt ngưỡng 2⁶³ |
| Giám sát mạng | `NetworkTrafficAnalyzer` đọc thống kê từ `psutil.net_io_counters` |
| Môi trường cách ly cơ bản | `VirtualSandbox` chạy lệnh trong thư mục tạm |
| Dựng API giám sát | `app.py` (Flask) với 4 endpoint GET và 1 endpoint POST |
| Viết unit test | 6 test cho SAST, 5 test cho DAST, dùng `unittest` |

## 3. Cấu trúc thư mục

```
Lab05/
├── README.md
├── images/                        # Ảnh minh hoạ cho README
├── sast-tool/
│   ├── requirements.txt
│   ├── examples/                  # vulnerable_01.py, vulnerable_02.py
│   ├── rules/default_rules.json   # Luật bảo mật và mức độ nghiêm trọng
│   ├── sast_tool/                 # ast_analyzer, vuln_pattern_matcher, security_rule_engine,
│   │                              # code_quality_checker, sarif_reporter, main
│   └── tests/                     # 5 file, 6 test
└── dast-tool/
    ├── requirements.txt
    ├── main.py                    # Chạy tất cả module trên tiến trình hiện tại
    ├── app.py                     # API Flask
    ├── runtime_monitor.py, memory_analyzer.py, network_traffic_analyzer.py,
    │   security_behavior_checker.py, virtual_sandbox.py
    └── tests/                     # 5 file, 5 test
```

## 4. Cách chạy

### 4.1 SAST-tool

```bash
cd sast-tool
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover tests
python -m sast_tool.main ./examples/vulnerable_01.py
```

Báo cáo được ghi vào `report.sarif` trong thư mục đang chạy. Mở file này bằng extension **SARIF Viewer** trong VS Code để xem danh sách issue.

### 4.2 DAST-tool

```bash
cd dast-tool
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests
python main.py
python app.py                      # giữ terminal này chạy
```

Ở terminal khác, gọi API:

```bash
curl http://127.0.0.1:5000/api/monitor
curl http://127.0.0.1:5000/api/memory
curl http://127.0.0.1:5000/api/network
curl http://127.0.0.1:5000/api/security
curl -X POST http://127.0.0.1:5000/api/sandbox \
     -H "Content-Type: application/json" \
     -d '{"command": "echo Hello Sandbox"}'
```

## 5. Kết quả thực hiện

### 5.1 SAST-tool

Unit test (6 test) và quét `vulnerable_02.py` (1 issue):

![Unit test SAST và quét vulnerable_02](images/sast_tests_and_vulnerable02.png)

Quét `vulnerable_01.py` cho ra 5 issue:

![Quét vulnerable_01 ra 5 issue](images/sast_vulnerable01_run.png)

| # | Issue | Nguồn phát hiện |
|---|---|---|
| 1 | Use of eval() is dangerous and should be avoided. | ASTAnalyzer |
| 2 | Hardcoded password detected. | VulnPatternMatcher |
| 3 | Usage of pickle module can be unsafe. | VulnPatternMatcher |
| 4 | F401 'pickle' imported but unused | CodeQualityChecker (flake8) |
| 5 | E402 module level import not at top of file | CodeQualityChecker (flake8) |

Mở báo cáo bằng SARIF Viewer:

![Cài extension SARIF Viewer](images/sast_sarif_viewer_installed.png)

![Kết quả trong SARIF Viewer](images/sast_sarif_results.png)

### 5.2 DAST-tool

`main.py` in ra thông tin của tiến trình hiện tại: PID, CPU, bộ nhớ, file đang mở, memory leak, overflow test, thống kê mạng, hàm nguy hiểm và kết quả sandbox.

![main.py: tiến trình, CPU, bộ nhớ, file mở, memory leak](images/dast_main_part1.png)

![main.py: overflow test, thống kê mạng, sandbox](images/dast_main_part2.png)

Kết quả các endpoint của Flask API:

![API /api/memory](images/dast_api_memory.png)

![API /api/security](images/dast_api_security.png)

![API /api/sandbox](images/dast_api_sandbox.png)

| Endpoint | Kết quả |
|---|---|
| `GET /api/memory` | `memory_leaks: "[]"`, `overflow_test: true` |
| `GET /api/security` | `suspicious_calls: ["os.system", "eval", "exec"]` |
| `POST /api/sandbox` | `stdout: "Hello Sandbox\n"`, `stderr: ""` |

## 6. Điều chỉnh so với tài liệu hướng dẫn

| Nội dung | Tài liệu | Bài làm | Lý do |
|---|---|---|---|
| Địa chỉ bind của Flask | `host="0.0.0.0"` | `host="127.0.0.1"` | `/api/sandbox` chạy shell command từ body của request. Nếu mở ra mạng, bất kỳ ai trong mạng cũng thực thi được lệnh trên máy. |
| Số issue của file mẫu | 8 issue (`vulnerable_01`) và 4 issue (`vulnerable_02`) | 5 issue và 1 issue | File mẫu viết theo PEP 8 (hai dòng trống giữa các hàm) nên flake8 không báo E302 và E305. |
| Cách gọi flake8 | Không nói rõ | Phải chạy khi venv đã được kích hoạt | `CodeQualityChecker` gọi `flake8` bằng tên lệnh, nên `flake8` phải có trong PATH. |

## 7. Hạn chế

- `ASTAnalyzer` chỉ phát hiện `eval()`. Trong `vulnerable_02.py` có `exec(code)` nhưng không được báo cáo.
- `VulnPatternMatcher` chỉ bắt mật khẩu viết dạng `password = "..."`.
- `SecurityBehaviorChecker` tìm chuỗi `os.system`, `eval`, `exec` trong chính file `security_behavior_checker.py`. Kết quả vì vậy không phản ánh hành vi thật của tiến trình đang chạy.
- `MemoryAnalyzer.check_memory_leaks()` chỉ đọc `gc.garbage`, nên thường trả về danh sách rỗng.
- Khi chạy trên Python 3.14, `jsonpickle` in ra `DeprecationWarning` về giá trị mặc định của `keys`. Kết quả không bị ảnh hưởng.

## 8. Tài liệu tham khảo

- [SARIF v2.1.0 – OASIS](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [Python `ast` module](https://docs.python.org/3/library/ast.html)
- [psutil documentation](https://psutil.readthedocs.io/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [sarif-om trên PyPI](https://pypi.org/project/sarif-om/)
