#!/usr/bin/env python3
"""
fetch_food.py - 전국통합식품영양성분정보(음식)표준데이터 수집

data.go.kr 표준데이터 다운로드(활용신청 불필요). 19,495개 음식·식품의
칼로리·탄단지·비타민·무기질 등 영양성분 정보.

사용법:
  python scripts/fetch_food.py
"""
import sys, json, time
from pathlib import Path
import requests

sys.stdout.reconfigure(encoding="utf-8")

PUBLIC_DATA_PK = "15100070"
SVC_TABLE = "tn_pubr_public_nutri_food_info_api"
COLUMNS = [
    "FOOD_CD", "FOOD_NM", "DATA_CD", "TYPE_NM", "FOOD_ORIGIN_NM",
    "FOOD_LV3_NM", "FOOD_LV4_NM", "FOOD_LV5_NM", "FOOD_LV6_NM", "FOOD_LV7_NM",
    "NUT_CON_SRTR_QUA", "ENERC", "WATER", "PROT", "FATCE", "ASH", "CHOCDF",
    "SUGAR", "FIBTG", "CA", "FE", "P", "K", "NAT", "VITA_RAE", "THIA", "RIBF",
    "NIA", "VITC", "VITD", "CHOLE", "FASAT", "FATRN", "SRC_NM", "SERV_SIZE",
    "REST_NM", "CRTR_YMD",
]
OUT_FILE = Path(__file__).parent.parent / "_rawdata" / "food_raw.json"
PER_PAGE = 20000


def fetch_page(page: int) -> list:
    params = [("publicDataPk", PUBLIC_DATA_PK)]
    params += [("colNmList", c) for c in COLUMNS]
    params += [
        ("totalCount", "99999"),
        ("svcTableNm", SVC_TABLE),
        ("perPage", str(PER_PAGE)),
        ("page", str(page)),
    ]
    resp = requests.get(
        "https://www.data.go.kr/download/standard.json",
        params=params, timeout=60,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return []
    return data


def main():
    print("=== 전국통합식품영양성분정보(음식)표준데이터 수집 시작 ===")
    all_items = []
    page = 1
    while True:
        items = fetch_page(page)
        if not items:
            break
        all_items.extend(items)
        print(f"  페이지 {page}: {len(items)}개 (누적 {len(all_items)})")
        if len(items) < PER_PAGE:
            break
        page += 1
        time.sleep(0.3)

    if not all_items:
        raise SystemExit("수집된 데이터가 없습니다.")

    if OUT_FILE.exists():
        existing = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        if len(all_items) < len(existing) * 0.5:
            raise SystemExit(
                f"수집 건수({len(all_items)}건)가 기존 데이터({len(existing)}건)의 절반 미만입니다. "
                "오류로 판단하여 저장을 중단합니다."
            )

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료: {OUT_FILE}")
    print(f"  총 {len(all_items)}개 음식 저장")


if __name__ == "__main__":
    main()
