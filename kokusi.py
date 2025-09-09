import streamlit as st
import json

st.write(json.loads(st.secrets["gcp_service_account"]))
