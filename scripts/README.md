# [계산과 문서 재생성]

1. `python scripts/rebuild_research.py`: 제품 성장·DSO/DIO/DPO에서 파생 입력을 갱신하고 본문·CSV·JSON을 계산한다.
2. `python scripts/build_figures.py --font /path/to/NanumGothic-Regular.ttf`: 같은 결과에서 3개 그림을 만든다.
3. `node scripts/build_model.mjs`: 편집 가능한 Excel을 생성하고 Python 결과와 대조한다. `@oai/artifact-tool`이 설치된 Node 환경이 필요하다.
4. `python scripts/build_report_pdf.py --font-dir /path/to/font-directory`: 본문·그림에서 PDF를 만든다. 폰트 디렉터리에 NanumGothic-Regular.ttf·NanumGothic-Bold.ttf가 필요하다.

Excel은 일반 Excel에서 가정을 편집하고 수식을 계산할 수 있다. 생성 스크립트는 별도의 artifact-tool 환경을 필요로 한다. 공개 Python 입력·계산 코드는 이 패키지 없이 재현할 수 있다.

`leeno_extensions.py`는 제품별 매출·NWC 입력, 기업 고유 민감도, 가격 역산과 자세한 설명을 담당한다. `valuation_review.py`는 기존 다섯 보고서와 같은 장기 수익률·현금 민감도를 계산한다. 원자료·추정·역산 결과를 혼동하지 않도록 입력 설명을 유지한다.

README 전문과 PDF를 갱신할 때 그림도 같은 결과에서 다시 만들어야 한다. 산출값만 복사해 기존 자료와 섞지 않는다.
