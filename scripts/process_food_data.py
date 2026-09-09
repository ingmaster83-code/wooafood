#!/usr/bin/env python3
"""
process_food_data.py - 원본 영양성분 데이터를 Jekyll 페이지 생성용 JSON으로 가공

입력: _rawdata/food_raw.json
출력: _rawdata/food.json (개별 페이지 생성용), search_index.json (검색/분류 목록용)

사용법:
  python scripts/process_food_data.py
"""
import json, re, hashlib, sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
RAW = ROOT / "_rawdata" / "food_raw.json"
OUT = ROOT / "_rawdata" / "food.json"
SEARCH_INDEX_OUT = ROOT / "search_index.json"


def make_slug(name: str, code: str) -> str:
    slug = re.sub(r"[^\w가-힣\s-]", "", name).strip()
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    h = hashlib.md5(f"{name}|{code}".encode("utf-8")).hexdigest()[:6]
    return f"{slug}-{h}" if slug else h


def num(v):
    """빈 값/'-' 는 빈 문자열로, 나머지는 그대로 문자열 반환(템플릿에서 != "" 로 체크)."""
    v = (v or "").strip()
    if v in ("", "-", "N/A"):
        return ""
    return v


def txt(v):
    """'해당없음' 등 사실상 빈 값을 나타내는 플레이스홀더 텍스트를 빈 문자열로 정규화."""
    v = (v or "").strip()
    if v in ("", "-", "해당없음", "해당사항없음"):
        return ""
    return v


def main():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    items = []
    seen_slugs = Counter()
    skipped = 0
    for d in raw:
        # 필드명 주의: Jekyll 내장 Page.name과 충돌하므로 "foodName" 사용
        food_name = (d.get("FOOD_NM") or "").strip()
        food_code = (d.get("FOOD_CD") or "").strip()
        if not food_name:
            skipped += 1
            continue

        slug = make_slug(food_name, food_code)
        seen_slugs[slug] += 1
        if seen_slugs[slug] > 1:
            slug = f"{slug}-{seen_slugs[slug]}"

        category = (d.get("FOOD_LV3_NM") or "").strip() or "기타"

        items.append({
            "foodName": food_name,
            "foodCode": food_code,
            "category": category,
            "subCategory": (d.get("FOOD_LV4_NM") or "").strip(),
            "origin": (d.get("FOOD_ORIGIN_NM") or "").strip(),
            "servSize": (d.get("SERV_SIZE") or "").strip(),
            "baseQty": (d.get("NUT_CON_SRTR_QUA") or "").strip(),
            "energy": num(d.get("ENERC")),
            "water": num(d.get("WATER")),
            "protein": num(d.get("PROT")),
            "fat": num(d.get("FATCE")),
            "ash": num(d.get("ASH")),
            "carb": num(d.get("CHOCDF")),
            "sugar": num(d.get("SUGAR")),
            "fiber": num(d.get("FIBTG")),
            "calcium": num(d.get("CA")),
            "iron": num(d.get("FE")),
            "phosphorus": num(d.get("P")),
            "potassium": num(d.get("K")),
            "sodium": num(d.get("NAT")),
            "vitaminA": num(d.get("VITA_RAE")),
            "thiamin": num(d.get("THIA")),
            "riboflavin": num(d.get("RIBF")),
            "niacin": num(d.get("NIA")),
            "vitaminC": num(d.get("VITC")),
            "vitaminD": num(d.get("VITD")),
            "cholesterol": num(d.get("CHOLE")),
            "satFat": num(d.get("FASAT")),
            "transFat": num(d.get("FATRN")),
            "source": txt(d.get("SRC_NM")),
            "company": txt(d.get("REST_NM")),
            "refDate": (d.get("CRTR_YMD") or "").strip(),
            "slug": slug,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    print(f"음식 {len(items)}개 저장 → {OUT}  (제외: {skipped}건)")

    cat_counts = Counter(i["category"] for i in items)
    print("\n분류별 수:")
    for c, cnt in cat_counts.most_common():
        print(f"  {c}: {cnt}개")

    index = [
        {
            "n": i["foodName"], "slug": i["slug"], "cat": i["category"],
            "kcal": i["energy"], "company": i["company"],
        }
        for i in items
    ]
    SEARCH_INDEX_OUT.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"\n검색 인덱스 {len(index)}건 저장 → {SEARCH_INDEX_OUT}")


if __name__ == "__main__":
    main()
