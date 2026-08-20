import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='MaterialLoop Local', page_icon='♻️', layout='wide')

REQUIRED = ['record_id','site_code','record_type','material_type','material_grade','quantity_tonnes','quality_score','condition_score','reusability_score','available_date','demand_date','source_zone','demand_zone','transport_distance_km','transport_capacity_tonnes','transport_cost_per_tonne','estimated_carbon_saving_kgco2e','processing_required_score','contamination_risk_score','storage_readiness_score','buyer_readiness_score','match_status']
SAMPLE = '''record_id,site_code,record_type,material_type,material_grade,quantity_tonnes,quality_score,condition_score,reusability_score,available_date,demand_date,source_zone,demand_zone,transport_distance_km,transport_capacity_tonnes,transport_cost_per_tonne,estimated_carbon_saving_kgco2e,processing_required_score,contamination_risk_score,storage_readiness_score,buyer_readiness_score,match_status
R001,DEM-101,SOURCE,Structural Steel,S355,42,94,91,95,2026-09-02,2026-09-08,Zone-A,Zone-C,18,50,14,38500,12,5,92,96,Ready
R002,DEM-102,SOURCE,Red Brick,Standard,28,88,86,90,2026-09-05,2026-09-12,Zone-B,Zone-C,26,30,11,16800,22,8,88,90,Ready
R003,DEM-103,SOURCE,Concrete,Grade-30,65,82,79,84,2026-09-10,2026-09-18,Zone-D,Zone-A,41,70,19,27600,38,12,76,84,Review
R004,DEM-104,SOURCE,Timber,C24,16,91,89,93,2026-09-03,2026-09-07,Zone-A,Zone-B,12,20,9,11200,15,7,95,94,Ready
R005,DEM-105,SOURCE,Glass,Tempered,9,86,83,87,2026-09-15,2026-09-21,Zone-C,Zone-D,34,12,16,4900,28,10,84,80,Review
R006,DEM-106,SOURCE,Floor Tile,Porcelain,22,78,76,80,2026-09-06,2026-09-14,Zone-B,Zone-A,20,25,10,8200,30,16,86,78,Review
R007,CST-201,DEMAND,Structural Steel,S355,38,90,0,0,2026-09-08,2026-09-08,Zone-C,Zone-C,0,0,0,0,0,0,0,93,Open
R008,CST-202,DEMAND,Red Brick,Standard,24,88,0,0,2026-09-12,2026-09-12,Zone-C,Zone-B,0,0,0,0,0,0,0,89,Open
R009,CST-203,DEMAND,Timber,C24,14,92,0,0,2026-09-07,2026-09-07,Zone-B,Zone-A,0,0,0,0,0,0,0,95,Open
R010,CST-204,DEMAND,Concrete,Grade-30,52,86,0,0,2026-09-18,2026-09-18,Zone-A,Zone-D,0,0,0,0,0,0,0,82,Open
R011,CST-205,DEMAND,Glass,Tempered,8,84,0,0,2026-09-21,2026-09-21,Zone-D,Zone-C,0,0,0,0,0,0,0,79,Open
R012,CST-206,DEMAND,Floor Tile,Porcelain,18,81,0,0,2026-09-14,2026-09-14,Zone-A,Zone-B,0,0,0,0,0,0,0,86,Open
'''

st.markdown('''<style>
.stApp{background:#f6faf8;color:#17332a}.block-container{max-width:1450px;padding-top:1.2rem}.hero{background:linear-gradient(135deg,#fff,#e5f4ec);border:1px solid #d7e8df;border-radius:24px;padding:28px 32px;box-shadow:0 8px 28px rgba(27,83,62,.07)}.hero h1{margin:0;font-size:2.5rem;letter-spacing:-1px}.hero p{color:#5e746b;margin:.35rem 0}.section{font-size:1.12rem;font-weight:750;margin:22px 0 10px}.card{background:#fff;border:1px solid #d7e8df;border-radius:18px;padding:18px;box-shadow:0 5px 18px rgba(27,83,62,.05)}.muted{color:#60766d}.stButton>button{border-radius:11px;color:#15523e;border:1px solid #b9d8c9;background:#fff}.stDownloadButton>button{border-radius:11px;background:#19775a;color:#fff;border:0}div[data-testid='stMetric']{background:#fff;border:1px solid #d7e8df;border-radius:16px;padding:10px}
</style>''', unsafe_allow_html=True)

st.markdown('''<div class="hero"><h1>♻️ MaterialLoop Local</h1><p><b>Construction Material Reuse Matcher</b> — screen reusable demolition materials against construction demand using quality, quantity, timing, transport, readiness and indicative carbon-saving signals.</p><p class="muted">100% local processing • No external APIs • Explainable screening • Human review</p></div>''', unsafe_allow_html=True)

def score_source(r):
    transport = max(0, 100 - min(float(r.transport_distance_km)/1.5,100))
    carbon = min(float(r.estimated_carbon_saving_kgco2e)/400,100)
    return round(float(np.clip(.18*r.quality_score+.18*r.condition_score+.20*r.reusability_score+.10*r.storage_readiness_score+.12*r.buyer_readiness_score+.10*transport+.07*carbon+.05*(100-r.contamination_risk_score)+.05*(100-r.processing_required_score),0,100)),1)

def classify(x):
    return 'Excellent Match' if x>=85 else 'Strong Match' if x>=70 else 'Review' if x>=55 else 'Low Priority'

def prepare(df):
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError('Missing required columns: '+', '.join(missing))
    df=df.copy()
    nums=['quantity_tonnes','quality_score','condition_score','reusability_score','transport_distance_km','transport_capacity_tonnes','transport_cost_per_tonne','estimated_carbon_saving_kgco2e','processing_required_score','contamination_risk_score','storage_readiness_score','buyer_readiness_score']
    for c in nums: df[c]=pd.to_numeric(df[c],errors='coerce')
    df['available_date']=pd.to_datetime(df['available_date'],errors='coerce'); df['demand_date']=pd.to_datetime(df['demand_date'],errors='coerce')
    if df[nums].isna().any().any(): raise ValueError('Numeric fields contain invalid or missing values.')
    source=df.record_type.astype(str).str.upper().eq('SOURCE'); df['reuse_screen_score']=np.nan; df.loc[source,'reuse_screen_score']=df.loc[source].apply(score_source,axis=1); df['screening_class']=df.reuse_screen_score.apply(lambda x: classify(x) if pd.notna(x) else 'Demand Record')
    return df

def matches_for(df):
    s=df[df.record_type.str.upper().eq('SOURCE')]; d=df[df.record_type.str.upper().eq('DEMAND')]; rows=[]
    for _,a in s.iterrows():
        for _,b in d[d.material_type.eq(a.material_type)].iterrows():
            grade=100 if str(a.material_grade).lower()==str(b.material_grade).lower() else 55; qty=min(a.quantity_tonnes/max(b.quantity_tonnes,.01),1)*100; timing=max(0,100-abs((a.demand_date-b.demand_date).days)*12); dist=max(0,100-min(a.transport_distance_km/1.5,100)); carbon=min(a.estimated_carbon_saving_kgco2e/400,100)
            score=.30*a.reuse_screen_score+.18*grade+.15*qty+.12*timing+.12*dist+.08*carbon+.05*b.buyer_readiness_score
            rows.append({'source_id':a.record_id,'demand_id':b.record_id,'material_type':a.material_type,'source_zone':a.source_zone,'demand_zone':b.demand_zone,'available_date':a.available_date.date(),'required_date':b.demand_date.date(),'source_qty_t':a.quantity_tonnes,'demand_qty_t':b.quantity_tonnes,'transport_km':a.transport_distance_km,'carbon_saving_kgco2e':a.estimated_carbon_saving_kgco2e,'match_score':round(float(np.clip(score,0,100)),1)})
    out=pd.DataFrame(rows)
    if not out.empty: out['match_class']=out.match_score.apply(classify); out=out.sort_values('match_score',ascending=False)
    return out

with st.sidebar:
    st.markdown('### ♻️ MaterialLoop')
    page=st.radio('Workspace',['Overview','Match Studio','Registry','Methodology'])
    up=st.file_uploader('Upload authorized CSV',type=['csv'])
    if up:
        try: st.session_state.df=prepare(pd.read_csv(up)); st.success(f'Loaded {len(st.session_state.df):,} records')
        except Exception as e: st.error(str(e))
    if 'df' not in st.session_state: st.session_state.df=prepare(pd.read_csv(io.StringIO(SAMPLE)))
    st.download_button('Download sample CSV',SAMPLE,'material_reuse_sample.csv','text/csv')

df=st.session_state.df; src=df[df.record_type.str.upper().eq('SOURCE')]; dem=df[df.record_type.str.upper().eq('DEMAND')]; mt=matches_for(df)

if page=='Overview':
    st.markdown('<div class="section">Circular-material command center</div>',unsafe_allow_html=True)
    c=st.columns(5)
    for col,label,val in zip(c,['Source lots','Demand records','Reusable tonnes','Candidate matches','Indicative carbon signal'],[len(src),len(dem),f'{src.quantity_tonnes.sum():,.1f} t',len(mt),f'{src.estimated_carbon_saving_kgco2e.sum()/1000:,.1f} tCO₂e']):
        col.metric(label,val)
    a,b=st.columns([1.25,1])
    with a:
        x=src.groupby('material_type',as_index=False).quantity_tonnes.sum().sort_values('quantity_tonnes',ascending=False); fig=px.bar(x,x='material_type',y='quantity_tonnes',title='Reusable material inventory'); fig.update_layout(height=370,plot_bgcolor='white',paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)
    with b:
        x=src.screening_class.value_counts().reset_index(); x.columns=['classification','count']; fig=px.pie(x,names='classification',values='count',hole=.58,title='Source readiness profile'); fig.update_layout(height=370,paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section">Top reuse opportunities</div>',unsafe_allow_html=True); st.dataframe(mt.head(8),use_container_width=True,hide_index=True)

elif page=='Match Studio':
    st.markdown('<div class="section">Match Studio</div>',unsafe_allow_html=True); st.caption('Transparent planning matches; not certification of structural suitability, regulatory acceptance or commercial feasibility.')
    c1,c2=st.columns([1,1]);
    with c1: choice=st.selectbox('Material type',['All']+sorted(mt.material_type.unique().tolist()) if not mt.empty else ['All'])
    with c2: threshold=st.slider('Minimum match score',0,100,65)
    view=mt[mt.match_score>=threshold].copy() if not mt.empty else mt
    if choice!='All': view=view[view.material_type.eq(choice)]
    st.metric('Candidate matches',len(view)); st.dataframe(view,use_container_width=True,hide_index=True); st.download_button('Export scored match queue',view.to_csv(index=False),'scored_material_matches.csv','text/csv')
    if not view.empty:
        fig=px.scatter(view,x='transport_km',y='match_score',size='source_qty_t',color='material_type',hover_data=['source_id','demand_id','carbon_saving_kgco2e'],title='Match quality vs transport distance'); fig.update_layout(height=430,plot_bgcolor='white',paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)

elif page=='Registry':
    st.markdown('<div class="section">Local material registry</div>',unsafe_allow_html=True); filt=st.multiselect('Material types',sorted(df.material_type.unique()),default=sorted(df.material_type.unique())); view=df[df.material_type.isin(filt)]; st.dataframe(view,use_container_width=True,hide_index=True); st.download_button('Export registry',view.to_csv(index=False),'material_reuse_registry.csv','text/csv')
    x=src[src.material_type.isin(filt)].groupby('material_type',as_index=False)[['quality_score','condition_score','reusability_score']].mean().melt('material_type',var_name='signal',value_name='score'); fig=px.bar(x,x='material_type',y='score',color='signal',barmode='group',title='Material readiness signals'); fig.update_layout(height=400,plot_bgcolor='white',paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown('<div class="section">Methodology & responsible use</div>',unsafe_allow_html=True)
    st.markdown('''**Purpose:** prioritize possible reuse pairings between demolition/deconstruction material lots and construction demand records.\n\n**Source screening weights:** quality 18%, condition 18%, reusability 20%, storage readiness 10%, buyer readiness 12%, transport fit 10%, carbon-saving signal 7%, contamination-risk inverse 5%, processing-burden inverse 5%.\n\n**Limitations:** scores do not certify structural performance, contamination status, hazardous-material status, fire/code compliance, ownership, waste/product classification, legal transferability, transport legality, or actual lifecycle-carbon savings. Qualified technical, environmental, safety, legal and commercial review remains necessary.\n\n**Privacy:** uploaded CSV data is processed locally; no external APIs are used.''')

st.divider(); st.caption('MaterialLoop Local • 100% local processing • No external APIs • Synthetic or authorized records only')
