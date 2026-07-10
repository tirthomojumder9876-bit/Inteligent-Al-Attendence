import streamlit as st


def footer_home():
    logo_url = "https://www.google.com/imgres?q=cartoon%20png&imgurl=https%3A%2F%2Fsimilarpng.com%2F_next%2Fimage%3Furl%3Dhttps%253A%252F%252Fimage.similarpng.com%252Ffile%252Fsimilarpng%252Fvery-thumbnail%252F2020%252F07%252FMickey-Mouse-cartoon-on-transparent-PNG.png%26w%3D3840%26q%3D75&imgrefurl=https%3A%2F%2Fsimilarpng.com%2Fcollection%2Fcartoon%2F&docid=S3aUeATn-U8jpM&tbnid=nwW4vPL91_sDvM&vet=12ahUKEwjWmpCFoMiVAxXXZmwGHVL3BPYQnPAOegUI1gEQAA..i&w=600&h=938&hcb=2&ved=2ahUKEwjWmpCFoMiVAxXXZmwGHVL3BPYQnPAOegUI1gEQAA"
    
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:white;"> Created by Tirtho Mojumdar </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)


def footer_dashboard():
    logo_url = "https://www.google.com/imgres?q=cartoon%20png&imgurl=https%3A%2F%2Fsimilarpng.com%2F_next%2Fimage%3Furl%3Dhttps%253A%252F%252Fimage.similarpng.com%252Ffile%252Fsimilarpng%252Fvery-thumbnail%252F2020%252F07%252FMickey-Mouse-cartoon-on-transparent-PNG.png%26w%3D3840%26q%3D75&imgrefurl=https%3A%2F%2Fsimilarpng.com%2Fcollection%2Fcartoon%2F&docid=S3aUeATn-U8jpM&tbnid=nwW4vPL91_sDvM&vet=12ahUKEwjWmpCFoMiVAxXXZmwGHVL3BPYQnPAOegUI1gEQAA..i&w=600&h=938&hcb=2&ved=2ahUKEwjWmpCFoMiVAxXXZmwGHVL3BPYQnPAOegUI1gEQAA"
    
    st.markdown(f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center">
        <p style="font-weight:bold; color:black;"> Created by Tirtho Mojumdar </p>  
        <img src='{logo_url}' style='max-height:25px' />
        </div>
                
                """, unsafe_allow_html=True)