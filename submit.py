import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timezone

SIGNING_SECRET = b"hello-there-from-b12"
URL = "https://b12.io/apply/submission"

def iso8601_now():
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )

def main():
    action_run_link = (
        f"https://github.com/{os.environ['GITHUB_REPOSITORY']}"
        f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    )

    payload = {
        "action_run_link": action_run_link,
        "email": "halebdev@gmail.com",
        "name": "Barbara Hale",
        "repository_link": f"https://github.com/{os.environ['GITHUB_REPOSITORY']}",
        "resume_link": "www.linkedin.com/in/barbarahhale",
        "timestamp": iso8601_now(),
    }

    body = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")

    digest = hmac.new(SIGNING_SECRET, body, hashlib.sha256).hexdigest()
    signature_header = f"sha256={digest}"

    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": signature_header,
    }

    response = requests.post(URL, data=body, headers=headers)

    if response.status_code != 200:
        print("Submission failed:")
        print(response.status_code, response.text)
        raise SystemExit(1)

    result = response.json()

    if not result.get("success"):
        print("Submission unsuccessful:", result)
        raise SystemExit(1)

    print("Submission receipt:")
    print(result["receipt"])


if __name__ == "__main__":
    main()