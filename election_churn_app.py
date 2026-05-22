import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, f1_score, precision_score, recall_score, accuracy_score
)
from sklearn.utils import resample
import warnings
warnings.filterwarnings("ignore")

# ── 한글 폰트 설정 (환경에 따라 경로 수정 필요) ──────────────────────────────
# Mac: 'AppleGothic' / Windows: 'Malgun Gothic' / Linux: 'NanumGothic'
try:
    plt.rcParams["font.family"] = "Malgun Gothic"
except:
    plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# ── 페이지 설정 ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="선거 지역구 이탈 예측",
    page_icon="🗳️",
    layout="wide",
)

# ── 샘플 데이터 생성 (실제 데이터로 교체 필요) ────────────────────────────────
@st.cache_data
def load_data():
    """
    실제 데이터 수집 전까지 사용할 샘플 데이터.
    컬럼 구성:
      - region       : 광역시/도
      - district     : 지역구명
      - prev_party   : 직전 선거 1위 정당
      - margin       : 직전 선거 득표율 차이 (%)
      - elder_rate   : 고령화율 (%)
      - youth_rate   : 청년 인구 비율 (%)
      - fiscal_ind   : 재정자립도 (%)
      - turnout_diff : 투표율 변화 (%p, 직전 대비)
      - churn        : 이탈 여부 (1: 정당 교체 / 0: 유지)
    """
    np.random.seed(42)
    n = 254
    regions = ["서울", "경기", "부산", "대구", "인천", "광주", "대전", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
    parties = ["더불어민주당", "국민의힘", "기타"]

    df = pd.DataFrame({
        "region":       np.random.choice(regions, n),
        "district":     [f"지역구_{i+1:03d}" for i in range(n)],
        "prev_party":   np.random.choice(parties, n, p=[0.45, 0.45, 0.10]),
        "margin":       np.round(np.random.exponential(scale=8, size=n).clip(0.1, 55), 1),
        "elder_rate":   np.round(np.random.normal(20, 5, n).clip(8, 42), 1),
        "youth_rate":   np.round(np.random.normal(22, 4, n).clip(10, 38), 1),
        "fiscal_ind":   np.round(np.random.normal(38, 15, n).clip(8, 85), 1),
        "turnout_diff": np.round(np.random.normal(-0.5, 3, n).clip(-12, 10), 1),
    })

    # 이탈 확률 설계 (도메인 반영)
    churn_prob = (
        0.15
        + (df["margin"] < 5).astype(float) * 0.30
        + (df["margin"] < 10).astype(float) * 0.10
        + (df["elder_rate"] > 25).astype(float) * 0.20
        + (df["elder_rate"] > 20).astype(float) * 0.10
        + (df["fiscal_ind"] < 30).astype(float) * 0.10
        + (df["turnout_diff"] < -2).astype(float) * 0.15
        + np.random.normal(0, 0.08, n)
    ).clip(0.02, 0.98)
    df["churn"] = (np.random.random(n) < churn_prob).astype(int)
    return df


@st.cache_resource
def train_models(df):
    """5개 모델 학습 및 성능 반환"""
    features = ["margin", "elder_rate", "youth_rate", "fiscal_ind", "turnout_diff"]
    X = df[features]
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # SMOTE 대신 간단한 오버샘플링 (imbalanced-learn 미설치 환경 대응)
    train_df = pd.concat([X_train, y_train], axis=1)
    majority  = train_df[train_df.churn == 0]
    minority  = train_df[train_df.churn == 1]
    minority_up = resample(minority, replace=True, n_samples=len(majority), random_state=42)
    balanced  = pd.concat([majority, minority_up])
    X_bal, y_bal = balanced[features], balanced["churn"]

    scaler = StandardScaler()
    X_bal_s  = scaler.fit_transform(X_bal)
    X_test_s = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "SVM":                 SVC(probability=True, random_state=42),
        "KNN":                 KNeighborsClassifier(n_neighbors=7),
        "Random Forest":       RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost (GBM)":       GradientBoostingClassifier(n_estimators=100, random_state=42),
    }

    results = {}
    trained = {}
    for name, model in models.items():
        model.fit(X_bal_s, y_bal)
        y_pred = model.predict(X_test_s)
        y_prob = model.predict_proba(X_test_s)[:, 1]
        results[name] = {
            "Accuracy":  round(accuracy_score(y_test, y_pred), 3),
            "Precision": round(precision_score(y_test, y_pred, zero_division=0), 3),
            "Recall":    round(recall_score(y_test, y_pred, zero_division=0), 3),
            "F1":        round(f1_score(y_test, y_pred, zero_division=0), 3),
            "AUC-ROC":   round(roc_auc_score(y_test, y_prob), 3),
        }
        trained[name] = model

    return trained, scaler, results, X_test_s, y_test, features


# ── 데이터 & 모델 로드 ─────────────────────────────────────────────────────────
df = load_data()
trained_models, scaler, perf_results, X_test_s, y_test, FEATURES = train_models(df)
best_model_name = max(perf_results, key=lambda k: perf_results[k]["F1"])
best_model      = trained_models[best_model_name]

# ── 사이드바 ───────────────────────────────────────────────────────────────────
st.sidebar.title("🗳️ 선거 이탈 예측")
st.sidebar.caption("지역구 정당 교체 가능성 분석")
st.sidebar.divider()

page = st.sidebar.radio(
    "메뉴",
    ["📊 EDA", "🤖 이탈 예측", "📈 모델 성능"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.subheader("🔍 데이터 필터")
sel_region = st.sidebar.multiselect(
    "광역시/도",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique()),
)
sel_party = st.sidebar.multiselect(
    "직전 1위 정당",
    options=df["prev_party"].unique().tolist(),
    default=df["prev_party"].unique().tolist(),
)

filtered_df = df[df["region"].isin(sel_region) & df["prev_party"].isin(sel_party)]

# ══════════════════════════════════════════════════════════════════════════════
# 페이지 1: EDA
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 EDA":
    st.title("📊 탐색적 데이터 분석 (EDA)")
    st.caption(f"필터 적용 기준: {len(filtered_df)}개 지역구")

    # ── 요약 지표 ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 지역구 수",    f"{len(filtered_df)}개")
    c2.metric("이탈 지역구",     f"{filtered_df['churn'].sum()}개",
              f"{filtered_df['churn'].mean()*100:.1f}%")
    c3.metric("평균 득표율 차이", f"{filtered_df['margin'].mean():.1f}%")
    c4.metric("평균 고령화율",   f"{filtered_df['elder_rate'].mean():.1f}%")

    st.divider()

    # ── 차트 행 1 ──────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("지역별 이탈 비율")
        region_churn = (
            filtered_df.groupby("region")["churn"]
            .mean()
            .sort_values(ascending=True)
            .mul(100)
            .round(1)
        )
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.barh(region_churn.index, region_churn.values, color="#378ADD", height=0.6)
        ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
        ax.set_xlabel("이탈 비율 (%)")
        ax.set_xlim(0, region_churn.max() * 1.25)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.subheader("이탈 label 분포")
        counts   = filtered_df["churn"].value_counts()
        labels_p = ["유지 (0)", "이탈 (1)"]
        colors_p = ["#378ADD", "#E24B4A"]
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax2.pie(
            counts, labels=labels_p, colors=colors_p,
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(width=0.55),
        )
        for at in autotexts:
            at.set_fontsize(11)
        ax2.set_title("클래스 비율", fontsize=12)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close()

        if filtered_df["churn"].mean() < 0.35:
            st.warning("⚠️ 불균형 데이터 — 오버샘플링(SMOTE) 적용 권장")

    st.divider()

    # ── 차트 행 2: feature 분포 ────────────────────────────────────────────────
    st.subheader("이탈 여부별 주요 feature 분포")
    feat_labels = {
        "margin":       "득표율 차이 (%)",
        "elder_rate":   "고령화율 (%)",
        "turnout_diff": "투표율 변화 (%p)",
        "fiscal_ind":   "재정자립도 (%)",
    }
    fig3, axes = plt.subplots(1, 4, figsize=(14, 3.5))
    for ax, (col, label) in zip(axes, feat_labels.items()):
        for val, color, lbl in [(0, "#378ADD", "유지"), (1, "#E24B4A", "이탈")]:
            ax.hist(
                filtered_df[filtered_df["churn"] == val][col],
                bins=15, alpha=0.6, color=color, label=lbl, density=True,
            )
        ax.set_title(label, fontsize=10)
        ax.legend(fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    st.divider()

    # ── 원본 데이터 테이블 ─────────────────────────────────────────────────────
    st.subheader("원본 데이터 미리보기")
    st.dataframe(
        filtered_df.rename(columns={
            "region": "광역시/도", "district": "지역구", "prev_party": "직전 1위 정당",
            "margin": "득표율 차이(%)", "elder_rate": "고령화율(%)",
            "youth_rate": "청년비율(%)", "fiscal_ind": "재정자립도(%)",
            "turnout_diff": "투표율변화(%p)", "churn": "이탈여부",
        }),
        use_container_width=True,
        height=280,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 페이지 2: 이탈 예측
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 이탈 예측":
    st.title("🤖 지역구 이탈 예측")
    st.caption("지역구 정보를 입력하면 다음 선거에서 정당 교체(이탈) 가능성을 예측합니다.")

    with st.form("pred_form"):
        st.subheader("지역구 정보 입력")
        r1, r2 = st.columns(2)
        with r1:
            inp_region = st.selectbox("광역시/도",    sorted(df["region"].unique()))
            inp_party  = st.selectbox("직전 1위 정당", df["prev_party"].unique())
            inp_margin = st.slider("직전 선거 득표율 차이 (%)", 0.1, 55.0, 8.0, 0.1,
                                   help="1위와 2위의 득표율 차이가 작을수록 이탈 위험 ↑")
        with r2:
            inp_elder   = st.slider("고령화율 (%)",      8.0, 42.0, 20.0, 0.1)
            inp_youth   = st.slider("청년 인구 비율 (%)", 10.0, 38.0, 22.0, 0.1)
            inp_fiscal  = st.slider("재정자립도 (%)",     8.0, 85.0, 38.0, 0.1)
            inp_turnout = st.slider("투표율 변화 (%p)",  -12.0, 10.0, -1.0, 0.1,
                                    help="직전 선거 대비 투표율 변화. 음수 = 감소")

        submitted = st.form_submit_button("🔍 이탈 예측하기", use_container_width=True)

    if submitted:
        X_input = np.array([[inp_margin, inp_elder, inp_youth, inp_fiscal, inp_turnout]])
        X_scaled = scaler.transform(X_input)
        prob     = best_model.predict_proba(X_scaled)[0][1]
        pred     = int(prob >= 0.5)

        st.divider()
        col_res, col_gauge = st.columns([2, 1])

        with col_res:
            if pred == 1:
                st.error(f"### ⚠️ 이탈 가능성 높음\n이탈 확률: **{prob*100:.1f}%**")
            else:
                st.success(f"### ✅ 현상 유지 가능성 높음\n이탈 확률: **{prob*100:.1f}%**")

            st.progress(float(prob), text=f"이탈 확률: {prob*100:.1f}%")

            st.markdown("**주요 영향 요인 분석**")
            factors = []
            if inp_margin  < 5:    factors.append(f"🔴 박빙 선거구 (득표율 차이 {inp_margin}%)")
            elif inp_margin < 10:  factors.append(f"🟡 경합 선거구 (득표율 차이 {inp_margin}%)")
            if inp_elder   > 25:   factors.append(f"🔴 고령화율 높음 ({inp_elder}%)")
            if inp_fiscal  < 30:   factors.append(f"🟡 낮은 재정자립도 ({inp_fiscal}%)")
            if inp_turnout < -2:   factors.append(f"🔴 투표율 하락 ({inp_turnout:+.1f}%p)")
            if not factors:
                factors.append("✅ 특이 위험 요인 없음")
            for f in factors:
                st.markdown(f"- {f}")

        with col_gauge:
            fig_g, ax_g = plt.subplots(figsize=(3, 3))
            colors_g = ["#E24B4A" if prob >= 0.5 else "#1D9E75",
                        "#e0e0e0"]
            ax_g.pie(
                [prob, 1 - prob], colors=colors_g,
                startangle=90, wedgeprops=dict(width=0.45),
            )
            ax_g.text(0, 0, f"{prob*100:.0f}%", ha="center", va="center",
                      fontsize=20, fontweight="bold",
                      color="#E24B4A" if prob >= 0.5 else "#1D9E75")
            ax_g.set_title("이탈 확률", fontsize=11)
            st.pyplot(fig_g)
            plt.close()

        st.caption(f"사용 모델: {best_model_name} | 지역: {inp_region} | 직전 정당: {inp_party}")


# ══════════════════════════════════════════════════════════════════════════════
# 페이지 3: 모델 성능
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 모델 성능":
    st.title("📈 모델 성능 비교")
    st.caption("불균형 데이터 처리(오버샘플링) 후 측정된 지표입니다.")

    # ── 평가 지표 설명 ─────────────────────────────────────────────────────────
    with st.expander("📌 평가 지표 선정 이유"):
        st.markdown("""
**이탈 예측에서는 Accuracy 단독 사용이 부적합합니다.**
- 이탈 비율이 약 30~35% 수준으로 클래스 불균형이 존재합니다.
- 모든 지역구를 "유지"로 예측해도 Accuracy는 65% 이상 나옵니다.

따라서 아래 두 지표를 주요 기준으로 선정했습니다:
- **F1-score (이탈 클래스)**: Precision과 Recall의 조화 평균 → 놓친 이탈과 오탐 모두 고려
- **AUC-ROC**: 전체 임계값 범위에서의 분류 성능 → 모델 간 공정한 비교 가능
        """)

    st.divider()

    # ── 성능 테이블 ────────────────────────────────────────────────────────────
    st.subheader("모델별 평가 지표")
    perf_df = pd.DataFrame(perf_results).T.reset_index().rename(columns={"index": "모델"})

    def highlight_best(row):
        return ["background-color: #dbeafe; font-weight: bold"
                if row["모델"] == best_model_name else "" for _ in row]

    st.dataframe(
        perf_df.style.apply(highlight_best, axis=1),
        use_container_width=True,
        hide_index=True,
    )
    st.success(f"🏆 최종 선정 모델: **{best_model_name}** (F1: {perf_results[best_model_name]['F1']})")

    st.divider()

    # ── 시각화 ────────────────────────────────────────────────────────────────
    col_bar, col_cm = st.columns(2)

    with col_bar:
        st.subheader("F1-score 비교")
        names  = list(perf_results.keys())
        f1s    = [perf_results[n]["F1"] for n in names]
        colors = ["#E24B4A" if n == best_model_name else "#378ADD" for n in names]
        fig4, ax4 = plt.subplots(figsize=(5, 3.5))
        bars4 = ax4.barh(names, f1s, color=colors, height=0.55)
        ax4.bar_label(bars4, fmt="%.3f", padding=3, fontsize=9)
        ax4.set_xlim(0, 1.0)
        ax4.set_xlabel("F1-score")
        ax4.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

    with col_cm:
        st.subheader(f"혼동 행렬 ({best_model_name})")
        y_pred_best = best_model.predict(X_test_s)
        cm = confusion_matrix(y_test, y_pred_best)
        fig5, ax5 = plt.subplots(figsize=(4, 3.5))
        im = ax5.imshow(cm, cmap="Blues")
        ax5.set_xticks([0, 1]); ax5.set_yticks([0, 1])
        ax5.set_xticklabels(["예측: 유지", "예측: 이탈"])
        ax5.set_yticklabels(["실제: 유지", "실제: 이탈"])
        for i in range(2):
            for j in range(2):
                ax5.text(j, i, str(cm[i, j]), ha="center", va="center",
                         fontsize=16, fontweight="bold",
                         color="white" if cm[i, j] > cm.max() / 2 else "black")
        plt.colorbar(im, ax=ax5, shrink=0.8)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()

    # ── Feature 중요도 (Random Forest / GBM 계열만) ────────────────────────────
    if hasattr(best_model, "feature_importances_"):
        st.divider()
        st.subheader(f"Feature 중요도 ({best_model_name})")
        importances = best_model.feature_importances_
        feat_labels_ko = {
            "margin":       "득표율 차이",
            "elder_rate":   "고령화율",
            "youth_rate":   "청년 비율",
            "fiscal_ind":   "재정자립도",
            "turnout_diff": "투표율 변화",
        }
        imp_df = pd.DataFrame({
            "feature": [feat_labels_ko[f] for f in FEATURES],
            "importance": importances,
        }).sort_values("importance", ascending=True)

        fig6, ax6 = plt.subplots(figsize=(7, 3))
        ax6.barh(imp_df["feature"], imp_df["importance"], color="#378ADD", height=0.55)
        ax6.set_xlabel("중요도")
        ax6.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()
