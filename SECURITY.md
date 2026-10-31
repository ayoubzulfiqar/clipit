# Security Policy

The Clipit team takes security vulnerabilities seriously. We appreciate your efforts to responsibly disclose findings and will make every reasonable effort to acknowledge, triage, and resolve confirmed vulnerabilities promptly.

---

## Supported Versions

Only the latest active minor release receives ongoing security patches. We recommend all users and operators stay up to date with the latest release.

| Version | Supported          |
| ------- | ------------------ |
| 1.15.x  | :white_check_mark: |
| 1.14.x  | :x:                |
| < 1.14  | :x:                |

---

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues or discussions.**

To report a vulnerability:
1. Email full details to **[security@clipit.dev](mailto:security@clipit.dev)**.
2. If the issue is critical, include "[SECURITY VULNERABILITY]" in the email subject line.
3. Provide the following information in your report:
   - **Type of issue**: (e.g., Command injection, Directory traversal, SSRF, Broken authentication, Information disclosure).
   - **Affected component**: (e.g., CLI runner, Web Studio API, Zip importer, FFmpeg filter constructor).
   - **Detailed steps to reproduce**: Clear instructions, sample payload, or minimal proof-of-concept (PoC) script.
   - **Impact**: The potential consequences of exploiting the vulnerability in a production environment.
   - **Suggested remediation**: If you have identified a fix or code change.

### Response Targets & SLA

- **Initial Acknowledgement**: Within 48 hours of receipt.
- **Triage & Severity Assessment**: Within 5 business days.
- **Remediation & Patch Release**: Dependent on severity, typically within 14–30 business days.
- **Public Disclosure**: Coordinated disclosure after a fix has been verified and released to users.

---

## Threat Model & Security Architecture

Clipit processes user-supplied media files, network video URLs, and custom subtitles. Security safeguards built into the engine include:

### 1. Subprocess & Command Injection Defenses
- FFmpeg and external utility invocations use explicit argument lists (`subprocess.run(list_of_args)`), strictly avoiding `shell=True` to eliminate shell expansion vulnerabilities.
- Filter complex arguments (video aspect crops, ASS subtitle paths) are sanitized and escaped before compilation.

### 2. Path Traversal & Zip Slip Prevention
- Uploaded media and community `.clipit-pack` zip archives are validated using realpath boundaries (`os.path.realpath`) to ensure files cannot escape designated directories or overwrite system resources.

### 3. API Authentication & Webhooks
- API endpoints support token authentication (`CLIPIT_API_KEY`) via HTTP Bearer tokens and custom header validation.
- Webhook payloads are signed using HMAC-SHA256 digests (`X-Clipit-Signature: sha256=...`) to ensure tamper-proof delivery to downstream receivers.

### 4. Network Video Ingestion (SSRF Safeguards)
- Operators deploying Clipit as a public SaaS or multi-tenant service are advised to restrict outbound network access from worker nodes to local private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.169.254`).

---

## Safe Harbor Policy

We consider security research conducted under this policy to be authorized and will not initiate legal action against researchers who:
- Make a good faith effort to avoid privacy violations, data destruction, and service interruption.
- Give us reasonable time to remediate vulnerabilities before disclosing them publicly.
- Do not exploit vulnerabilities beyond the minimum necessary to demonstrate proof-of-concept.
- Comply with all applicable laws.

Thank you for helping keep Clipit and our community safe!
