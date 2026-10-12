import os
import requests
import streamlit as st

st.set_page_config(page_title="IoT Maintenance Command Center",layout="wide")
st.title("Predictive Maintenance · IoT Sensor Monitoring")
st.caption("Research simulation — scores are not safety-certified maintenance decisions")
api=os.getenv("API_URL","http://localhost:8000")
try:
    health=requests.get(api+"/health",timeout=3).json()
    st.info(f"API: {health['status']} | Model ready: {health['model_available']}")
except (requests.RequestException,ValueError,KeyError):
    st.warning("Start FastAPI to enable scoring")
left,right=st.columns(2)
temperature=left.slider("Temperature",20,140,80)
vibration=right.slider("Vibration",0.0,12.0,2.0)
pressure=left.slider("Pressure",0.0,12.0,5.0)
rpm=right.slider("RPM",0,3500,1500)
hours=st.slider("Operating hours",0,12000,2000)
if st.button("Estimate failure risk"):
    payload={"temperature":temperature,"vibration":vibration,"pressure":pressure,"rpm":rpm,"operating_hours":hours}
    try:
        r=requests.post(api+"/predict",json=payload,timeout=10)
        if r.ok:
            value=r.json();st.metric("Estimated failure probability",f"{value['failure_probability']:.1%}")
            st.warning("Review recommended") if value["alert"] else st.success("Below demo threshold")
        else:st.error(f"API returned {r.status_code}: {r.text}")
    except requests.RequestException as e:st.error(str(e))
