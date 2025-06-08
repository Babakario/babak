import argparse
from vuln_scanner.utils.helpers import is_valid_url
from vuln_scanner.core.scanner import check_sql_injection
from vuln_scanner.core.gpt_analyzer import analyze_with_gpt # Import the new function

def main():
    parser = argparse.ArgumentParser(description="Automated Penetration Testing Panel")
    parser.add_argument("url", help="The target URL to scan (e.g., http://example.com?query=test).")
    args = parser.parse_args()

    target_url = args.url
    print(f"[*] Target URL: {target_url}")

    if not is_valid_url(target_url):
        print("[-] Invalid URL provided. Please enter a valid URL (e.g., http://example.com or https://example.com).")
        return

    print(f"[+] URL is valid. Starting scans...")

    # Perform SQL Injection Scan
    print(f"[*] Performing SQL Injection scan...")
    is_sqli_vulnerable, sqli_tested_url, sqli_findings = check_sql_injection(target_url)

    if is_sqli_vulnerable:
        print(f"[!!!] Potential SQL Injection vulnerability found!")
        print(f"  [-] Tested URL: {sqli_tested_url}")
        print(f"  [-] Findings: {', '.join(sqli_findings)}")
    else:
        print(f"[+] SQL Injection scan completed. No obvious vulnerabilities detected based on error patterns.")
        if sqli_findings:
             print(f"  [-] Details: {', '.join(sqli_findings)}")

    # GPT-4 analysis call
    print("[*] Getting GPT-4 analysis...")
    gpt_summary_prompt = f"Security scan of '{target_url}': SQLi vulnerable: {is_sqli_vulnerable}. Details: {', '.join(sqli_findings)}"
    analysis_result = analyze_with_gpt(gpt_summary_prompt)
    print(f"[+] GPT-4 Analysis: {analysis_result}")


if __name__ == "__main__":
    import os
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
         sys.path.insert(0, project_root)
    main()
