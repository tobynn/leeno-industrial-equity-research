# [원자료와 가정]

- `research_inputs.json`: 실제 재무제표·제품 매출·제품 성장·회수일수·비용·투자·배당·평가 조건과 출처.
- `actuals_verified.csv`: 2023~2025와 2025H1·2026H1 별도 실제 손익.
- `actuals_audit.csv`: 원자료 계정·정확한 원 단위 수치·모델의 십억원 입력·출처와 표 위치.
- `source_register.csv`: 공시·IR·방법론·시세 URL과 사용 범위.
- `source_manifest.json`: 확보한 원자료의 URL·해시와 확인일.
- `price_crosscheck.csv`: 시세 공급사 차이 기록.

`cases.*.rev26`, `growth`, `nwc`, `product_forecast`는 H2 제품 매출·제품별 성장·마진·DSO/DIO/DPO에서 계산한 파생값이다. 파생 필드를 직접 조정해 성장 근거를 바꾸지 않는다. `price_hurdle_uplift`는 가격을 맞춘 역산 결과이고 Base 성장 전망에 반영하지 않는다.
