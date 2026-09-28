# AI 활용 및 검증 기록 (ai_log.md)

**작성자**: [김채원]  
**역할**: 4번 (Pandas 분석 B)

---
## 첫 번째 활용 사례: [컬럼 결합, 변환/datetime 형식으로 변환하는 코드]

* **a) AI 프롬프트 (요청 내용)**: 
  > "[date와 time 컬럼을 결합하여 datetime 형식으로 변환하는 코드 알려줘]"

* **b) AI 출력 내용 (코드/답변)**:
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


* **c) 데이터 검증 내용 (내가 직접 확인한 방법)**:

  * `df.head()`를 통해 `2026-01-01` 날짜와 `07:13` 시간이 합쳐져 `2026-01-01 07:13:00` 형태의 결합 데이터로 정상적으로 생성되었는지 확인함.
  * 파생 생성된 요일(`day_name`)의 첫 행 데이터가 2026년 1월 1일의 실제 요일인 'Thursday(목요일)'와 일치하는지 실제 달력과 맞춰 cross-check함.


* **d) 채택 / 수정 / 폐기 여부 및 이유**:

판단: [채택]

이유: [데이터 검증 내용이 일치하기 때문에 채택했습니다.]

##  두 번째 활용 사례: [차트 그리기/지출 패턴 비교 차트 그리기 코드]

* **a) AI 프롬프트 (요청 내용)**: 
  > "[월별 지출 추이 선 차트까지 제대로 생성됐어. 다음 요일별/시간대별 지출 패턴 비교 차트 그리기 코드를 알려줘.]"

* **b) AI 출력 내용 (코드/답변)**:
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

* **c) 데이터 검증 내용 (내가 직접 확인한 방법)**:
* 본인이 Pandas로 계산한 요일별/시간대별 총 지출 금액이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결과 수치와 원 단위까지 정확히 일치하는지 확인함.
* 좌측에는 월~일 요일별 막대 차트, 우측에는 0~23시 시간대별 막대 차트가 나오는지 확인함.

* **d) 채택 / 수정/ 폐기 여부 및 이유**:

판단: [채택]

이유: [데이터 검증 내용이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결광와 일치하며, 막대 차트가 요일별, 시간별로 도출되었기 때문에 채택했습니다.]