import streamlit as st
import pandas as pd
import random
import time

# --- 1. GLOBAL DATABASE MOCK ---
if 'lab_database' not in st.session_state:
    st.session_state.lab_database = []

MASTER_DATA = [
    {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
    {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
    {"id": "TRX-901", "val": 332.11}
]

# --- 2. ROLE SELECTION ---
if 'role' not in st.session_state:
    st.title("Behavioral Accounting Lab")
    st.subheader("Interactive Workflow Experiment")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enter as SENDER (Data Entry)", use_container_width=True):
            st.session_state.role = "sender"
            st.session_state.pay = random.choice(["Fixed Pay", "Bonus Contract"])
            st.session_state.receiver_type = random.choice(["Peer Associate", "Supervisor"])
            st.session_state.stage = "intro"
            st.rerun()
    with col2:
        if st.button("Enter as RECEIVER (Reviewer)", use_container_width=True):
            st.session_state.role = "receiver"
            st.session_state.stage = "queue"
            st.rerun()
    st.stop()

# --- 3. SENDER WORKFLOW ---
if st.session_state.role == "sender":
    if st.session_state.stage == "intro":
        st.title("Sender Portal")
        st.info(f"**Pay:** {st.session_state.pay} | **Recipient:** {st.session_state.receiver_type}")
        st.write(f"The **{st.session_state.receiver_type}** is waiting for your file. They must manually fix any errors you leave.")
        if st.button("Start Task"):
            st.session_state.stage = "task"
            st.session_state.start_time = time.time()
            st.rerun()

    elif st.session_state.stage == "task":
        st.title("Active Ledger")
        with st.form("sender_form"):
            for item in MASTER_DATA:
                c1, c2 = st.columns([1, 1])
                c1.write(f"**{item['id']}**: `${item['val']}`")
                c2.text_input("Amt", key=f"s_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button(f"Forward to {st.session_state.receiver_type}"):
                # Store Sender's work
                submission = {
                    "sender_id": random.randint(1000, 9999),
                    "pay": st.session_state.pay,
                    "receiver_type": st.session_state.receiver_type,
                    "sender_data": {item['id']: st.session_state.get(f"s_{item['id']}") for item in MASTER_DATA},
                    "status": "Pending Review",
                    "corrections": None
                }
                st.session_state.lab_database.append(submission)
                st.session_state.stage = "done"
                st.rerun()

    elif st.session_state.stage == "done":
        st.success("Work submitted. Please wait for the Receiver to process your file.")
        if st.button("Return to Start"): 
            st.session_state.clear()
            st.rerun()

# --- 4. RECEIVER WORKFLOW ---
elif st.session_state.role == "receiver":
    st.title("Receiver Portal: Correction Desk")
    
    # Find a job that hasn't been finalized yet
    pending_jobs = [j for j in st.session_state.lab_database if j['status'] == "Pending Review"]
    
    if not pending_jobs:
        st.warning("No files currently in the queue.")
        if st.button("Refresh Queue"): st.rerun()
        if st.button("Back"): st.session_state.clear(); st.rerun()
    else:
        job = pending_jobs[0] # Grab the oldest pending job
        st.info(f"Reviewing File: Sender #{job['sender_id']} | Hierarchy: {job['receiver_type']}")
        
        with st.form("receiver_form"):
            st.write("Correct the Sender's entries using the Master Log.")
            for item in MASTER_DATA:
                s_val = job['sender_data'].get(item['id'], "")
                c1, c2, c3 = st.columns([1, 1, 1])
                c1.write(f"**Master:** `${item['val']}`")
                c2.write(f"**Sender:** `{s_val}`")
                # Receiver inputs their correction here
                c3.text_input("Fix", value=s_val, key=f"fix_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button("Finalize & Submit Report"):
                # ACTUALLY SAVE THE CORRECTIONS
                job['corrections'] = {item['id']: st.session_state.get(f"fix_{item['id']}") for item in MASTER_DATA}
                job['status'] = "Finalized"
                st.session_state.role = "admin_view"
                st.rerun()

# --- 5. ADMIN VIEW ---
elif st.session_state.role == "admin_view":
    st.title("Final Experiment Results")
    st.write("This is a summary of the full interaction.")
    
    for entry in st.session_state.lab_database:
        with st.expander(f"Report: Sender {entry['sender_id']} → {entry['receiver_type']}"):
            st.write(f"**Pay Scheme:** {entry['pay']}")
            st.write(f"**Status:** {entry['status']}")
            
            # Show comparison
            comp_data = []
            for item in MASTER_DATA:
                comp_data.append({
                    "ID": item['id'],
                    "Correct Value": item['val'],
                    "Sender Input": entry['sender_data'].get(item['id']),
                    "Receiver Fixed": entry['corrections'].get(item['id']) if entry['corrections'] else "N/A"
                })
            st.table(pd.DataFrame(comp_data))

    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()
