import streamlit as st
from supabase import Client, create_client


try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    SUPABASE_URL = "https://kegzgefdglrfgyuailkr.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtlZ3pnZWZkZ2xyZmd5dWFpbGtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY5NTA3MjcsImV4cCI6MjEwMjUyNjcyN30.bWyH6pDo4iPOWgo1FXY7sLASUztYLKSpI4hsNAlW1-g"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)