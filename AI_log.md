# 1. 가상 데이터셋 생성

**작성자**: [이승원]

첨부한 분석 질문을 바탕으로 소비 데이터 분석 프로젝트를 진행하려고 해. date, transaction_id, type, category, amount를 포함한 가상 거래 데이터를 만들어줘. 고객·가맹점 정보도 별도 데이터셋으로 구성하고, ID를 기준으로 JOIN할 수 있게 해줘. 각 데이터셋의 컬럼과 연결 기준도 간단히 설명해줘.

**채택 / 수정 / 폐기 여부 및 이유**

판단: [채택]

이유: 거래 데이터와 고객·가맹점·카테고리 데이터를 별도 CSV로 구성하고, `customer_id`, `merchant_id`, `category`를 기준으로 JOIN할 수 있어 세 분석 질문에 활용할 수 있습니다. 실제 분석에 사용하기 전에는 ID 중복과 JOIN 누락 여부를 검증합니다.

# 2. main.py 생성

**작성자**: [이승훈]

지금 역할 별로 한 사람씩 전부 결과물을 보낸 상태야. git log를 보면 알 수 있겠지만 이제부터 이 결과물을 main.py와 연결해서 소비 패턴 데이터를 분석하는 '소비 패턴 데이터 탐정'을 만들어야 해.

- 미션: 거래내역에서 카테고리별 지출, 큰 금액, 기간별 패턴을 찾아 브리핑 작성
- 데이터 확보: transactions.csv / 공공데이터포털 금융·소비 관련 데이터
- 활용 포인트: WHERE·GROUP BY·ORDER BY / 결측·중복·이상값 / Python 분류 함수

이 조건들을 맞춰서 해야 하는데 지금 잘 진행이 되었는지 모르겠어. 파일들을 삭제하는 건 절대 하면 안돼고 위치도 옮기지 말고 main.py를 꾸며줘.

**채택 / 수정 / 폐기 여부 및 이유**

판단: [수정]

이유: 각 담당자의 결과물을 연결해 실행한다는 방향은 채택했습니다. 다만 `main.py`가 세 질문의 분석 결과와 브리핑을 모두 출력하는지 확인해야 합니다. 기존 파일의 위치를 유지한 상태에서 경로와 실행 순서를 점검한 뒤 반영합니다.

# 3. Pandas 분석

**작성자**: [김채원]

### 첫 번째 활용 사례: [컬럼 결합, 변환/datetime 형식으로 변환하는 코드]

**a) AI 프롬프트 (요청 내용)**

> "[date와 time 컬럼을 결합하여 datetime 형식으로 변환하는 코드 알려줘]"

**b) AI 출력 내용 (코드/답변)**

```python
# 1. date와 time을 합쳐서 하나의 datetime 컬럼으로 변환
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])

# 2. 분석에 필요한 파생 컬럼 만들기 (월, 요일, 시간대, 연월)
df['month'] = df['datetime'].dt.month
df['day_name'] = df['datetime'].dt.day_name() # 요일 (Monday, Tuesday...)
df['hour'] = df['datetime'].dt.hour           # 시간대 (0~23시)
df['year_month'] = df['datetime'].dt.to_period('M') # 연-월 (2026-01 등)

# 3. 변환된 결과 확인
df[['date', 'time', 'datetime', 'month', 'day_name', 'hour']].head()
```

**c) 데이터 검증 내용 (내가 직접 확인한 방법)**

- `df.head()`를 통해 `2026-01-01` 날짜와 `07:13` 시간이 합쳐져 `2026-01-01 07:13:00` 형태의 결합 데이터로 정상적으로 생성되었는지 확인함.
- 파생 생성된 요일(`day_name`)의 첫 행 데이터가 2026년 1월 1일의 실제 요일인 'Thursday(목요일)'와 일치하는지 실제 달력과 맞춰 cross-check함.

**d) 채택 / 수정 / 폐기 여부 및 이유**

판단: [채택]

이유: [데이터 검증 내용이 일치하기 때문에 채택했습니다.]

### 두 번째 활용 사례: [차트 그리기/지출 패턴 비교 차트 그리기 코드]

**a) AI 프롬프트 (요청 내용)**

> "[월별 지출 추이 선 차트까지 제대로 생성됐어. 다음 요일별/시간대별 지출 패턴 비교 차트 그리기 코드를 알려줘.]"

**b) AI 출력 내용 (코드/답변)**

```python
# 1. 요일 순서 정렬 (월요일 ~ 일요일)
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# 요일별 지출 총액 집계
daily_expense = df.groupby('day_name')['amount'].sum().reindex(day_order).reset_index()

# 2. 시간대별(0~23시) 지출 총액 집계
hourly_expense = df.groupby('hour')['amount'].sum().reset_index()

# 3. 요일별 & 시간대별 시각화 (2개의 그래프 함께 출력)
fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# (1) 요일별 지출 막대그래프
sns.barplot(data=daily_expense, x='day_name', y='amount', ax=axes[0], palette='Blues_d')
axes[0].set_title('요일별 총 지출 금액', fontsize=14, fontweight='bold')
axes[0].set_xlabel('요일')
axes[0].set_ylabel('총 지출 금액 (원)')
axes[0].tick_params(axis='x', rotation=30)
axes[0].grid(True, axis='y', linestyle='--', alpha=0.6)

# (2) 시간대별 지출 막대그래프
sns.barplot(data=hourly_expense, x='hour', y='amount', ax=axes[1], palette='Oranges_d')
axes[1].set_title('시간대별 총 지출 금액 (0~23시)', fontsize=14, fontweight='bold')
axes[1].set_xlabel('시간대 (시)')
axes[1].set_ylabel('총 지출 금액 (원)')
axes[1].grid(True, axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

# 집계된 요일별/시간대별 수치 확인
print("=== 요일별 지출 금액 ===")
print(daily_expense)
print("\n=== 시간대별 지출 금액 (상위 5개 피크 시간대) ===")
print(hourly_expense.sort_values(by='amount', ascending=False).head())
```

**c) 데이터 검증 내용 (내가 직접 확인한 방법)**

- 본인이 Pandas로 계산한 요일별/시간대별 총 지출 금액이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결과 수치와 원 단위까지 정확히 일치하는지 확인함.
- 좌측에는 월~일 요일별 막대 차트, 우측에는 0~23시 시간대별 막대 차트가 나오는지 확인함.

**d) 채택 / 수정/ 폐기 여부 및 이유**

판단: [채택]

이유: [데이터 검증 내용이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결광와 일치하며, 막대 차트가 요일별, 시간별로 도출되었기 때문에 채택했습니다.]

---

**작성자**: [김도경]

내 역할은 PANDAS 분석이야

- Q1 어떤 카테고리에 지출이 가장 많이 몰리는가? (금액, 건수, 비중)
- Q2 큰 금액 거래는 어떤 특징이 있는가? (상위 N건, 기준 금액 초과)

내 상세 할 일은

- 정제본을 불러와 카테고리별 금액, 건수, 비중 계산 (groupby)
- 카테고리별 지출 비중 막대 차트
- 큰 금액 기준(상위 5%/IQR 등) 적용해 고액 거래 추출
- 고액 거래의 카테고리 및 시기 특징 정리
- SQL 결과와 비교할 수치표 저장
- 데이터로 확인된 인사이트 2~3줄 작성
- 산출물: analysis_<이름>. ipynb
- 리뷰: SQL PR

**채택 / 수정 / 폐기 여부 및 이유**

판단: [수정]

이유: Q1의 금액·건수·비중 분석과 Q2의 고액 거래 분석 방향은 채택했습니다. 고액 거래 기준으로 상위 5%, IQR, 고정 금액이 함께 제시되어 있으므로 팀에서 하나의 기준을 확정해야 합니다. 이후 SQL과 Pandas에 같은 기준을 적용하고 결과를 비교합니다.