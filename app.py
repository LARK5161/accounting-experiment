import streamlit as st
import pandas as pd
import random
import time

# --- EXPERIMENTAL CONFIG ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'condition' not in st.session_state:
    # 2x2 Randomization
    pay = random.choice(["Fixed ($10.00)", "Bonus (Up to $15.00)"])
    receiver = random.choice(["Peer Associate", "Supervisor"])
    st.session_state.condition = {"Pay": pay, "Receiver": receiver}

cond = st.session_state.condition

# --- UI SETUP ---
st.set_page_config(page_title="Financial Journal Entry Task", layout="centered")

# --- STAGE 1: INSTRUCTIONS ---
if 'stage' not in st.session_state:
    st.session_state.stage = "intro"

if st.session_state.stage == "intro":
    st.title("Accounting Journal Processing Task")
    st.write("### Instructions")
    st.write(f"""
    In this simulation, you are responsible for entering journal data into the company ledger. 
    
    **Workflow Details:**
    * **Your Pay:** {cond['Pay']} for this session.
    * **Submission:** Once you submit your entries, your file will be sent directly to a **{cond['Receiver']}**.
    * **Finalization:** The **{cond['Receiver']}** is responsible for reviewing your data, correcting any errors, and submitting the final report.
    """)
    
    if st.button("Start Task"):
        st.session_state.stage = "task"
        st.rerun()

# --- STAGE 2: THE TASK ---
elif st.session_state.stage == "task":
    st.subheader("Data Entry Portal")
    st.info(f"Recipient of this file: {cond['Receiver']}")
    
    # Sample Task Data
    tasks = [
        {"ref": "REC-9921", "val": 10482.93},
        {"ref": "REC-4402", "val": 128.40},
        {"ref": "REC-1109", "val": 5590.01},
        {"ref": "REC-8832", "val": 932.11},
        {"ref": "REC-7761", "val": 4410.50}
    ]
    
    responses = []
    for i, t in enumerate(tasks):
        val = st.text_input(f"Enter amount for Reference {t['ref']}:", key=f"input_{i}")
        responses.append(val)

    if st.button("Submit to " + cond['Receiver']):
        # Logic to calculate errors
        errors = 0
        for i, t in enumerate(tasks):
            try:
                if float(responses[i]) != t['val']:
                    errors += 1
            except:
                errors += 1
        
        st.session_state.results = {
            "Time_Taken": round(time.time() - st.session_state.start_time, 2),
            "Errors": errors,
            "Condition_Pay": cond['Pay'],
            "Condition_Receiver": cond['Receiver']
        }
        st.session_state.stage = "finish"
        st.rerun()

# --- STAGE 3: FINISH & DATA DOWNLOAD ---
elif st.session_state.stage == "finish":
    st.success("Task Complete. Your file has been sent.")
    st.write("Please click the button below to download your participation token and data.")
    
    # Create a simple CSV for the researcher
    df = pd.DataFrame([st.session_state.results])
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="Download Research Token",
        data=csv,
        file_name='experiment_data.csv',
        mime='text/csv',
    )