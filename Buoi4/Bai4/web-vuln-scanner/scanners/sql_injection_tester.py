from urllib.parse import urlparse, parse_qs

class SQLInjectionTester:
    # Payload theo từng hệ quản trị CSDL, chỉ dùng chuỗi phát hiện không phá hủy
    payloads = {
        'Generic': [
            "' OR '1'='1",
            "\" OR 1=1--",
            "' UNION SELECT NULL--",
        ],
        'MySQL': [
            "' OR SLEEP(0)-- ",
            "' AND 1=1#",
        ],
        'PostgreSQL': [
            "' OR pg_sleep(0)--",
            "'; SELECT version()--",
        ],
        'MSSQL': [
            "' OR WAITFOR DELAY '0:0:0'--",
            "'; SELECT @@version--",
        ],
        'Oracle': [
            "' OR 1=1 FROM dual--",
            "' UNION SELECT NULL FROM dual--",
        ],
        'SQLite': [
            "' OR sqlite_version() IS NOT NULL--",
        ],
    }

    def scan(self, url):
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        for param, values in params.items():
            for val in values:
                for dbms, payloads in self.payloads.items():
                    for payload in payloads:
                        if payload in val:
                            findings.append({
                                'type': 'SQL Injection',
                                'param': param,
                                'payload': payload,
                                'dbms': dbms,
                                'url': url,
                                'desc': 'Potential SQL Injection',
                                'risk': 'Critical',
                                'remediation': 'Dùng truy vấn tham số hóa '
                                               '(prepared statement), không ghép '
                                               'trực tiếp đầu vào vào câu SQL.'
                            })
        return findings
