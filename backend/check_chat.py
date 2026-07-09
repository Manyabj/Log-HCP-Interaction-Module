import json
import urllib.request
import urllib.error

url = "http://127.0.0.1:8000/chat"
body = json.dumps({"session_id": "test", "message": "hello"}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as res:
        print("status", res.status)
        print(res.read().decode())
except urllib.error.HTTPError as e:
    print("status", e.code)
    print(e.read().decode())
except Exception as e:
    import traceback
    traceback.print_exc()
