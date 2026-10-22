# -*- coding: utf-8 -*-
"""手順1：集計に使った元のページを、wiss.org と Internet Archive から raw/ に取得し直す。

元のページは論文の概要の全文などを含むので、リポジトリには入れていない。
pipeline/sources.json に、保存先と URL と、2026年10月22日に取得したときの SHA-256 を載せてある。
取得し直したページが当時と違う場合は、そのことを表示する（ページが更新された可能性がある）。

使い方: python3 pipeline/fetch_raw.py
"""
import hashlib, json, os, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sources = json.load(open(os.path.join(ROOT, "pipeline", "sources.json"), encoding="utf-8"))
same = changed = failed = 0
for s in sources:
    path = os.path.join(ROOT, s["path"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        req = urllib.request.Request(s["url"], headers={"User-Agent": "wiss-talk-stats (research; https://github.com/qurihara/wiss-talk-stats)"})
        body = urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print("取得できない:", s["url"], e); failed += 1; continue
    open(path, "wb").write(body)
    if hashlib.sha256(body).hexdigest() == s["sha256"]:
        same += 1
    else:
        changed += 1; print("当時と中身が違う:", s["path"], s["url"])
    time.sleep(0.5)  # 相手のサーバーに負担をかけないよう間をあける
print(f"取得 {same + changed} 件（当時と同じ {same} 件、違う {changed} 件）、取得できない {failed} 件")
