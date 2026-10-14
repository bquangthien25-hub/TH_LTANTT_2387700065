import logging

import requests

logger = logging.getLogger(__name__)

class XSSScanner:
    def __init__(self):
        self.payloads = ["<script>alert(1)</script>",
                         "'><svg/onload=alert(1)>"]

    def scan(self, url):
        results = []
        for payload in self.payloads:
            test_url = f"{url}?q={payload}"
            try:
                resp = requests.get(test_url, timeout=5)
                if payload in resp.text:
                    results.append({
                        "type": "XSS",
                        "payload": payload,
                        "url": test_url,
                        "desc": "Reflected XSS: payload được phản chiếu không mã hóa",
                        "risk": "HIGH",
                        "remediation": "Mã hóa đầu ra (htmlspecialchars), "
                                       "bật Content Security Policy và tránh innerHTML."
                    })
            except requests.RequestException as e:
                logger.warning("Không gửi được request tới %s: %s", test_url, e)
        return results
