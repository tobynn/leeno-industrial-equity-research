from pathlib import Path
import argparse,json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt,font_manager
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--font',type=Path);args=ap.parse_args()
if args.font and args.font.exists():font_manager.fontManager.addfont(str(args.font));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(args.font)).get_name()
else:plt.rcParams['font.family']='NanumGothic'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.unicode_minus':False,'figure.facecolor':'white','axes.facecolor':'white'})
p=json.loads((ROOT/'data/research_inputs.json').read_text());rs=json.loads((ROOT/'model/research_results.json').read_text());c=p['cases']['Base'];out=ROOT/'report/figures';out.mkdir(exist_ok=True)
colors=['#175E68','#488C99','#8BB8BF','#D8D4C7'];years=['2025A']+[f'{y}E' for y in range(2026,2032)];fig,ax=plt.subplots(figsize=(9,4));bottom=np.zeros(7)
for j,name in enumerate(p['product_names']):
 vals=np.array([[243.944034,87.100284,41.351312,.138455][j]]+c['product_forecast'][name]);ax.bar(years,vals,bottom=bottom,color=colors[j],label=['소켓','핀','의료·관련 상품','기타'][j],width=.58);bottom+=vals
ax.set_ylabel('십억원');ax.set_title('제품군 매출 | 2025 실제와 Base 전망',loc='left',fontweight='bold',pad=18);ax.legend(ncol=4,frameon=False,loc='upper left');ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);fig.tight_layout();fig.savefig(out/'revenue_build.png',dpi=170,bbox_inches='tight');plt.close(fig)
hist=p['hist'][:3];labels=[h[0] for h in hist]+['2026H1A']+[f'{y}E' for y in range(2026,2032)];v=[h[2]/h[1]*100 for h in hist]+[p['h1']['op']/p['h1']['rev']*100]+[m*100 for m in c['margin']];fig,ax=plt.subplots(figsize=(9,3.8));ax.plot(range(4),v[:4],marker='o',color='#175E68',label='공시 실제');ax.plot(range(3,len(v)),v[3:],marker='o',linestyle='--',color='#A8752E',label='Base 전망');ax.axhline(c['permargin']*100,color='#7C8991',linestyle=':',label='PER 정상 마진');ax.set_xticks(range(len(labels)),labels,rotation=25);ax.set_ylim(40,54);ax.set_ylabel('%');ax.set_title('영업이익률 | 최고 수익성과 정상 이익의 구분',loc='left',fontweight='bold',pad=18);ax.grid(axis='y',alpha=.18);ax.legend(frameon=False,ncol=3,loc='upper left');fig.tight_layout();fig.savefig(out/'operating_margin.png',dpi=170,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(9,3.8));labels=['DCF','이론 PER','RIM'];keys=['dcf_price','per_price','rim_price']
for j,case in enumerate(['Bear','Base','Bull']):ax.bar(np.arange(3)+(j-1)*.22,[rs[case][k] for k in keys],width=.2,color=['#A6B0B6','#175E68','#C69C5F'][j],label=case)
ax.axhline(p['reference_price'],color='#A34E3E',linestyle='--',linewidth=1.4,label=f'참고가격 {p["reference_price"]:,.0f}원');ax.set_xticks(range(3),labels);ax.set_ylabel('원 / 주');ax.set_title('조건부 주당가치 | 2026년 말 평가',loc='left',fontweight='bold',pad=18);ax.legend(frameon=False,ncol=4,loc='upper left');ax.set_ylim(0,max(p['reference_price']*1.25,max(rs['Bull'][k] for k in keys)*1.22));ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);fig.tight_layout();fig.savefig(out/'valuation_cases.png',dpi=170,bbox_inches='tight');plt.close(fig)
print('Three source-linked figures exported')
