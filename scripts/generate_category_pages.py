#!/usr/bin/env python3
"""category/{분류}/index.html 프론트매터 페이지 생성"""
import json
from pathlib import Path
from collections import Counter
from urllib.parse import quote

ROOT = Path(__file__).parent.parent
DATA = json.loads((ROOT / "_rawdata" / "food.json").read_text(encoding="utf-8"))

counts = Counter(f["category"] for f in DATA)

for cat in sorted(counts):
    cnt = counts[cat]
    d = ROOT / "category" / cat
    d.mkdir(parents=True, exist_ok=True)

    content = f"""---
layout: category
title: {cat} 칼로리·영양성분
description: {cat} {cnt}개 음식의 칼로리와 영양성분을 확인하세요.
cat_name: {cat}
title_h1: {cat} ({cnt}개)
subtitle: {cat} 음식의 칼로리와 영양성분을 확인하세요.
---
"""
    (d / "index.html").write_text(content, encoding="utf-8")
    print(f"  {cat}: {cnt}개")

print(f"\n완료: {len(counts)}개 분류 페이지 생성")
