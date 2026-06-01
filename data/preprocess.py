"""
============================================================
제9회 전국동시지방선거 기권율 예측 프로젝트
데이터 전처리 파이프라인

입력 파일 (DATA 디렉터리):
  중앙선거관리위원회_제8회_전국동시지방선거_개표결과_20220601.xlsx
  중앙선거관리위원회_제7회_전국동시지방선거_개표결과_20180613.xlsx
  02_성별_연령대별_투표율_구시군별_.xlsx
  202204_202204_연령별인구현황_월간.xlsx
  202604_202604_연령별인구현황_월간.xlsx
  제8회_전국동시지방선거_유권자의식조사_1차_.sav
  제8회_전국동시지방선거_유권자의식조사_2차_.sav
  제9회_유권자의식_조사.csv

출력 파일 (OUT 디렉터리):
  train_total.csv  — 250행 × 22컬럼 (Y=기권율_Y_pct 실측값, 결측 0건)
  predict_9th.csv  — 250행 × 22컬럼 (Y=NaN, 9회 설문 반영)
  두 파일 컬럼명·순서·dtype(float64) 완전 대칭
============================================================
"""

import os, warnings
import numpy as np
import pandas as pd
import pyreadstat

warnings.filterwarnings("ignore")


# ══════════════════════════════════════════════════════════
# 0. 경로 설정
# ══════════════════════════════════════════════════════════
DATA = "/data/raw"
OUT  = "/data/processed"
os.makedirs(OUT, exist_ok=True)

PATH_8TH     = f"{DATA}/중앙선거관리위원회_제8회_전국동시지방선거_개표결과_20220601.xlsx"
PATH_7TH     = f"{DATA}/중앙선거관리위원회_제7회_전국동시지방선거_개표결과_20180613.xlsx"
PATH_TURN    = f"{DATA}/02_성별_연령대별_투표율_구시군별_.xlsx"
PATH_POP22   = f"{DATA}/202204_202204_연령별인구현황_월간.xlsx"
PATH_POP26   = f"{DATA}/202604_202604_연령별인구현황_월간.xlsx"
PATH_SAV1    = f"{DATA}/제8회_전국동시지방선거_유권자의식조사_1차_.sav"
PATH_SAV2    = f"{DATA}/제8회_전국동시지방선거_유권자의식조사_2차_.sav"
# PATH_SURVEY9 = f"{DATA}/제9회_유권자의식_조사.csv"
PATH_SURVEY9_V2 = f"{DATA}/제9회_유권자의식_조사_v2.csv" 



# ══════════════════════════════════════════════════════════
# 1. 공통 상수
# ══════════════════════════════════════════════════════════

# 행정구역 법정명 변경 (7회 구 명칭 → 현행 명칭)
SIDO_NORM = {
    "강원도":   "강원특별자치도",
    "전라북도": "전북특별자치도",
}

# 8회 설문 SAV 시도 코드 → 시도명
SIDO_CODE_MAP = {
    1:"서울특별시",  2:"부산광역시",  3:"대구광역시",  4:"인천광역시",
    5:"광주광역시",  6:"대전광역시",  7:"울산광역시",  8:"세종특별자치시",
    9:"경기도",     10:"강원특별자치도", 11:"충청북도", 12:"충청남도",
    13:"전북특별자치도", 14:"전라남도", 15:"경상북도",
    16:"경상남도",  17:"제주특별자치도",
}

SIDO_LIST = list(SIDO_CODE_MAP.values()) + list(SIDO_NORM.keys())

# 연령대별 투표율 파일 시트명 → 시도명
SHEET_SIDO_MAP = {
    "서울":"서울특별시",  "부산":"부산광역시",  "대구":"대구광역시",
    "인천":"인천광역시",  "광주":"광주광역시",  "대전":"대전광역시",
    "울산":"울산광역시",  "세종":"세종특별자치시", "경기":"경기도",
    "강원":"강원특별자치도", "충북":"충청북도", "충남":"충청남도",
    "전북":"전북특별자치도", "전남":"전라남도", "경북":"경상북도",
    "경남":"경상남도",   "제주":"제주특별자치도",
}

AGE_LABELS = [
    "합계","18세","19세","20-24세","25-29세","30-34세","35-39세",
    "40-49세","50-59세","60-69세","70-79세","80세이상",
]

SAV_MISSING = [9999.0, 9997.0]

# 개표결과(공백없음) ↔ 인구파일(공백있음) 구시군명 불일치 매핑
POP_SGG_NAME_MAP = {
    ("경기도","고양시덕양구"):"고양시 덕양구",
    ("경기도","고양시일산동구"):"고양시 일산동구",
    ("경기도","고양시일산서구"):"고양시 일산서구",
    ("경기도","성남시분당구"):"성남시 분당구",
    ("경기도","성남시수정구"):"성남시 수정구",
    ("경기도","성남시중원구"):"성남시 중원구",
    ("경기도","수원시권선구"):"수원시 권선구",
    ("경기도","수원시영통구"):"수원시 영통구",
    ("경기도","수원시장안구"):"수원시 장안구",
    ("경기도","수원시팔달구"):"수원시 팔달구",
    ("경기도","안산시단원구"):"안산시 단원구",
    ("경기도","안산시상록구"):"안산시 상록구",
    ("경기도","안양시동안구"):"안양시 동안구",
    ("경기도","안양시만안구"):"안양시 만안구",
    ("경기도","용인시기흥구"):"용인시 기흥구",
    ("경기도","용인시수지구"):"용인시 수지구",
    ("경기도","용인시처인구"):"용인시 처인구",
    ("경상남도","창원시마산합포구"):"창원시 마산합포구",
    ("경상남도","창원시마산회원구"):"창원시 마산회원구",
    ("경상남도","창원시성산구"):"창원시 성산구",
    ("경상남도","창원시의창구"):"창원시 의창구",
    ("경상남도","창원시진해구"):"창원시 진해구",
    ("경상북도","포항시남구"):"포항시 남구",
    ("경상북도","포항시북구"):"포항시 북구",
    ("전북특별자치도","전주시덕진구"):"전주시 덕진구",
    ("전북특별자치도","전주시완산구"):"전주시 완산구",
    ("충청남도","천안시동남구"):"천안시 동남구",
    ("충청남도","천안시서북구"):"천안시 서북구",
    ("충청북도","청주시상당구"):"청주시 상당구",
    ("충청북도","청주시서원구"):"청주시 서원구",
    ("충청북도","청주시청원구"):"청주시 청원구",
    ("충청북도","청주시흥덕구"):"청주시 흥덕구",
}

# 9회 의식조사 권역 → 시도 매핑 (7개 권역 → 17개 시도)
REGION_SIDO_MAP = {
    "서울":           ["서울특별시"],
    "인천/경기":       ["인천광역시", "경기도"],
    "대전/세종/충청":   ["대전광역시", "세종특별자치시", "충청북도", "충청남도"],
    "광주/전라":       ["광주광역시", "전북특별자치도", "전라남도"],
    "대구/경북":       ["대구광역시", "경상북도"],
    "부산/울산/경남":   ["부산광역시", "울산광역시", "경상남도"],
    "강원/제주":       ["강원특별자치도", "제주특별자치도"],
}

# 설문 피처 5개 컬럼명 (train·predict 공통)
SURVEY_FEAT_COLS = [
    "기권의향률_pct", "정치무관심률_pct",
    "효능감_평균", "정책인지_평균", "공정선거인식_평균",
]

# 최종 피처 컬럼 (순서 고정)
SHARED_FEATURE_COLS = [
    "기권율_이전회_pct",      # 8회 기권율 (predict에서 X 피처)
    "투표율_이전회_pct",       # 8회 투표율
    "기권율_전전회_pct",       # 7회 기권율
    "투표율_전전회_pct",       # 7회 투표율
    "기권율_증가_pct",         # 7→8회 증가분
    "청년_20대_투표율_pct",    # 연령대별 투표율 (8회 기준)
    "장년_30-40대_투표율_pct",
    "중년_50-60대_투표율_pct",
    "고령_70대이상_투표율_pct",
    "세대격차_pct",            # 고령 - 청년 투표율
    "청년인구비율_pct",        # 인구 구조 (train=2022 / predict=2026)
    "장년인구비율_pct",
    "중년인구비율_pct",
    "고령인구비율_pct",
    "기권의향률_pct",          # 설문 (train=8회 SAV / predict=9회 CSV)
    "정치무관심률_pct",
    "효능감_평균",
    "정책인지_평균",
    "공정선거인식_평균",
]

ID_COLS    = ["시도명", "구시군명"]
TARGET_COL = "기권율_Y_pct"


# ══════════════════════════════════════════════════════════
# 2. 헬퍼 함수
# ══════════════════════════════════════════════════════════

def norm_sido(name: str) -> str:
    """시도명을 현행 법정명으로 정규화"""
    return SIDO_NORM.get(str(name).strip(), str(name).strip())


def split_region(full_name: str):
    """'서울특별시 종로구' → ('서울특별시', '종로구')"""
    full_name = str(full_name).strip()
    for sido in sorted(SIDO_LIST, key=len, reverse=True):
        if full_name.startswith(sido) and len(full_name) > len(sido):
            return sido, full_name[len(sido):].strip()
    return full_name, None


def replace_missing(df: pd.DataFrame) -> pd.DataFrame:
    """SAV 무응답 코드(9999, 9997) → NaN"""
    return df.replace(SAV_MISSING, np.nan)


def check_merge_quality(df: pd.DataFrame, probe_col: str,
                        threshold: float = 0.05, label: str = "") -> None:
    """left join 후 미매칭 비율 검증 (5% 초과 시 경고)"""
    miss = df[probe_col].isna().mean()
    icon = "✅" if miss <= threshold else "⚠️ "
    print(f"  [{icon}] {label}  미매칭: {miss:.1%}  (기준 {threshold:.0%})")
    if miss > threshold:
        print(df[df[probe_col].isna()][["시도명","구시군명"]].head(10).to_string(index=False))


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    결측 처리:
      1) 컬럼 결측률 30% 초과 → 삭제
      2) 잔여 결측 → 시도 평균 → 전국 평균 대체
    """
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    miss_rate = df[num_cols].isnull().mean()
    drop_cols = miss_rate[miss_rate > 0.30].index.tolist()
    if drop_cols:
        print(f"  → 결측 30% 초과 삭제: {drop_cols}")
        df = df.drop(columns=drop_cols)
        num_cols = [c for c in num_cols if c not in drop_cols]
    for col in num_cols:
        if df[col].isnull().any():
            sido_mean = df.groupby("시도명")[col].transform("mean")
            df[col]   = df[col].fillna(sido_mean).fillna(df[col].mean())
    return df


# ══════════════════════════════════════════════════════════
# 3. 모듈 A: 개표 결과 전처리
# ══════════════════════════════════════════════════════════

def load_election_8th(filepath: str) -> pd.DataFrame:
    """
    8회 개표결과 → 구시군별 기권율
    필터: 읍면동명 == '합계' (구시군 전체 집계 행)
    기권율 = 기권수 / 선거인수 × 100  (≠ 100 - 투표율, 무효투표 처리 차이)
    """
    
    df = pd.read_excel(filepath, sheet_name="시·도지사", header=0)
    mask = (df.iloc[:, 2] == "합계") & df.iloc[:, 0].notna()
    d = df[mask].iloc[:, [0, 1, 4, 5, -2, -1]].copy()
    d.columns = ["시도명","구시군명","선거인수_명","투표수_명","무효투표수_명","기권수_명"]
    for c in ["선거인수_명","투표수_명","무효투표수_명","기권수_명"]:
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",","").str.strip(), errors="coerce")
    d["시도명"]        = d["시도명"].apply(norm_sido)
    d["투표율_8회_pct"] = (d["투표수_명"] / d["선거인수_명"] * 100).round(2)
    d["기권율_8회_pct"] = (d["기권수_명"] / d["선거인수_명"] * 100).round(2)
    return (d.dropna(subset=["선거인수_명"])
             .drop_duplicates(subset=["시도명","구시군명"])
             .reset_index(drop=True))


def load_election_7th(filepath: str) -> pd.DataFrame:
    """
    7회 개표결과 → 구시군별 기권율
    필터: 읍면동명 == '계'  (8회는 '합계', 7회는 '계' 사용)
    시도명 정규화: 강원도→강원특별자치도, 전라북도→전북특별자치도
    """
    df = pd.read_excel(filepath, sheet_name="시·도지사", header=0)
    mask = (df.iloc[:, 4] == "계") & df.iloc[:, 3].notna()
    d = df[mask].iloc[:, [2, 3, 6, 7, -2, -1]].copy()
    d.columns = ["시도명","구시군명","선거인수_명_7회","투표수_명_7회","무효투표수_명_7회","기권수_명_7회"]
    for c in d.columns[2:]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["시도명"]        = d["시도명"].apply(norm_sido)
    d["투표율_7회_pct"] = (d["투표수_명_7회"] / d["선거인수_명_7회"] * 100).round(2)
    d["기권율_7회_pct"] = (d["기권수_명_7회"] / d["선거인수_명_7회"] * 100).round(2)
    return (d.dropna(subset=["선거인수_명_7회"])
             .drop_duplicates(subset=["시도명","구시군명"])
             .reset_index(drop=True))


# ══════════════════════════════════════════════════════════
# 4. 모듈 B: 연령대별 투표율 전처리
# ══════════════════════════════════════════════════════════

def load_age_turnout(filepath: str) -> pd.DataFrame:
    """
    02_성별_연령대별_투표율 → 구시군별 연령 투표율 + 파생변수

    파일 구조: 17개 시도 시트, header 없는 raw 형식
      col0: 구시군명 (새 구시군 시작 행에만 값, 나머지 NaN → forward-fill)
      col1: 성별 (합계/남자/여자)
      col2: 구분 (선거인수/투표자수/투표율)
      col3~14: 합계 + 연령대 12개 값
    수집 조건: 성별='합계' + 구분='투표율'인 행

    파생변수:
      청년(20대): (20-24세 + 25-29세) / 2
      장년(30-40대): (30-34세 + 35-39세 + 40-49세) / 3
      중년(50-60대): (50-59세 + 60-69세) / 2
      고령(70+): (70-79세 + 80세이상) / 2
      세대격차: 고령 - 청년
    """
    all_rows = []
    for sheet, sido_full in SHEET_SIDO_MAP.items():
        df = pd.read_excel(filepath, sheet_name=sheet, header=None)
        current_sgg = None
        current_gender = None
        for idx in range(4, len(df)):
            row = df.iloc[idx]
            v0  = row.iloc[0]
            v1  = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            v2  = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            if pd.notna(v0) and str(v0).strip() not in ("","nan","전체"):
                current_sgg = str(v0).strip()
            if v1 in ("합계","남자","여자"):
                current_gender = v1
            if v2 == "투표율" and current_sgg and current_gender == "합계":
                rec = {"시도명": sido_full, "구시군명": current_sgg}
                for ci, col_name in enumerate(AGE_LABELS):
                    val = row.iloc[3+ci] if (3+ci) < len(row) else np.nan
                    rec[f"투표율_{col_name}"] = pd.to_numeric(val, errors="coerce")
                all_rows.append(rec)

    df_age = pd.DataFrame(all_rows)
    df_age["청년_20대_투표율_pct"]   = (df_age["투표율_20-24세"] + df_age["투표율_25-29세"]) / 2
    df_age["장년_30-40대_투표율_pct"] = (df_age["투표율_30-34세"] + df_age["투표율_35-39세"] + df_age["투표율_40-49세"]) / 3
    df_age["중년_50-60대_투표율_pct"] = (df_age["투표율_50-59세"] + df_age["투표율_60-69세"]) / 2
    df_age["고령_70대이상_투표율_pct"] = (df_age["투표율_70-79세"] + df_age["투표율_80세이상"]) / 2
    df_age["세대격차_pct"]            = (df_age["고령_70대이상_투표율_pct"] - df_age["청년_20대_투표율_pct"]).round(2)
    return df_age


# ══════════════════════════════════════════════════════════
# 5. 모듈 C: 인구 데이터 전처리 (공통 파서)
# ══════════════════════════════════════════════════════════

def _parse_population_file(filepath: str) -> pd.DataFrame:
    """
    연령별인구현황_월간.xlsx 공통 파서 (2022·2026 동일 구조)

    처리:
      - 행정기관명 → 시도명 + 구시군명 분리
      - 구시군 행만 유지
      - 인구 비율 파생 (절대값 대신 비율 사용, 대도시 편향 방지)
      - POP_SGG_NAME_MAP으로 개표결과 구시군명과 통일

    인구비율 파생:
      청년(20대), 장년(30·40대), 중년(50·60대), 고령(70·80대)
    """
    df_raw = pd.read_excel(filepath, header=None)
    df = df_raw.iloc[4:].copy()
    col_names = [
        "행정기관코드","행정기관","총인구수","연령구간인구수",
        "인구_0-9세","인구_10-19세","인구_20-29세","인구_30-39세",
        "인구_40-49세","인구_50-59세","인구_60-69세","인구_70-79세",
        "인구_80-89세","인구_90-99세","인구_100세이상",
        "남_인구수","남_연령구간","남_0-9세","남_10-19세","남_20-29세",
        "남_30-39세","남_40-49세","남_50-59세","남_60-69세","남_70-79세",
        "남_80-89세","남_90-99세","남_100세이상",
        "여_인구수","여_연령구간","여_0-9세","여_10-19세","여_20-29세",
        "여_30-39세","여_40-49세","여_50-59세","여_60-69세","여_70-79세",
        "여_80-89세","여_90-99세","여_100세이상",
    ]
    df.columns = col_names
    for c in col_names[2:]:
        df[c] = pd.to_numeric(df[c].astype(str).str.replace(",","").str.strip(), errors="coerce")

    regions = df["행정기관"].apply(split_region)
    df["시도명"]      = regions.apply(lambda x: norm_sido(x[0]))
    df["구시군명_raw"] = regions.apply(lambda x: x[1])

    df_sgg = df[df["구시군명_raw"].notna() & (df["구시군명_raw"] != "")].copy()
    tot = df_sgg["총인구수"]
    df_sgg["청년인구비율_pct"] = (df_sgg["인구_20-29세"] / tot * 100).round(2)
    df_sgg["장년인구비율_pct"] = ((df_sgg["인구_30-39세"] + df_sgg["인구_40-49세"]) / tot * 100).round(2)
    df_sgg["중년인구비율_pct"] = ((df_sgg["인구_50-59세"] + df_sgg["인구_60-69세"]) / tot * 100).round(2)
    df_sgg["고령인구비율_pct"] = ((df_sgg["인구_70-79세"] + df_sgg["인구_80-89세"]) / tot * 100).round(2)

    result = df_sgg[["시도명","구시군명_raw",
                     "청년인구비율_pct","장년인구비율_pct",
                     "중년인구비율_pct","고령인구비율_pct"]].rename(
        columns={"구시군명_raw":"구시군명"}).drop_duplicates(
        subset=["시도명","구시군명"]).reset_index(drop=True)

    # 인구파일 구시군명 → 개표결과 구시군명으로 역매핑
    reverse_map = {(s,pn):en for (s,en),pn in POP_SGG_NAME_MAP.items()}
    result["구시군명"] = result.apply(
        lambda r: reverse_map.get((r["시도명"],r["구시군명"]), r["구시군명"]), axis=1)
    return result


def load_population_2022(filepath): return _parse_population_file(filepath)
def load_population_2026(filepath): return _parse_population_file(filepath)


# ══════════════════════════════════════════════════════════
# 6. 모듈 D: 8회 설문 집계 (train 전용)
# ══════════════════════════════════════════════════════════

def load_survey_8th(path1: str, path2: str) -> pd.DataFrame:
    """
    8회 1·2차 설문(D-30 컷오프 내, 선거 전 수집) → 시도별 집계
    3차(선거 후) 제외: D-30 컷오프 원칙 (미래 정보 오염 방지)

    문항 정의:
      1차 Q1: 관심도 (3·4=무관심) → 정치무관심률
      1차 Q2: 투표의향 (3·4=기권) → 기권의향률
      1차 Q6_1~3: 민주주의 효능감 (1~5점, 6=모름→NaN)
      2차 Q2: 투표의향 (동일)
      2차 Q6: 정책공약 인지도 (1=매우잘앎 ~ 4=전혀모름)
      2차 Q9_1~3: 효능감 (1차와 동일 구성, 문항 번호만 다름)
      2차 Q10: 공정선거인식 (1=매우깨끗 ~ 4=매우혼탁)

    집계 단위: 시도 (구시군 단위는 표본 수 부족)
    브로드캐스트: 시도값 → 해당 시도 구시군 전체 적용
    """
    df1, _ = pyreadstat.read_sav(path1)
    df1 = replace_missing(df1)
    df1["시도명"]     = df1["SQ1"].map(SIDO_CODE_MAP)
    df1["기권의향"]   = df1["Q2"].isin([3.0, 4.0]).astype(float)
    df1["정치무관심"] = df1["Q1"].isin([3.0, 4.0]).astype(float)
    df1["효능감_1차"] = df1[["Q6_1","Q6_2","Q6_3"]].mean(axis=1)

    df2, _ = pyreadstat.read_sav(path2)
    df2 = replace_missing(df2)
    df2["시도명"]       = df2["SQ1"].map(SIDO_CODE_MAP)
    df2["기권의향_2차"] = df2["Q2"].isin([3.0, 4.0]).astype(float)
    df2["효능감_2차"]   = df2[["Q9_1","Q9_2","Q9_3"]].mean(axis=1)
    df2["정책인지"]     = df2["Q6"]
    df2["공정선거인식"] = df2["Q10"]

    s1 = df1.groupby("시도명", as_index=False).agg(
        기권의향률_1차=("기권의향","mean"),
        정치무관심률  =("정치무관심","mean"),
        효능감_1차    =("효능감_1차","mean"),
    )
    s2 = df2.groupby("시도명", as_index=False).agg(
        기권의향률_2차    =("기권의향_2차","mean"),
        효능감_2차        =("효능감_2차","mean"),
        정책인지_평균     =("정책인지","mean"),
        공정선거인식_평균 =("공정선거인식","mean"),
    )
    sv = s1.merge(s2, on="시도명", how="outer")
    sv["기권의향률_pct"]   = ((sv["기권의향률_1차"] + sv["기권의향률_2차"]) / 2 * 100).round(2)
    sv["정치무관심률_pct"] = (sv["정치무관심률"] * 100).round(2)
    sv["효능감_평균"]       = ((sv["효능감_1차"] + sv["효능감_2차"]) / 2).round(2)
    sv["정책인지_평균"]     = sv["정책인지_평균"].round(2)
    sv["공정선거인식_평균"] = sv["공정선거인식_평균"].round(2)
    return sv[["시도명"] + SURVEY_FEAT_COLS]


# ══════════════════════════════════════════════════════════
# 7. 모듈 E: 9회 의식조사 설문 피처 교체 (predict 전용)
# ══════════════════════════════════════════════════════════

def _pct_to_likert5(pct: float) -> float:
    """
    % → 1~5점 리커트 선형 변환 (효능감용)
    - 9회 CSV: 긍정 응답 비율(%) / 8회 SAV: 1~5점 (방향 동일)
    - 0% → 1점, 100% → 5점
    - 검증: 전체 72.4% → 3.90점 ≈ 8회 전국 평균 3.88점
    """
    return round(1 + (pct / 100) * 4, 2)


def _pct_to_likert4_inv(pct: float) -> float:
    """
    % → 1~4점 리커트 역방향 변환 (정책인지, 공정선거인식용)
    - 9회 CSV: 긍정 비율(%) 높을수록 좋음
    - 8회 SAV: 1=좋음, 4=나쁨 (방향 반대)
    - 100% → 1점(최상), 0% → 4점(최하)
    """
    return round(4 - (pct / 100) * 3, 2)


def build_survey_9th(survey_path: str) -> pd.DataFrame:
    """
    제9회_유권자의식_조사.csv → 시도별 설문 피처 DataFrame

    처리:
      1) 권역별 행 추출 (연령별 행 제외)
      2) 척도 변환:
         기권의향률, 정치무관심률 → % 그대로
         효능감 → pct_to_likert5 (% → 1~5점)
         정책인지, 공정선거인식 → pct_to_likert4_inv (% → 1~4점 역방향)
      3) 권역 → 시도 전개 (7권역 → 17시도)
    """
    df9 = pd.read_csv(survey_path, encoding="utf-8-sig")
    rdf = df9[df9["집단구분"] == "권역별"].copy()
    rdf = rdf.rename(columns={"세부집단": "권역"})

    rdf["기권의향률_pct"]   = rdf["기권의향률_pct"].round(2)
    rdf["정치무관심률_pct"] = rdf["정치무관심률_pct"].round(2)
    rdf["효능감_평균"]       = rdf["효능감_평균"].apply(_pct_to_likert5)
    rdf["정책인지_평균"]     = rdf["정책인지_평균"].apply(_pct_to_likert4_inv)
    rdf["공정선거인식_평균"] = rdf["공정선거인식_평균"].apply(_pct_to_likert4_inv)

    rows = []
    for _, row in rdf.iterrows():
        for sido in REGION_SIDO_MAP.get(row["권역"], []):
            rows.append({
                "시도명":             sido,
                "기권의향률_pct":     row["기권의향률_pct"],
                "정치무관심률_pct":   row["정치무관심률_pct"],
                "효능감_평균":         row["효능감_평균"],
                "정책인지_평균":       row["정책인지_평균"],
                "공정선거인식_평균":   row["공정선거인식_평균"],
            })
    return pd.DataFrame(rows)


def replace_survey_features(predict: pd.DataFrame,
                             survey9: pd.DataFrame) -> pd.DataFrame:
    """
    predict의 설문 피처 5개를 9회 의식조사 값으로 교체
    - 기존 설문 컬럼 제거 → 9회 값으로 merge → 컬럼 순서 복원
    """
    original_cols = list(predict.columns)
    pred_new = predict.drop(columns=SURVEY_FEAT_COLS)
    pred_new = pred_new.merge(
        survey9[["시도명"] + SURVEY_FEAT_COLS],
        on="시도명", how="left"
    )
    pred_new = pred_new[original_cols]
    for col in SURVEY_FEAT_COLS:
        pred_new[col] = pred_new[col].astype("float64")
    return pred_new


# ══════════════════════════════════════════════════════════
# 8. 공통: 컬럼 정렬 + dtype 표준화
# ══════════════════════════════════════════════════════════

def align_and_finalize(df_train: pd.DataFrame,
                       df_pred:  pd.DataFrame) -> tuple:
    """
    두 파일을 SHARED_FEATURE_COLS 기준 순서로 정렬 + float64 강제
    sklearn 호환 보장
    """
    final_cols = ID_COLS + SHARED_FEATURE_COLS + [TARGET_COL]
    for df in [df_train, df_pred]:
        for col in final_cols:
            if col not in df.columns:
                df[col] = np.nan
    df_train = df_train[final_cols].copy()
    df_pred  = df_pred[final_cols].copy()
    for col in SHARED_FEATURE_COLS:
        df_train[col] = df_train[col].astype("float64")
        df_pred[col]  = df_pred[col].astype("float64")
    return df_train, df_pred


# ══════════════════════════════════════════════════════════
# 9. 메인 파이프라인
# ══════════════════════════════════════════════════════════

def run_pipeline():
    print("=" * 62)
    print("  기권율 예측 전처리 파이프라인 (최종 통합본)")
    print("=" * 62)

    # ── Step 1: 개표 결과
    print("\n[Step 1] 개표 결과 로드...")
    df8 = load_election_8th(PATH_8TH)
    df7 = load_election_7th(PATH_7TH)
    df_election = df8.merge(
        df7[["시도명","구시군명","투표율_7회_pct","기권율_7회_pct"]],
        on=["시도명","구시군명"], how="left")
    df_election["기권율_증가_pct"] = (
        df_election["기권율_8회_pct"] - df_election["기권율_7회_pct"]).round(2)
    check_merge_quality(df_election, "기권율_7회_pct", label="8회+7회")
    print(f"  8회: {len(df8)}개 | 7회: {len(df7)}개 구시군")

    # ── Step 2: 연령대별 투표율
    print("\n[Step 2] 연령대별 투표율 파싱...")
    df_age = load_age_turnout(PATH_TURN)
    print(f"  파싱 완료: {len(df_age)}개 구시군")

    # ── Step 3: 인구 데이터 (2022·2026 분리)
    print("\n[Step 3] 인구 데이터 로드...")
    df_pop22 = load_population_2022(PATH_POP22)
    df_pop26 = load_population_2026(PATH_POP26)
    print(f"  2022년: {len(df_pop22)}개 | 2026년: {len(df_pop26)}개 행정구역")

    # ── Step 4: 8회 설문 집계 (train 전용)
    print("\n[Step 4] 8회 유권자의식조사 집계 (train 전용)...")
    df_survey8 = load_survey_8th(PATH_SAV1, PATH_SAV2)
    print(f"  집계 완료: {len(df_survey8)}개 시도")

    # ── Step 5: 9회 의식조사 → predict 설문 피처 준비
    print("\n[Step 5] 9회 의식조사 → predict 설문 피처 변환...")
    df_survey9 = build_survey_9th(PATH_SURVEY9)
    print(f"  변환 완료: {len(df_survey9)}개 시도")
    missing_sidos = set(df8["시도명"].unique()) - set(df_survey9["시도명"].unique())
    if missing_sidos:
        print(f"  ⚠️  매핑 누락 시도: {missing_sidos}")
    else:
        print(f"  ✅ 전체 17개 시도 완전 커버")

    # ── Step 6: train_total 조립
    print("\n[Step 6] train_total 조립...")
    age_feat = ["청년_20대_투표율_pct","장년_30-40대_투표율_pct",
                "중년_50-60대_투표율_pct","고령_70대이상_투표율_pct","세대격차_pct"]
    pop_feat = ["청년인구비율_pct","장년인구비율_pct","중년인구비율_pct","고령인구비율_pct"]

    train = (
        df_election
        .merge(df_age[["시도명","구시군명"]+age_feat],  on=["시도명","구시군명"], how="left")
        .merge(df_pop22[["시도명","구시군명"]+pop_feat], on=["시도명","구시군명"], how="left")
        .merge(df_survey8, on="시도명", how="left")   # 8회 SAV 설문
    ).rename(columns={
        "기권율_8회_pct":"기권율_이전회_pct", "투표율_8회_pct":"투표율_이전회_pct",
        "기권율_7회_pct":"기권율_전전회_pct", "투표율_7회_pct":"투표율_전전회_pct",
    })
    train[TARGET_COL] = train["기권율_이전회_pct"]

    check_merge_quality(train, "청년_20대_투표율_pct", label="train+연령")
    check_merge_quality(train, "청년인구비율_pct",     label="train+2022인구")
    check_merge_quality(train, "기권의향률_pct",       label="train+8회설문")
    print(f"  shape: {train.shape}")

    # ── Step 7: predict_9th 조립 + 9회 설문 교체
    print("\n[Step 7] predict_9th 조립 + 9회 설문 피처 교체...")
    predict = (
        df8.rename(columns={
            "기권율_8회_pct":"기권율_이전회_pct",
            "투표율_8회_pct":"투표율_이전회_pct"})
        .merge(df_age[["시도명","구시군명"]+age_feat],  on=["시도명","구시군명"], how="left")
        .merge(df_pop26[["시도명","구시군명"]+pop_feat], on=["시도명","구시군명"], how="left")
        .merge(df_survey8, on="시도명", how="left")   # 8회로 초안 채움
    )
    predict["기권율_전전회_pct"] = predict["기권율_이전회_pct"]
    predict["투표율_전전회_pct"] = predict["투표율_이전회_pct"]
    predict["기권율_증가_pct"]   = np.nan
    predict[TARGET_COL]          = np.nan

    # 핵심: 8회 설문 → 9회 설문으로 교체
    predict = replace_survey_features(predict, df_survey9)

    check_merge_quality(predict, "청년_20대_투표율_pct", label="predict+연령")
    check_merge_quality(predict, "청년인구비율_pct",     label="predict+2026인구")
    check_merge_quality(predict, "기권의향률_pct",       label="predict+9회설문")
    print(f"  shape: {predict.shape}")

    # ── Step 8: 결측 처리
    print("\n[Step 8] 결측치 처리...")
    y_bak   = predict.pop(TARGET_COL)
    train   = fill_missing(train)
    predict = fill_missing(predict)
    predict[TARGET_COL] = y_bak

    # ── Step 9: 컬럼 정렬 + dtype
    print("\n[Step 9] 컬럼 정렬 및 dtype 표준화...")
    train, predict = align_and_finalize(train, predict)

    col_ok   = list(train.columns) == list(predict.columns)
    dtype_ok = all(train[c].dtype == predict[c].dtype for c in SHARED_FEATURE_COLS)
    print(f"  컬럼 순서 일치: {'✅' if col_ok   else '⚠️ '}")
    print(f"  dtype 일치    : {'✅' if dtype_ok else '⚠️ '}")

    # ── Step 10: 저장
    print("\n[Step 10] CSV 저장...")
    train_path   = f"{OUT}/train_total.csv"
    predict_path = f"{OUT}/predict_9th.csv"
    train.to_csv(train_path,   index=False, encoding="utf-8-sig")
    predict.to_csv(predict_path, index=False, encoding="utf-8-sig")

    # ── 최종 요약
    print("\n" + "="*62)
    print("  전처리 완료 요약")
    print("="*62)
    print(f"\n  {'파일':<22} {'행':>6}  {'컬럼':>6}  {'결측(Y제외)':>12}")
    print(f"  {'-'*50}")
    for name, df in [("train_total.csv", train), ("predict_9th.csv", predict)]:
        miss = df[SHARED_FEATURE_COLS].isnull().sum().sum()
        print(f"  {name:<22} {len(df):>6}  {len(df.columns):>6}  {miss:>12}")

    print(f"\n  Y 기술통계 [train]")
    print(f"    범위: {train[TARGET_COL].min():.1f}% ~ {train[TARGET_COL].max():.1f}%")
    print(f"    평균: {train[TARGET_COL].mean():.1f}%  표준편차: {train[TARGET_COL].std():.1f}%")

    print(f"\n  설문 피처 비교 (8회 train vs 9회 predict)")
    print(f"  {'피처':<28} {'train(8회)':>12} {'predict(9회)':>14}")
    print(f"  {'-'*56}")
    for col in SURVEY_FEAT_COLS:
        print(f"  {col:<28} {train[col].mean():>12.3f} {predict[col].mean():>14.3f}")

    print(f"\n  저장 경로:")
    print(f"    {train_path}")
    print(f"    {predict_path}")
    print()
    return train, predict


if __name__ == "__main__":
    train_df, predict_df = run_pipeline()
