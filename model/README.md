# [리노공업 수식 모델]

현재 파일은 [Equity_Research_Model.xlsx](Equity_Research_Model.xlsx)다. `Inputs!D3`에서 Bear·Base·Bull을 선택한다. 실제 자료와 출처는 별도로 남기고 같은 계산 시트가 선택한 가정을 읽는다.

|시트|계산과 읽는 순서|
|---|---|
|Summary|2026년 말 DCF·정상화 이론 PER·RIM과 참고가격|
|Inputs|할인율·마진·투자·상환·제품 성장·DSO/DIO/DPO의 선택 입력|
|Operating Build|제품별 매출 합계와 매출원가 기반 NWC 계산|
|Forecast|2026E와 2027~2031 손익·현금·주주자본·경제적 주당이익|
|Cash Equity Bridge|H1 실제에서 H2 손익·투자·미지급비용 정산을 거쳐 연말로 연결|
|DCF|2027~2031 FCFF와 g/ROIC 재투자를 반영한 잔존가치|
|RIM|지배 순이익·자본 연결과 초과 ROE; 동일 배당경로 DDM 검증|
|PER|정상마진45%의 EPS와 성장·증분 ROE·요구수익률의 이론 배수|
|Diagnostics|현금 수익률 분리·장기 초과수익 소멸·마진/투자 충격·가격 역산|
|Special Cases|고객·회수·ELS·미지급비용과 투자비율을 유지한 매출 경로 역산|
|Peer Data|리노공업·ISC 같은 날짜 가격과 과거 지배 순이익·현재 경제주식수 비교|
|Actuals Sources|공시 원자료·금융자산·상각·주식수·제품 매출과 출처 목록|

금액은 십억원, 주식수는 백만주, 주당가치는 원이다. 파란 숫자는 원자료 또는 편집할 가정, 계산은 수식이다. 실제 자료를 바꿀 때는 출처·회계범위·기간을 먼저 맞춘다.

`price_hurdle_uplift`는 Python이 참고가격을 맞춰 역산한 계산 파라미터다. 분석자 Base 성장 가정과 구분한다. Special Cases의 별도 경로를 움직이며 본 Forecast를 변경하지 않는다. 사용자가 파라미터를 바꾸면 역산 가격은 참고가격과 달라질 수 있다.

배당은 전년 순이익×성향을 다음 해 지급하는 경로다. H2 미지급비용 현금조정은 EBIT에 재차 비용을 더하지 않는다. 원자료 제품표의 천원 반올림 때문에 H1 재무제표 원 단위 매출과 202원 차이가 있다.

[가정별 설명](../research/ASSUMPTION_LEDGER.md) · [독립 계산](research_results.json) · [검증](model_validation.json) · [가격 역산](company_detail.json)
