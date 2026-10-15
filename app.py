from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
import database

st.set_page_config(page_title="CarbonLens AI", page_icon="🌿", layout="wide")
database.create_table()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--forest:#12372a;--green:#246b45;--leaf:#55b879;--mint:#eaf7ef;--canvas:#f6f9f6;--ink:#172820;--muted:#6b7d72;--line:#dce8df}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(circle at 90% 0%,rgba(85,184,121,.10),transparent 28%),var(--canvas);color:var(--ink)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#12372a,#174532);border-right:1px solid #214c39}
[data-testid="stSidebar"] *{color:#f3fbf5}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#c4ddcd}
.brand{font-family:Manrope,sans-serif;font-size:29px;font-weight:800;letter-spacing:-1px;color:var(--forest);margin:0}
.kicker{font-size:11px;letter-spacing:1.7px;color:#318154;font-weight:700;text-transform:uppercase}
.hero{background:linear-gradient(115deg,#12372a,#1f6345 72%,#2c8055);border-radius:22px;padding:28px;color:#fff;margin:12px 0 24px;box-shadow:0 15px 36px #12372a18}
.hero h1{font-family:Manrope,sans-serif;color:white;font-size:clamp(25px,3vw,36px);letter-spacing:-1px;margin:0 0 8px}
.hero p{color:#d5ebdd;font-size:14px;margin:0}
.pill{display:inline-block;background:#ffffff20;border:1px solid #ffffff35;padding:5px 10px;border-radius:99px;font-size:10px;letter-spacing:1px;margin-bottom:12px}
.section-title{font-family:Manrope,sans-serif;font-size:23px;font-weight:800;color:var(--forest);letter-spacing:-.5px}
.section-note{font-size:13px;color:var(--muted);margin-bottom:18px}
[data-testid="stMetric"]{background:white;border:1px solid var(--line);padding:16px;border-radius:16px;box-shadow:0 4px 16px #1a3e2a08}
[data-testid="stMetricLabel"]{color:var(--muted);font-size:12px}
[data-testid="stMetricValue"]{color:var(--forest);font-family:Manrope,sans-serif;font-weight:800}
div[data-testid="stForm"]{background:white;border:1px solid var(--line);border-radius:18px;padding:18px}
div.stButton>button,div.stFormSubmitButton>button,div[data-testid="stDownloadButton"]>button{border-radius:11px;min-height:42px;font-weight:700;transition:all .18s}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primary"]{background:var(--green);color:white;border:1px solid var(--green)}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{transform:translateY(-1px);box-shadow:0 6px 15px #1d513b20}
[data-testid="stPlotlyChart"]{background:white;border:1px solid var(--line);border-radius:17px;padding:8px}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden}
hr{border-color:var(--line)}
.footer{text-align:center;color:#809087;font-size:11px;padding:22px 0 8px}
@media(max-width:768px){.hero{padding:20px;border-radius:16px}.brand{font-size:24px}}
</style>
""", unsafe_allow_html=True)

ELECTRICITY_FACTOR = 0.70  # illustrative kg CO2/kWh
TRANSPORT_FACTOR = 0.12    # illustrative kg CO2/vehicle-km
WASTE_FACTOR = 0.50        # illustrative kg CO2/kg waste
AC_POWER_KW = 2.0          # illustrative average AC load

def intro(tag, title, note):
    st.markdown(f'<div class="kicker">{tag}</div><div class="section-title">{title}</div><div class="section-note">{note}</div>', unsafe_allow_html=True)

def calculate_emissions(electricity_kwh, vehicles, distance_km, solar_kwh, ac_hours, waste_kg):
    ac_electricity = ac_hours * AC_POWER_KW
    grid_electricity = max(0.0, electricity_kwh + ac_electricity - solar_kwh)
    electricity_emissions = grid_electricity * ELECTRICITY_FACTOR
    transport_emissions = vehicles * distance_km * TRANSPORT_FACTOR
    waste_emissions = waste_kg * WASTE_FACTOR
    return {
        "Electricity": electricity_emissions,
        "Transportation": transport_emissions,
        "Waste": waste_emissions,
        "Total": electricity_emissions + transport_emissions + waste_emissions,
        "Grid electricity": grid_electricity,
        "AC electricity": ac_electricity,
    }

def emission_chart(result, title="Emission breakdown"):
    df = pd.DataFrame({"Source":["Electricity","Transportation","Waste"],
                       "Emissions (kg CO₂/day)":[result["Electricity"],result["Transportation"],result["Waste"]]})
    fig = px.pie(df, names="Source", values="Emissions (kg CO₂/day)", title=title, hole=.58,
                 color_discrete_sequence=["#246b45","#7ccb91","#d7a84f"])
    fig.update_layout(margin=dict(l=12,r=12,t=55,b=25),paper_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color="#294235"),
                      legend=dict(orientation="h",yanchor="bottom",y=-.12,xanchor="center",x=.5))
    st.plotly_chart(fig,use_container_width=True)

with st.sidebar:
    st.markdown("## 🌿 CarbonLens AI")
    st.caption("CARBON INTELLIGENCE PLATFORM")
    page = st.radio("Workspace", ["Dashboard","Carbon Prediction","Digital Twin","AI Recommendations","Data History"])
    st.divider()

logo = Path(__file__).parent / "logo.png"
if logo.exists():
    c1,c2 = st.columns([.7,6],vertical_alignment="center")
    with c1: st.image(str(logo),width=100)
    with c2:
        st.markdown('<div class="brand">CarbonLens AI</div><div class="kicker">AI-powered carbon intelligence</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="brand">🌿 CarbonLens AI</div><div class="kicker">AI-powered carbon intelligence</div>',unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<span class="pill">● SUSTAINABILITY CONTROL CENTER</span>
<h1>Measure today. Improve tomorrow.</h1>
<p>Explore your campus carbon footprint, simulate greener choices, and turn activity data into practical sustainability actions.</p>
</div>
""",unsafe_allow_html=True)

if page == "Dashboard":
    intro("OVERVIEW","Campus carbon overview","A quick snapshot of campus activity and emission trends.")
    a,b,c,d=st.columns(4)
    a.metric("Estimated CO₂","1,420 kg","Sample data")
    b.metric("Electricity use","850 kWh","Per day · sample")
    c.metric("Vehicles tracked","150","Per day · sample")
    d.metric("Solar generation","200 kWh","Per day · sample")
    left,right=st.columns([1.8,1],gap="large")
    with left:
        monthly=pd.DataFrame({"Month":["May","June","July","August","September","October"],"Emissions (kg CO₂)":[1800,1650,1580,1490,1450,1420]})
        fig=px.area(monthly,x="Month",y="Emissions (kg CO₂)",markers=True,title="Monthly emissions trend · sample data",color_discrete_sequence=["#32915b"])
        fig.update_traces(line=dict(width=3),fillcolor="rgba(85,184,121,.16)")
        fig.update_layout(margin=dict(l=15,r=15,t=60,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color="#294235"))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("### 🌱 Focus areas")
        st.success("⚡ Improve energy efficiency")
        st.info("🚌 Encourage low-carbon travel")
        st.warning("♻️ Reduce and sort campus waste")
        st.write("Go to **Carbon Prediction** to estimate your own daily footprint.")
    st.caption("Dashboard figures are illustrative sample data.")

elif page == "Carbon Prediction":
    intro("CALCULATOR","Carbon emission estimator","Adjust the inputs, calculate your footprint, and inspect the source breakdown.")
    st.info("Example factors are used for demonstration. Replace them with verified local factors before formal reporting.")
    with st.form("predict"):
        x,y=st.columns(2)
        with x:
            electricity=st.number_input("Electricity consumption (kWh/day)",min_value=0.0,value=850.0,step=50.0)
            vehicles=st.number_input("Vehicles per day",min_value=0,value=150,step=10)
            distance=st.number_input("Average distance per vehicle (km/day)",min_value=0.0,value=10.0,step=1.0)
        with y:
            solar=st.number_input("Solar generation (kWh/day)",min_value=0.0,value=200.0,step=20.0)
            ac=st.number_input("Air-conditioning use (hours/day)",min_value=0.0,max_value=24.0,value=8.0,step=1.0)
            waste=st.number_input("Waste generated (kg/day)",min_value=0.0,value=180.0,step=10.0)
        run=st.form_submit_button("Calculate my footprint",type="primary",use_container_width=True)
    if run:
        result=calculate_emissions(electricity,vehicles,distance,solar,ac,waste)
        st.success("Your estimate is ready.")
        a,b,c=st.columns(3)
        a.metric("Electricity emissions",f"{result['Electricity']:,.2f} kg/day")
        b.metric("Transport emissions",f"{result['Transportation']:,.2f} kg/day")
        c.metric("Waste emissions",f"{result['Waste']:,.2f} kg/day")
        st.metric("Total estimated emissions",f"{result['Total']:,.2f} kg CO₂/day")
        emission_chart(result)
        with st.expander("How is this calculated?"):
            st.write(f"Grid electricity = max(0, electricity + AC load − solar) = {result['Grid electricity']:.2f} kWh/day.")
            st.write(f"Electricity factor: {ELECTRICITY_FACTOR} kg CO₂/kWh; transport factor: {TRANSPORT_FACTOR} kg CO₂/vehicle-km; waste factor: {WASTE_FACTOR} kg CO₂/kg.")
        st.caption("This is a calculator, not a trained machine-learning prediction model.")

elif page == "Digital Twin":
    intro("SCENARIO LAB","Campus digital twin","Compare your current baseline with a proposed greener scenario.")
    st.subheader("1 · Baseline values")
    a,b,c=st.columns(3)
    with a:
        be=st.number_input("Baseline electricity (kWh/day)",min_value=0.0,value=850.0,step=50.0,key="be")
        bv=st.number_input("Baseline vehicles/day",min_value=0,value=150,step=10,key="bv")
    with b:
        bd=st.number_input("Baseline distance (km/vehicle/day)",min_value=0.0,value=10.0,step=1.0,key="bd")
        bs=st.number_input("Baseline solar (kWh/day)",min_value=0.0,value=200.0,step=20.0,key="bs")
    with c:
        bac=st.number_input("Baseline AC hours/day",min_value=0.0,max_value=24.0,value=8.0,step=1.0,key="bac")
        bw=st.number_input("Baseline waste (kg/day)",min_value=0.0,value=180.0,step=10.0,key="bw")
    st.divider()
    st.subheader("2 · Tune the scenario")
    x,y=st.columns(2)
    with x:
        e=st.slider("Electricity (kWh/day)",0,3000,min(int(be),3000),50)
        v=st.slider("Vehicles/day",0,500,min(int(bv),500),10)
        dist=st.slider("Distance per vehicle (km/day)",0,200,min(int(bd),200),5)
    with y:
        s=st.slider("Solar generation (kWh/day)",0,1000,min(int(bs),1000),20)
        ah=st.slider("AC usage (hours/day)",0,24,min(int(bac),24),1)
        w=st.slider("Waste (kg/day)",0,500,min(int(bw),500),10)
    baseline=calculate_emissions(be,bv,bd,bs,bac,bw)
    scenario=calculate_emissions(e,v,dist,s,ah,w)
    delta=baseline["Total"]-scenario["Total"]
    pct=(delta/baseline["Total"]*100) if baseline["Total"] else 0
    st.divider()
    st.subheader("3 · Results")
    a,b,c=st.columns(3)
    a.metric("Baseline emissions",f"{baseline['Total']:,.1f} kg/day")
    b.metric("Scenario emissions",f"{scenario['Total']:,.1f} kg/day")
    c.metric("Change",f"{abs(delta):,.1f} kg/day",f"{pct:.1f}% reduction" if delta>=0 else f"{abs(pct):.1f}% increase",delta_color="normal")
    comp=pd.DataFrame({"Source":["Electricity","Transportation","Waste"],"Baseline":[baseline["Electricity"],baseline["Transportation"],baseline["Waste"]],"Scenario":[scenario["Electricity"],scenario["Transportation"],scenario["Waste"]]})
    long=comp.melt(id_vars="Source",var_name="Scenario",value_name="Emissions (kg CO₂/day)")
    fig=px.bar(long,x="Source",y="Emissions (kg CO₂/day)",color="Scenario",barmode="group",title="Baseline vs scenario",color_discrete_sequence=["#a9cbb5","#246b45"])
    fig.update_layout(margin=dict(l=15,r=15,t=60,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color="#294235"))
    st.plotly_chart(fig,use_container_width=True)
    if delta>0: st.success(f"This scenario reduces estimated emissions by {delta:,.2f} kg CO₂/day ({pct:.1f}%).")
    elif delta<0: st.warning(f"This scenario increases estimated emissions by {abs(delta):,.2f} kg CO₂/day ({abs(pct):.1f}%).")
    else: st.info("This scenario matches the baseline.")
    with st.expander("Recommendations",expanded=True):
        if e>be: st.write("• Electricity increased: review lighting, equipment, and schedules.")
        if s<bs: st.write("• Solar generation decreased: consider renewable generation options.")
        if v>bv or dist>bd: st.write("• Transport activity increased: encourage carpooling and public transport.")
        if ah>bac: st.write("• AC use increased: review thermostat settings and cooling schedules.")
        if w>bw: st.write("• Waste increased: improve reuse, segregation, and recycling.")
        if e<=be and s>=bs and v<=bv and dist<=bd and ah<=bac and w<=bw: st.write("• Your settings are no worse than the baseline for the measured inputs.")
    if st.button("Save scenario to history",type="primary",use_container_width=True):
        database.save_record(float(e),int(v),float(s),float(ah),float(w),float(scenario["Total"]))
        st.success("Scenario saved. Open Data History to view or export it.")

elif page == "AI Recommendations":
    intro("ACTION CENTER","Sustainability recommendations","Get practical suggestions based on the daily activity values you enter.")
    with st.form("recommendations"):
        a,b=st.columns(2)
        with a:
            electricity=st.number_input("Electricity (kWh/day)",min_value=0.0,value=850.0,step=50.0)
            solar=st.number_input("Solar generation (kWh/day)",min_value=0.0,value=200.0,step=20.0)
            vehicles=st.number_input("Vehicles/day",min_value=0,value=150,step=10)
        with b:
            distance=st.number_input("Distance per vehicle (km/day)",min_value=0.0,value=10.0,step=1.0)
            ac=st.slider("AC usage (hours/day)",0,24,8)
            waste=st.number_input("Waste (kg/day)",min_value=0.0,value=180.0,step=10.0)
        submitted=st.form_submit_button("Generate recommendations",type="primary",use_container_width=True)
    if submitted:
        result=calculate_emissions(electricity,vehicles,distance,solar,ac,waste)
        st.metric("Estimated emissions",f"{result['Total']:,.2f} kg CO₂/day")
        emission_chart(result,"Your emission sources")
        suggestions=[]
        if electricity>0: suggestions.append(("⚡","Improve energy efficiency","Track electricity by building and switch off unused equipment."))
        if solar<electricity: suggestions.append(("☀️","Explore renewable energy","Assess rooftop solar or renewable electricity options."))
        if vehicles>0: suggestions.append(("🚌","Choose low-carbon travel","Encourage carpooling, public transport, cycling, and walking."))
        if ac>=8: suggestions.append(("❄️","Optimize cooling","Review AC schedules, filters, maintenance, and thermostat settings."))
        if waste>0: suggestions.append(("♻️","Reduce campus waste","Separate recyclables and reduce single-use items."))
        st.subheader("Recommended actions")
        for icon,title,desc in suggestions:
            st.markdown(f"**{icon} {title}**  \n{desc}")
            st.divider()
        st.caption("These are rule-based suggestions, not output from a trained AI model.")

elif page == "Data History":
    intro("RECORDS","Simulation history","Search saved scenarios, inspect trends, and export records for your report.")
    records=database.get_all_records()
    if records:
        cols=["ID","Electricity (kWh/day)","Vehicles","Solar (kWh/day)","AC Hours/day","Waste (kg/day)","CO₂ Emissions (kg/day)","Date and Time"]
        history=pd.DataFrame(records,columns=cols)
        query=st.text_input("Search history by date, ID, or value",placeholder="Type to filter records")
        filtered=history
        if query.strip():
            filtered=history[history.astype(str).apply(lambda col: col.str.contains(query,case=False,na=False)).any(axis=1)]
        st.dataframe(filtered,use_container_width=True,hide_index=True)
        st.caption(f"Showing {len(filtered)} of {len(history)} records.")
        if not filtered.empty:
            fig=px.line(filtered.sort_values("ID"),x="Date and Time",y="CO₂ Emissions (kg/day)",markers=True,title="Saved emissions over time",color_discrete_sequence=["#246b45"])
            fig.update_layout(margin=dict(l=15,r=15,t=60,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="DM Sans",color="#294235"))
            st.plotly_chart(fig,use_container_width=True)
        st.download_button("Download visible records as CSV",filtered.to_csv(index=False).encode("utf-8"),"carbonlens_history.csv","text/csv",use_container_width=True)
        with st.expander("Danger zone · delete all history"):
            st.warning("This permanently deletes all saved simulation records.")
            confirm=st.checkbox("I understand all history will be deleted.")
            if st.button("Delete all history",disabled=not confirm):
                database.delete_all_records()
                st.success("History deleted.")
                st.rerun()
    else:
        st.info("No saved records yet. Open Digital Twin, adjust the scenario, and click Save scenario to history.")

st.markdown('<div class="footer">CARBONLENS AI · INTERACTIVE SUSTAINABILITY PROTOTYPE · SAMPLE DATA</div>',unsafe_allow_html=True)
