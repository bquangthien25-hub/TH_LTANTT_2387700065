class ReportGenerator:
    def generate(self, findings_list):
        report = {'vulnerabilities': []}
        for findings in findings_list:
            if isinstance(findings, list):
                items = findings
            elif isinstance(findings, dict):
                items = [findings]
            else:
                continue
            for item in items:
                # Trang đã có CSRF token là kết quả an toàn, không phải lỗ hổng
                if item.get('csrf_protected') is True:
                    continue
                report['vulnerabilities'].append(item)
        return report
