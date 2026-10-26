"""外部程序调用示例：只发送 question，最多等待 210 秒，不自动重试。"""

import argparse
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("question")
parser.add_argument("--url", default="http://127.0.0.1:8000/api/rag/ask")
args = parser.parse_args()
request = Request(
    args.url,
    data=json.dumps({"question": args.question}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urlopen(request, timeout=210) as response:
        print(json.dumps(json.load(response), ensure_ascii=False, indent=2))
except HTTPError as error:
    print(f"HTTP {error.code}: {error.read().decode('utf-8')}")
    raise SystemExit(1) from None
