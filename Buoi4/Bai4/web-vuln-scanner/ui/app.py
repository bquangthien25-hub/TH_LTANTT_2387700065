import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))

import requests
from flask import Flask, render_template, request
from scanners.xss_scanner import XSSScanner
from scanners.sql_injection_tester import SQLInjectionTester
from scanners.csrf_detector import CSRFDetector
from scanners.ssrf_tester import SSRFTester
from report.report_generator import ReportGenerator

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        options = request.form.getlist("scanner")
        results = []

        if "xss" in options:
            xss = XSSScanner()
            results.append(xss.scan(url))

        if "sql" in options:
            sql = SQLInjectionTester()
            results.append(sql.scan(url))

        if "csrf" in options:
            try:
                html = requests.get(url, timeout=5).text
            except requests.RequestException as e:
                # Không tải được trang thì không được kết luận là có/không có CSRF
                results.append([{'type': 'CSRF', 'url': url, 'risk': 'LOW',
                                 'desc': f'Không tải được trang để kiểm tra CSRF: {e}'}])
            else:
                csrf = CSRFDetector()
                results.append([csrf.scan(html) | {'url': url}])

        if "ssrf" in options:
            ssrf = SSRFTester()
            results.append(ssrf.scan(url))

        report = ReportGenerator().generate(results)
        return render_template("result.html", report=report)

    return render_template("index.html")

if __name__ == "__main__":
    # Chế độ debug (Werkzeug debugger) chỉ bật khi đặt FLASK_DEBUG=1
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
