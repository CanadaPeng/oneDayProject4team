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
```


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
```

* **c) 데이터 검증 내용 (내가 직접 확인한 방법)**:
* 본인이 Pandas로 계산한 요일별/시간대별 총 지출 금액이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결과 수치와 원 단위까지 정확히 일치하는지 확인함.
* 좌측에는 월~일 요일별 막대 차트, 우측에는 0~23시 시간대별 막대 차트가 나오는지 확인함.

* **d) 채택 / 수정/ 폐기 여부 및 이유**:

판단: [채택]

이유: [데이터 검증 내용이 2번 담당자가 SQL query(GROUP BY)로 뽑은 결광와 일치하며, 막대 차트가 요일별, 시간별로 도출되었기 때문에 채택했습니다.]

---

# AI 활용 및 검증 기록 — main.py 통합

**작성자**: [이름]  
**역할**: 1번 (데이터 정제 + 저장소 관리) · 최종 통합

---
## 세 번째 활용 사례: [팀원 결과물을 main.py 하나로 연결한 '소비패턴 데이터 탐정' 만들기]

* **a) AI 프롬프트 (요청 내용)**: 
  > "[지금 역할 별로 한 사람씩 전부 결과물을 보낸 상태야. git log를 보면 알 수 있겠지만 이제부터 이 결과물을 main.py와 연결해서 소비 패턴 데이터를 분석하는 '소비 패턴 데이터 탐정'을 만들어야 해.
  > 미션: 거래내역에서 카테고리별 지출, 큰 금액, 기간별 패턴을 찾아 브리핑 작성
  > 데이터 확보: transactions.csv / 공공데이터포털 금융·소비 관련 데이터
  > 활용 포인트: WHERE·GROUP BY·ORDER BY / 결측·중복·이상값 / Python 분류 함수
  > 이 조건들을 맞춰서 해야 하는데 지금 잘 진행이 되었는지 모르겠어. 파일들을 삭제하는 건 절대 하면 안돼고 위치도 옮기지 말고 main.py를 꾸며줘.]"

* **b) AI 출력 내용 (코드/답변)**:
  AI가 git log와 팀원 파일을 읽고 main.py를 아래 5단계로 구성함.

  | 단계 | 내용 | 연결한 팀원 결과물 |
  |---|---|---|
  | STEP 1 현장 조사 | `docs/data_rules.md` R1~R6 규칙으로 결측·중복·이상값 점검 (삭제 없이 `is_*` 플래그) | 1번 규칙 문서 |
  | STEP 2 단서 분류 | `classify_amount()`(소액/일반/고액), `classify_time()`(새벽/오전/오후/저녁) 분류 함수 적용 | — |
  | STEP 3 SQL 심문 | `sql/q1~q3_*.sql` 실행 | 2번 이승원 `sql/`, `function/run_sql.py` |
  | STEP 4 알리바이 확인 | 같은 질문을 Pandas로 다시 계산해 SQL 결과와 대조 (8개 항목) | 2번 SQL 결과 |
  | STEP 5 사건 보고서 | 브리핑 생성 후 결론 3줄 출력 | 6번 이성호 `brief_seongho.py` |

  ```python
  def main() -> None:
      frames = load_frames()
      tx = inspect_data(frames)      # STEP 1
      tx = tag_transactions(tx)      # STEP 2
      sql = run_sql_files()          # STEP 3
      cross_check(tx, sql)           # STEP 4
      write_briefing()               # STEP 5
      detective_findings(tx, sql)
  ```

  함께 받은 진행 상황 점검: 2번·4번·6번 결과물 있음 / 1번 정제 스크립트, 3번 분석 노트북, 5번 검증 스크립트, CONTRIBUTION.md 없음.

* **c) 데이터 검증 내용 (내가 직접 확인한 방법)**:
  * 프로젝트 폴더가 아닌 다른 폴더(`C:\`)에서 `python main.py`를 실행해 끝까지 에러 없이 도는지 확인함.
  * STEP 4 교차검증 8개 항목(Q1 카테고리별 건수·금액, Q1 비중 합 100%, Q2 고액 건수·금액 합, Q3 월·요일·시간별 금액, 전체 합계 = 월별 합계)이 모두 ✅인지 확인함.
  * 월별 합계를 Pandas `groupby`로 따로 뽑아 SQL Q3 결과와 비교함 → 최고 지출 월은 **4월(10,690,800원)**, 최저는 **3월(5,585,500원)**.
  * `git status`로 main.py 외에 삭제·이동된 파일이 없는지 확인함.

* **d) 채택 / 수정 / 폐기 여부 및 이유**:

판단: [수정 후 채택]

| 판단 | 대상 | 이유 |
|---|---|---|
| 채택 | 5단계 구조 전체 | 미션 조건(WHERE·GROUP BY·ORDER BY / 결측·중복·이상값 / Python 분류 함수 / 브리핑)이 단계마다 하나씩 대응되고, 교차검증 8개 항목이 모두 일치했기 때문 |
| 채택 | `function/run_sql.py`의 `load_csv_files()` 재사용 | 2번이 만든 코드를 복사하지 않고 import해서 쓰므로, SQL 쪽 수정이 main.py에 그대로 반영됨 |
| 채택 | 이상값을 지우지 않고 플래그만 붙이는 방식 | `data_rules.md`의 "삭제보다 플래그 우선" 원칙과 같음. 이상값 54건이 전체 지출의 32.7%를 차지해서, 지우면 결론 자체가 바뀜 |
| 수정 | STEP 2 시간대 집계 | 첫 실행에서 `ValueError: cannot convert float NaN to integer` 발생. 새벽(00~06시) 거래가 0건이라 빈 값이 생긴 것이 원인 → `reindex(..., fill_value=0)`으로 고쳐 재실행 후 통과 |
| 수정 | `brief_seongho.py` 호출 방식 | 이 파일은 `Path("data")` 상대 경로를 써서 다른 폴더에서 실행하면 데이터를 못 찾음. 팀원 파일은 고치지 않고, main.py에서 잠깐 프로젝트 폴더로 이동해 실행한 뒤 돌아오도록(`os.chdir` + `try/finally`) 수정 |
| 폐기 | 기존 `import function.dk` | `dk.py`는 함수 없이 import하는 순간 바로 실행되는 파일이고, 설치되지 않은 matplotlib를 불러와 main.py 전체가 멈춤. 하는 일도 CSV 미리보기뿐이라 main.py에서 빼기로 함 (파일 자체는 삭제하지 않음) |
| 폐기 | 4번 노트북 요약표의 "최고 지출 월: 5월" | SQL과 Pandas가 모두 4월을 가리킴. 손으로 옮겨 적은 값이라 틀린 것으로 판단 → 4번 담당자에게 4월로 정정 요청 |
