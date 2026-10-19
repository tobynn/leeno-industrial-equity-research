import copy,math

def normalize(p):
 for c in p['cases'].values():
  parts=[[p['product_actuals'][j]+c['h2'][j]] for j in range(4)]
  for i in range(5):
   for j in range(4):parts[j].append(parts[j][-1]*(1+c['pg'][j][i]))
  totals=[sum(parts[j][i] for j in range(4)) for i in range(6)]
  c['product_forecast']=dict(zip(p['product_names'],parts));c['rev26']=totals[0];c['growth']=[totals[i]/totals[i-1]-1 for i in range(1,6)]
  c['nwc']=[c['dso'][i]/365+(1-c['margin'][i]-c['sgaratio'])*(c['dio'][i]-c['dpo'][i])/365 for i in range(6)]
 return p

def additional(p,r,jper):
 c=p['cases'][r['case']];a=p['actual_aux'];x=p['review_inputs'];f=r['forecast'];s=r['bridge']['shares_mn'];w=c['wacc']
 z=dict(dso_15day_liquidity=f[1]['revenue']*x['collection_delay_days']/365,
   customer_one_year_dcf=r['dcf_price']-f[1]['revenue']*x['customer_a_share']*x['customer_shock']*x['contribution_margin']*(1-p['tax'])/(1+w)*1000/s,
   ignored_accrual_dcf=r['dcf_price']-p['h2_cash_adjustment']*1000/s,
   els_haircut_dcf=r['dcf_price']-20.329235*.20*1000/s,
   h1_cash_conversion=p['h1']['cfo']/p['h1']['ni'],dso_h1=a['ar_h1']/(p['h1']['rev']*2)*365,dso_2025=a['ar_2025']/a['fy2025_rev']*365,
   project_remaining=a['project_budget']-a['project_spent'],h2_other_capex=c['capex'][0]-p['h1']['capex']-(a['project_budget']-a['project_spent']))
 stages=[('조건 비교 시작: 성장 6%·증분 ROE 15%·ke 11.5%',.06,.15,.115),('성장률 12%로 변경',.12,.15,.115),('증분 ROE 30%로 변경',.12,.30,.115),('ke 10.5%로 변경',.12,.30,.105)]
 z['premium_steps']=[dict(label=l,per=jper(g,roe,.025,.12,ke)) for l,g,roe,ke in stages]
 z['duration_prices']=[dict(years=n,per=jper(c['pergrowth'],c['perroe'],c['g'],c['roe'],c['ke'],n),price=r['normalized_eps']*jper(c['pergrowth'],c['perroe'],c['g'],c['roe'],c['ke'],n)) for n in [3,5,7,10,15]]
 def hurdle(mult):
  nwc=r['forecast'][0]['nwc'];vals=[]
  for i,q in enumerate(f[1:],1):
   scale=mult**i;newnwc=q['nwc']*scale;fcff=(q['nopat']+q['da']-q['capex'])*scale-(newnwc-nwc);vals.append(dict(year=q['year'],revenue=q['revenue']*scale,capex=q['capex']*scale,da=q['da']*scale,nwc=newnwc,fcff=fcff));nwc=newnwc
  tv=f[-1]['nopat']*mult**5*(1+c['g'])*(1-c['g']/c['roic'])/(w-c['g'])/(1+w)**5
  eq=sum(q['fcff']/(1+w)**i for i,q in enumerate(vals,1))+tv+r['bridge']['netcash_2026e']+p['h1']['nonop']-p['h1']['nci']
  return eq*1000/s,vals
 lo=.50;hi=2.0
 assert hurdle(lo)[0]<p['reference_price']<hurdle(hi)[0]
 for _ in range(100):
  mid=(lo+hi)/2
  if hurdle(mid)[0]<p['reference_price']:lo=mid
  else:hi=mid
 mult=(lo+hi)/2;price,path=hurdle(mult)
 z['price_hurdle_uplift']=mult-1;z['price_hurdle_dcf']=price;z['price_hurdle_2027_growth']=path[0]['revenue']/f[0]['revenue']-1;z['price_hurdle_path']=path
 ic=r['bridge']['book_2026e']-r['bridge']['netcash_2026e']-p['h1']['nonop'];op_returns=[]
 for q in f[1:]:
  op_returns.append(dict(year=q['year'],begin_operating_capital=ic,implied_roic=q['nopat']/ic));ic=q['end_book']-q['end_netcash']-p['h1']['nonop']
 z['operating_capital_2031']=ic;z['operating_returns']=op_returns
 z['all_assets_no_excess_dcf']=(r['pv_fcff']+ic/(1+w)**5+r['bridge']['netcash_2026e']+p['h1']['nonop']-p['h1']['nci'])*1000/s
 z['market_per_hurdle']=p['reference_price']/r['normalized_eps']
 z['first_duration_matching_price']=next((n for n in range(1,41) if r['normalized_eps']*jper(c['pergrowth'],c['perroe'],c['g'],c['roe'],c['ke'],n)>=p['reference_price']),None)
 return z

def detail_sections(p,r,z,table,num,pct,px):
 t=lambda h,rows:table(h,rows)+'\n';c=p['cases']['Base'];a=p['actual_aux'];f=r['forecast'];sh=r['bridge']['shares_mn']
 facts='### [실제 이익과 현금 회수의 차이]\n\n'
 facts+=f'H1 매출은 전년 동기 대비 {pct(p["h1"]["rev"]/190.932307676-1)}, 영업이익은 {pct(p["h1"]["op"]/88.382117361-1)} 증가했다. 영업현금흐름/순이익은 **{pct(z["h1_cash_conversion"])}**다. H1 영업현금 68.533에서 유형·무형 현금 취득 41.843을 빼면 참고 현금 잉여는 **26.689십억원**이다. 이 값은 공시 현금흐름 분류를 유지한 실제치이며, 정상 세금·이자·영업운전자본으로 재구성한 전망 FCFF와 정의가 다르다. H1 순이익 106.319가 전부 같은 기간 현금으로 들어온 것으로 해석하지 않는다. [S01]({next(s[3] for s in p["sources"] if s[0]=="S01")})\n\n'
 facts+=t(['H1 현금흐름을 움직인 항목','십억원','해석'],[['매출채권 증가의 현금흐름 효과',-46.811231304,'매출 인식과 현금 회수의 시차'],['재고 증가',-4.974621206,'선행 생산·재고 구성 확인'],['미지급비용 증가',23.665235726,'비용 발생과 현금 지급의 시차'],['예수금 감소',-11.7447568,'일시적 지급 항목; 전년과 비교'],['현금 세금 납부',-30.113083637,'손익 세금 비용 33.537과 시점 차이']])
 facts+='현금흐름 주석의 매출채권 증가와 재무상태표의 AR 증가액은 외화 환산·분류 등의 영향으로 다르다. 전망 NWC는 재무상태표 잔액을 사용하고 실제 CFO 설명은 현금흐름 주석을 사용한다. 두 표의 차이를 누락이나 회수 손실로 단정하지 않는다. 미지급비용은 성과급 전체 금액으로 확인된 항목이 아니므로 정산 가정의 명칭을 그대로 유지한다.\n'
 forecast='### [제품별 매출을 합치는 과정]\n\n'
 labels=['소켓','핀','의료·관련 상품','기타 상품']
 forecast+=t(['십억원','H1 실제','H2 Bear','H2 Base','H2 Bull'],[[labels[j],num(p['product_actuals'][j],3)]+[num(p['cases'][case]['h2'][j],3) for case in ['Bear','Base','Bull']] for j in range(4)])
 forecast+=t(['Base 제품군 성장률','2027','2028','2029','2030','2031'],[[labels[j]]+[pct(g) for g in c['pg'][j]] for j in range(4)])
 forecast+=t(['Base 매출, 십억원']+[str(y) for y in range(2026,2032)],[[labels[j]]+[num(v) for v in c['product_forecast'][name]] for j,name in enumerate(p['product_names'])])
 forecast+='2026E 각 제품 매출 = H1 실제 + H2 추정. 이후 제품 매출 = 전년 같은 제품 매출 × (1+그 제품 성장률). 전체 매출은 네 제품군 합계다. 총매출에 별도 AI 성장률을 다시 곱하지 않는다. 제품 구성과 전체 매출을 구분하기 위해 수요를 출하량·단가로 나누는 설명은 유지하되, 공개되지 않은 고객별 수량과 ASP는 입력하지 않았다. 생산실적 EA는 판매량이 아니며 소켓 안에 들어간 핀의 내부 수량과도 중복될 수 있다.\n\n'
 forecast+='제품군별 25%·15%·8%는 회귀분석으로 식별한 인과 계수나 회사 가이던스가 아니다. 소켓 비중 상승·설비 투자·기술개발이 성장 가능성을 뒷받침하는 사실이고, 각 수치는 이를 어느 정도 인정할지 정한 분석자 조건이다. Bear는 소켓 14%·핀 8%·의료 4%, Bull은 32%·20%·12%를 2027년에 적용한다. 다음 제품별 실제 매출이 어느 경로에 접근하는지 확인해 조건을 수정한다.\n\n'
 forecast+='### [회수일수·투자·할인율의 산정 근거]\n\n'
 forecast+=t(['Base 입력']+[str(y) for y in range(2026,2032)],[[name]+[num(v,1) for v in c[key]] for name,key in [('DSO, 일','dso'),('DIO, 일','dio'),('DPO, 일','dpo'),('CAPEX','capex'),('D&A','da')]])
 forecast+=f'DSO 실제 대용치는 2025년 말 **{num(z["dso_2025"])}일**, H1 매출을 두 배로 본 2026년 6월 말 **{num(z["dso_h1"])}일**이다. 평균 AR와 매일의 매출을 사용한 정확한 회전일수가 아니다. Base 2026년 65일은 두 실제 기말 지표 사이에서 일부 회복을 가정한 조건이고, 2027년 63일도 실제 회수가 개선돼야 성립한다. 반기 말 매출 집중과 환율의 영향을 확인할 때까지 75일대 Bear를 유지한다. DIO와 DPO도 기말 잔액 대용치로 검증하고, 32일·12일은 주문제작 생산의 재고와 짧은 매입 신용을 반영한 범위 가정이다.\n\n'
 forecast+=f'매출원가율 = 1-영업이익률-판관비율이다. Base 판관비율 {pct(c["sgaratio"])}를 사용하며, 2027년 매출원가율은 {pct(1-c["margin"][1]-c["sgaratio"])}다. NWC/매출 = DSO/365 + 매출원가율×(DIO-DPO)/365이므로 2027년 NWC 비율은 {pct(c["nwc"][1])}다. 판관비율은 H1 약 3.93%에서 교육·연구·관리 부담을 더 인정한 조건이다. 제품별 원가를 공시하지 않아 소켓 1개당 원가와 핀 1개당 원가를 역산하지 않았다. 이 비용 가정이 공개된 견적표라는 뜻도 아니다.\n\n'
 forecast+=f'공장 계획상 남은 건설·장비 투자 {num(z["project_remaining"],3)}를 2026H2 CAPEX {num(c["capex"][0]-p["h1"]["capex"],3)}에 포함했고, 차이 {num(z["h2_other_capex"],3)}는 다른 설비·무형 투자와 시점 조정에 대한 분석자 예산이다. 2027년 CAPEX 45와 D&A 21의 차이 24는 신규 투자다. 이 현금 지출에 NWC 증가를 더해 재투자액을 만든다. 증설은 현금 투입 시점과 매출 기여 시점이 다르므로 프로젝트 잔여 금액을 곧바로 매출로 환산하지 않는다.\n\n'
 forecast+='WACC와 자기자본비용은 Bear 11.5%·Base 10.5%·Bull 9.5%로 같게 둔다. 공시상 차입금은 없고 리스부채도 약 0.212여서 유의적인 부채 조달 비중을 가정해 WACC를 인위적으로 낮출 근거가 약하기 때문이다. 이 범위는 고객 집중·기술 대체·생산 이전의 불확실성을 점검하는 요구수익률 조건이다. 동일 날짜의 무위험금리·추정 베타·ERP·목표 자본구조를 모두 확보한 CAPM은 아직 산정하지 않았다. 따라서 10.5%를 시장에서 직접 관측한 할인율로 표시하지 않는다. ±1%p 표에서 결과가 얼마나 변하는지 함께 판단한다.\n\n'
 forecast+='성숙 성장률 2.5%는 원화 명목 장기 조건이며 회사의 현재 성장률을 영구 연장한 값이 아니다. 성숙 ROIC 15%와 WACC 10.5%의 차이는 4.5%p다. 높은 현재 수익성이 계속되더라도 경쟁·가격·추가 투자에 의해 초과수익이 줄어드는 조건을 둔다. 이 15%는 새 공장의 개별 투자수익률을 공시에서 확인한 값이 아니다. 성숙 ROIC=WACC의 소멸 경로와 함께 읽어야 한다. 성숙 ROE 12%는 현금을 포함한 장부자본에 적용되는 별도 조건이며 현금 축적에 따른 하락 부담은 RIM 민감도에서 점검한다.\n'
 peer='### [ISC 한 곳을 직접 비교에 남기는 이유]\n\n'
 peer+='정량 후보를 통과시키는 조건은 ① 검사 접촉 부품의 외부 매출 존재 ② 개발·양산·번인의 수요 차이 식별 ③ 장비·서비스가 섞인 범위 확인 ④ 지배주주 순이익과 회계기간 대사 ⑤ 동일 날짜·공급사 가격과 주식수 사용이다. ISC는 소켓·핀과 한국 회계·12월 결산을 공유해 직접 비교 대상으로 남겼다. 제품 방식·성장률·투자 계획이 같다는 의미는 아니다. Yamaichi와 Cohu의 전사 배수를 함께 평균하면 커넥터·장비·서비스의 이익과 국가별 요구수익률이 섞이므로 제품·기술 비교에 사용한다.\n\n'
 peers=[]
 for q in p['peer_actuals']:
  ni=q['ni25']-q['nih125']+q['nih126'];eps=ni*1000/q['shares'];pe=q['price']/eps
  peers.append([q['name'],num(ni,3),num(q['shares'],6),num(eps,0),num(q['price'],0),num(pe,2),pct(q['margin'])])
 peer+=t(['동일 2026-10-16','TTM NI','경제주식, 백만','NI/현재주식, 원','참고가격','참고 PER','H1 OP마진'],peers)
 peer+='TTM NI = 2025A 지배 순이익 - 2025H1 지배 순이익 + 2026H1 지배 순이익. 위 주당이익은 TTM NI를 H1 말 경제적 주식수로 나눈 비교용 값이며, 기간별 가중평균 주식수를 사용하는 공시 기본 EPS와 정의가 다르다. 특히 ISC는 2026년 4월 교환사채 교환으로 자기주식 678,259주가 교부됐으므로 과거 EPS를 현재 주식수와 섞지 않았다. 양사의 가격은 NAVER 10월 16일, 주식수는 6월 말이다. 후속 자본거래를 모두 확인한 10월 현재 분모로 주장하지 않는다.\n\n'
 peer+='ISC 공식 IR은 요약 표와 Appendix의 1Q26·누적 순이익 및 EPS가 다르게 나타난다. 본 비교는 DART H1 지배 순이익 39.758, 전년 H1 18.333, 2025A 56.129를 사용한다. IR의 전체 순이익·지배 순이익·주당이익을 섞어 숫자를 맞추지 않는다. P01·P02·P03·P07을 함께 확인할 수 있다. ISC의 9월 28일 공시는 기존 100% 자회사 ISC VINA에 29.744십억원을 추가 출자하는 결정이다. 외부 기업 인수로 분류하지 않는다. 추가 거점·인프라 투자에 따른 현금 사용과 향후 생산능력은 재점검해야 하며 과거 TTM 배수에 미래 투자 이익을 자동 반영하지 않는다.\n\n'
 peer+='위 표에서 리노공업의 관측 배수가 ISC보다 낮더라도 곧바로 저평가라고 판단하지 않는다. ISC의 성장 기대, 자본거래와 제품 구성, 리노공업의 정상 마진·가동 위험이 다르다. 반대로 리노공업의 H1 마진이 높다는 사실만으로 일정 %의 배수 프리미엄을 가산하지 않는다. 분석의 다음 단계는 두 기업의 동일 기준 정상화 이익과 재투자를 만드는 것이다. 현재 보고서는 관측 TTM과 리노공업의 이론 forward PER를 명확히 구분한다.\n'
 forecast+='### [기존 영업자본과 신규 투자수익률의 구분]\n\n'
 forecast+=t(['연도','기초 영업자본 대용, 십억원','NOPAT/기초 영업자본'],[[q['year'],num(q['begin_operating_capital']),pct(q['implied_roic'])] for q in z['operating_returns']])
 forecast+='영업자본 대용치는 주주자본-순현금-별도 가산 비영업자산으로 구했다. 계정별 영업자산·부채를 모두 분리한 확정 투하자본과는 차이가 있다. 특히 미지급비용·연금·이연세금의 분류와 회계상 인식하지 않은 기술·고객 기반의 영향을 받는다. 위 높은 수익률은 현재 마진과 비교적 낮은 순투자가 유지된다는 명시기간 가정의 결과다. 새 공장의 실제 수익률을 직접 측정한 수치가 아니다.\n\n'
 forecast+='DCF 잔존가치의 g/ROIC 식에서 15%는 성숙기에 추가로 투입하는 자본의 한계수익률 조건으로 해석한다. 2031년까지 형성된 영업자산의 높은 수익성을 2032년에 모두 15%로 재설정한 것은 아니다. 신규 투자 ROIC=WACC만 적용해도 기존 자산의 이익은 남을 수 있다. 따라서 이 민감도를 전체 경쟁우위가 사라지는 가치로 부르지 않는다. 기존 영업자산까지 초과수익을 잃는 조건은 다음 별도 표에 제시한다.\n'
 premium='### [프리미엄의 크기를 변수로 설명하는 계산]\n\n'
 premium+='다음은 시장 peer를 가공한 표가 아닌 이론 조건 실험이다. 성숙 g=2.5%·성숙 ROE=12%·초과성장 기간 5년을 고정하고 성장률·증분 ROE·ke를 순서대로 변경한다. 동일한 EPS에서 자본을 얼마나 남겨 성장에 써야 하는지와 위험을 분리해 보기 위한 기준이다.\n\n'
 prev=None;rows=[]
 for q in z['premium_steps']:
  rows.append([q['label'],num(q['per'],2),'기준' if prev is None else f'{q["per"]-prev:+.2f}배']);prev=q['per']
 premium+=t(['동일 정상 EPS에 적용한 조건','이론 PER','직전 단계 변화'],rows)
 premium+='단계별 변화는 순서에 따라 달라질 수 있다. 특정 기술에 고유하게 귀속되는 관측 프리미엄으로 사용하지 않는다. 증분 ROE 30%를 정당화하려면 추가 투자 이후 세후 이익과 현금 회수가 확인돼야 한다. 역사적 전체 ROE와 증분 ROE는 분모가 다르므로 같은 수치로 바꾸지 않는다. Base 성장 12%는 5년 명시 Forecast의 실제 EPS 성장률을 복사한 값도 아니다. 정상화한 2027 EPS에서 시작하는 별도 분배가능이익 경로이며 보고 EPS의 고점·저점 효과를 줄이는 비교 조건이다.\n\n'
 premium+=t(['초과성장 기간','이론 PER','주당가치'],[[q['years'],num(q['per'],2),px(q['price'])] for q in z['duration_prices']])
 premium+=f'정상화 EPS에 참고가격을 맞추려면 **{num(z["market_per_hurdle"],2)}배**가 필요하다. Base 성장·증분 ROE·ke·성숙 조건을 모두 고정했을 때 이 가격에 도달하는 첫 정수 기간은 **{z["first_duration_matching_price"] if z["first_duration_matching_price"] is not None else "40년 이내 없음"}년**이다. 이 역산은 그 기간 동안 경쟁우위가 보장된다는 증거가 아니다. 장기간 성장률이 요구수익률보다 높은 경로는 큰 가정 부담을 지므로, 이 값을 매수 근거로 사용하지 않는다. 제품 채택·고객 유지·자본수익률 자료가 이 기간을 설명할 수 있는지 검토하는 질문이다.\n'
 special='### [같은 투자비율에서 참고가격을 설명하는 매출 경로]\n\n'
 special+=f'5년 뒤 마진 하나만 조정하는 역산에는 한계가 있어, 매출 경로 전체를 바꾸는 조건도 계산했다. 2026년 매출·연말 현금은 유지하고 2027~2031 각 연도의 제품군 성장계수에 공통 계수 **1+{pct(z["price_hurdle_uplift"])}**를 곱한다. 연도 t의 매출은 기존 Base 매출×(1+추가 계수)^t다. 매출에 대한 CAPEX·D&A·NWC 비율은 유지한다. 그 결과 2027년 전체 매출 성장률은 **{pct(z["price_hurdle_2027_growth"])}**가 필요하고, DCF는 참고가격 {px(z["price_hurdle_dcf"])}와 일치한다.\n\n'
 special+=t(['십억원','2027','2028','2029','2030','2031'],[[label]+[num(q[key]) for q in z['price_hurdle_path']] for label,key in [('필요 매출','revenue'),('이에 대응한 CAPEX','capex'),('D&A','da'),('NWC','nwc'),('FCFF','fcff')]])
 special+='매출 성장률에 추가 계수를 곱할 때 원래 성장률에 같은 %p를 더하는 계산과 다르다. 예를 들어 원래 20% 성장에 계수 1.10을 곱하면 새 성장률은 32%다. 위 경로에서는 투자 금액도 증가시켜 추가 매출이 투자 없이 발생한다는 가정을 피했다. 다만 같은 설비 투자비율·감가비율·마진으로 높은 성장을 감당할 수 있는지는 별도 검증이 필요하다. 수주나 생산능력으로 확인한 전망이 아니며 bisection으로 가격을 맞춘 역산 결과다. WACC·성숙 g·ROIC·현금 가산을 바꾸면 필요한 계수도 달라진다.\n\n'
 special+='### [기존 영업자산까지 초과수익을 잃는 조건]\n\n'
 special+=f'2031년 말 영업자본 대용치는 **{num(z["operating_capital_2031"])}십억원**이다. 2032년 NOPAT을 이 자본×WACC로 낮추고 이후 자본이 g로 성장하도록 재투자하면, terminal EV는 이 영업자본과 같아진다. 이때 DCF는 **{px(z["all_assets_no_excess_dcf"])}**다. 이 계산은 2027~2031년 전망·연말 현금·비영업 자산을 고정하고 기존 자산의 초과수익까지 2032년에 사라지는 강한 조건이다.\n\n'
 special+='산식은 NOPAT_2032=WACC×IC_2031, 재투자율=g/WACC, TV_2031=NOPAT_2032×(1-g/WACC)/(WACC-g)=IC_2031이다. IC_2031에 g를 추가로 곱하지 않는다. 이 경로는 이익이 급격히 낮아지는 스트레스이며 실적 전망이나 청산가치가 아니다. 신규 투자 수익률만 WACC로 두는 민감도와 구분해 경쟁우위의 지속에 관한 가정 부담을 확인한다.\n\n'
 special+='### [고객·회수·ELS·미지급비용의 영향]\n\n'
 special+=t(['점검','산출값','조건'],[['DSO +15일의 2027 추가 자금',num(z['dso_15day_liquidity'])+'십억원','가치 하락액이 아닌 필요 운전자금'],['고객 A 매출 10% 감소, 2027 한 해',px(z['customer_one_year_dcf']),'A 비중 고정·기여마진 50%·세후 충격'],['H2 미지급비용 정산을 누락한 DCF',px(z['ignored_accrual_dcf']),'기본 DCF는 정산 현금 -23.665 포함'],['ELS 장부금액 20% 가치조정 DCF',px(z['els_haircut_dcf']),'20%는 세율·관측 손실률이 아닌 가격 민감도']])
 special+='고객 A의 실제 이름과 제품별 거래조건은 공시되지 않았다. A 비중은 H1 실제 57.881/242.959를 사용한다. 10% 감소와 기여마진 50%는 임의로 고른 스트레스 크기이며 발생 확률을 추정하지 않는다. 단기 고정비를 유지하고 2027년 세후 영업이익·현금흐름의 감소만 할인했다. 2028년 이후 매출과 terminal은 고정했고 매출 감소에 따른 NWC 회수도 0으로 두었으므로 전사 시나리오와 구분한다.\n\n'
 special+='DSO 15일은 2027년 매출×15/365만큼의 자금 수요다. 회수 시점을 정하지 않고 이를 영구 손실이나 목표주가 차감액으로 바꾸지 않았다. ELS 가치조정은 비영업 자산 가산액에만 적용하며 정기예금에 같은 손실률을 적용하지 않는다. 미지급비용 정산은 이미 인식한 비용의 현금 지급이므로 추가 EBIT 비용으로 중복 차감하지 않는다.\n'
 return dict(facts=facts,forecast=forecast,peer=peer,premium=premium,special=special)
