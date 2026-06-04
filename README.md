# SKN31-2nd-1Team
<div align="center">
    <img src="image/team_poster.png" width="450" height="600"></td>

## 팀 및 팀원 소개

# 유권자들

| 김동민 | 김재원 | 박하린 | 안혁진 | 전서연 
| :---: | :---: | :---: | :---: | :---: |
| <a href="https://github.com/Uranium10"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/kimjae9360"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/MintRinne"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> | <a href="https://github.com/Jinxxxok"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> |  <a href="https://github.com/sxoxyn"><img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/> |
|<img src="image/dm.png" width="150" height="150"> | <img src="image/jw.png" width="150" height="150"> | <img src="image/hr.png" width="150" height="150"> | <img src="image/hj.png" width="150" height="150"> | <img src="image/sy.png" width="150" height="150"> |
| <b>PM</b>     |<b>데이터 전처리</b>  |<b>데이터 전처리</b>   |<b>ML/DL</b>  | <b>ML/DL</b>   | | 

</div>

---
## 목차
> 1. 프로젝트 개요 
> 2. 기술 스택  
> 3. 프로젝트 WBS  
> 4. 프로젝트 구조  
> 5. 데이터 파이프라인  
> 6. 요구사항 명세(기능/비기능)  
> 7. 수행 결과  
>8. 회고

---

## 1. 프로젝트 개요

## 1.1 프로젝트명
제9회 지방선거 시군구별 투표 이탈(기권) 예측

## 1.2 프로젝트 소개
과거 지방선거에는 참여했으나, 이번 제9회 지방선거에서는 **투표에 참여하지 않고 이탈(기권)할 가능성**이 높은 지역을 예측합니다. 
공간 데이터와 유권자 인구 특성을 결합하여 **기권 위험 지도**를 구축하는 것을 핵심으로 합니다.

## 1.3 프로젝트 배경
#### 📉 지방선거의 고질적인 낮은 참여율  
 : 지방선거는 대선이나 총선에 비해 상대적으로 유권자의 관심도가 낮아, **투표율 제고를 위한 선제적 조치**가 절차적으로 중요합니다.
#### 🔎 마케팅 개념의 공공 부문 도입  
 : 기업이 이탈 징후가 보이는 고객을 데이터로 식별하고 **타겟 마케팅**을 펼치듯, 
 유권자 데이터 분석을 통해 투표 참여율이 급감할 유력 지역을 미리 찾아냅니다.
#### ⚖️ 한정된 자원의 효율적 배분  
 : 선거관리위원회의 투표 독려 예산이나 정당의 캠페인 인력 등은 한정되어 있습니다. 따라서 무차별적인 홍보 대신, 
 **데이터 기반의 이탈 위험 지역을 정의**함으로써 최소한의 비용으로 유권자 이탈을 막는 **효율적인 자원 투입**이 필요합니다.

## 1.4 프로젝트 목표
#### 1️⃣ 유권자 이탈 예측 모델 개발 및 고도화 
: 과거 선거 데이터(투표율 변동 추이), 인구 통계 데이터(연령)를 융합한 머신러닝 기반의 이탈 위험 예측 모델을 구축.  
#### 2️⃣ 데이터 기반의 투표 이탈 위험 지도 시각화 
: 분석 결과를 한눈에 이탈 위험도를 파악할 수 있는 대시보드 및 지도 제작  
#### 3️⃣ 실효성 있는 타겟형 투표 독려 전략 제시 
: 이탈 위험이 높게 예측된 지역을 중심으로 '찾아가는 사전투표소 운영', '선거 공보물 가독성 개선', 
 '취약 지역 집중 가로수 현수막 및 모바일 알림톡 발송' 등의 맞춤형 행정 서비스를 제안

---

## 2. 기술 스택
| Layer | Technology  |
|:-|:-|
|**Web App & Core**|![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff) ![React](https://img.shields.io/badge/React-%2320232a.svg?logo=react&logoColor=%2361DAFB) ![Three.js](https://img.shields.io/badge/Three.js-000?logo=threedotjs&logoColor=fff)|
|**Data Analysis**|![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=fff) ![Requests](https://img.shields.io/badge/Requests-43B02A?logo=Requests&logoColor=fff)|
|**Machine Learning**|![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)  ![LightGBM](https://img.shields.io/badge/LightGBM-02569B?style=flat) ![Lasso](https://img.shields.io/badge/Lasso-84569B?style=flat) ![Ridge](https://img.shields.io/badge/Ridge-007FFF?style=flat) ![Logistic Regression](https://img.shields.io/badge/LogisticRegression-4C64FF?style=flat)|
|**Visualization**|![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) ![Matplotlib](https://custom-icon-badges.demolab.com/badge/Matplotlib-71D291?logo=matplotlib&logoColor=fff) ![Seaborn](https://img.shields.io/badge/Seaborn-4EAEAA?logo=python&logoColor=fff)|
|**Dev Tools**|![Visual Studio Code](https://custom-icon-badges.demolab.com/badge/Visual%20Studio%20Code-0078d7.svg?logo=visualstudiocode&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-ffffff?logo=Jupyter) ![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?logo=github&logoColor=white)|

---

## 3. 프로젝트 WBS

| 구분 | 주요 작업 내용 | 담당자 | 일정 |
|:-:|:-|:-:|:-:|
| **기획** | 요구사항 정의 및 UI/UX 설계 | 전체 | 05/26 ~ 05/27 |
| **데이터 전처리** | RAW DATA(개표·인구·설문) 수집, 정규화 및 피처 생성 | 박하린, 김재원, 안혁진| 05/26 ~ 05/31 |
| **ML/DL 모델링** | EDA, 베이스라인 구축, Lasso/LGBM 등 모델 학습 및 예측 | 안혁진, 전서연 | 05/31 ~ 06/03 |
| **웹 F/B** | FastAPI 연동, 코로플레스 지도 및 데이터 시각화, 배포 | 김동민 | 05/31 ~ 06/03 |
| **공통/PM** | 데일리 스탠드업, 통합 테스트 및 최종 발표 준비 | 전체 | 05/26 ~ 06/04 |

<span>자료 : <a href="https://docs.google.com/spreadsheets/d/180tRAA2pfOSqnx47854IKnDHFj3Zfdz4/edit?usp=sharing&ouid=102065251248098778885&rtpof=true&sd=true" target='_blank' rel='noreferrer noopener' >구글 - WBS</a></span>



---

## 4. 프로젝트 구조

```
📂  root
├ 📄 README.md
├ 📄 .gitignore
┃
├ 📂 data
┃├ 📂 processed  # 가공 후 데이터
┃├ 📂 raw  # 가공 전 데이터
┃└ 📄 preprocess.py   # 프로그램
├ 📂 DL  # 당선 예측 모델
├ 📂 image
├📂 ML
┃├ 📂 notebooks # 주피터
┃├ 📂 models  # 저장된 모델
┃└ 📄 requirements.txt  # 필요패키지 
├📂 web_back
├📂 web_front
├📂 산출물
```
---

## 5. 데이터 파이프라인

<img src="image/dataflow.jpg" width="720" height="850">
<span>자료 : <a href="https://www.notion.so/Feature-370db08ed97780edae09d6fc808a846d?source=copy_link" target='_blank' rel='noreferrer noopener' >Notion - Feature명세서</a></span>

---

## 6. 요구사항 명세

### FR-1. 데이터 전처리
| ID | 요구사항 | 담당 | 산출물 |
|---|---|---|---|
| D01 | 7,8회 개표결과 로드 및 기권율 계산, 시도명 정규화 | 하린,재원 | 구시군별 기권율 테이블 |
| D02 | 연령대별 투표율 파싱 → 청년/장년/중년/고령 파생변수 생성 | 하린,재원 | 연령그룹별 투표율 피처 |
| D03 | 2022,2026 인구 파일 파싱 및 비율 산출, 지명 불일치 33건 매핑 | 하린,재원 | 인구비율 4개 피처 |
| D04 | 8회 SAV 설문 집계 → 구시군 브로드캐스트 | 재원 | train 설문 피처 |
| D05 | 9회 의식조사 권역→시도 매핑, % → 리커트 척도 변환 | 하린 | predict 설문 피처 |
| D06 | 2026 여론조사(지선,대선/정당 지지율) 크롤링 수집 | 혁진 | 지지율 CSV 다수 |
| D07 | train 250행,결측 0건 / predict 250행,컬럼 대칭 최종 검증 | 하린,재원 | `train_total.csv` `predict_9th.csv` |

### FR-2. ML/DL 모델링
| ID | 요구사항 | 담당 | 산출물 |
|---|---|---|---|
| M01 | 피처별 분포·상관관계 EDA | 혁진,서연 | EDA 리포트 |
| M02 | Ridge 베이스라인 학습, Leakage 피처 제거 | 혁진,서연 | RMSE·R² 결과 |
| M03 | LOO 교차검증 (LR & MLP) | 혁진,서연 | LOO 정확도 |
| M04 | Lasso·LightGBM 주 모델 학습 및 비교 | 혁진,서연 | 모델 객체 |
| M05 | MLP+LR 경합지역 당락 예측 (DL) | 혁진,서연 | MLP+LR 모델 |
| M06 | SHAP 피처 중요도 분석 | 혁진,서연 | SHAP 차트 |
| M07 | `predict_9th.csv` 입력 → 9회 기권율 예측, 모델 저장 | 혁진,서연 | `predict_9th_result.csv` `model_final.pth` |

### FR-3. 웹 대시보드
| ID | 요구사항 | 담당 | 산출물 |
|---|---|---|---|
| W01 | 시군구별 기권율 React-rechart lib 지도 구현 | 동민 | 지도 컴포넌트 |
| W02 | 기권율 49.5% 컷오프 기준 고위험 지역 경고 팝업 | 동민 | 경고 팝업 컴포넌트 |
| W03 | 광역시단체장 당선 예측, 경합 지역 chart 구현 | 동민 | 바차트 컴포넌트 |
| W04 | 배포 | 동민 | 배포 URL |

### NFR. 비기능 요구사항
- **정확도** : 기권율 예측 RMSE ≤ 3.0%p, R² ≥ 0.70
- **완결성** : train/predict 데이터셋 결측값 0건, 전국 250개 구시군 커버리지 100%
- **성능** : 대시보드 초기 로딩 5초 이내
- **유지보수** : 모듈별 독립 실행 가능하도록 코드 분리, Feature 명세서(Notion) 갱신 및 GitHub 버전관리, 데일리 스탠드업 전 기간 운영

---

## 7. 수행 결과

### 1) 
<img src="">

### 2) 
<img src="">

### 3)
<img src="">

### 4) 
<img src="">


---

## 8. 회고
#### 김동민
 - 

#### 김재원
  - 수업 때 주어졌던 자료를 통해 데이터 수집을 하지 않았었는데 직접 해볼 수 있는 기회가 있어서 수업 때 부족했던 부분을 채울 수 있었습니다.
 데이터 수집이 원활한 주제를 통해서 할 수 없었다는 점은 아쉽지만, 그럼에도 넷상 다양한 자료가 있어서 선거관련된 부분을 부담없이 할 수 있었습니다.
 머신러닝과 그것을 시각화하는 팀원들의 모습을 보면서 감탄했고 또 저렇게 해보고 싶다는 마음이 들어서 식견이 넓어진 것 같습니다. 식견을 넓히게 해준 팀원들에게 감사하다는 말을 하고 싶습니다.

#### 박하린
 - 선거에 대한 도메인 지식이 부족하여, raw data를 수집할 때 어떤 데이터들이 필요한지 분석하는데, 어려움이 있었습니다. 따라서 문제를 타개하고자 지난 선거 데이터를 분석하여 예측한 분석리포트를 참고해보고, 정치 전문가에게 자문을 구하며, 투표 참여를 결정하는 요인들을 정의하게 되었습니다. 선관위(데이터셋)에서 양질의 공공데이터를 손쉽게 구할 수 있었습니다. clean data를 학습/검증용, 테스트용로 분류할 때, 데이터의 척도를 통일하고, merge하는 과정도 다소 복잡하였지만, 같은 파트를 담당한 팀원과 분담하여 계획한 시간 내로 프로젝트를 진행할 수 있었습니다. 2번째 프로젝트이다 보니, 협업을 더 유연하게 하는 여유가 생기는 것 같습니다. PM의 리더쉽과 팀원들이 책임감있고, 능동적으로 협업해주어 만족스러운 결과물이 나온 것 같습니다😆​

#### 안혁진
 - 처음 해보는 ML/DL 프로젝트에 막연한 두려움이 앞섰지만, 각자의 자리에서 묵묵히 맡은 바를 해내는 팀원들을 보며 저도 차근차근 뒤따라가고 있었습니다. 데이터를 앞에 두고 방향을 잡지 못해 헤매던 순간도, 팀원들과 머리를 맞대고 이야기를 나누다 보면 어느새 실마리가 풀려 있었고.
1차 때보다 훨씬 복잡한 문제였다고 생각하며 임했는데 역시 그만큼 막히는 순간도 많았습니다. 그래도 서로의 진행 상황을 공유하고, 누군가 어려움을 토로하면 다 같이 달려드는 분위기 덕분에 혼자였다면 포기했을 법한 고비들을 넘길 수 있었던 것 같습니다.
힘들었던 건 사실이지만, 그 힘든 시간을 함께 버텨낸 팀원들이 있었기에 이번 프로젝트가 나에게 단순한 결과물 이상의 의미로 남는 것 같습니다 2차프로젝트 1팀 최고!
 
#### 전서연
 - 
