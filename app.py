import streamlit as st
import pandas as pd
import random
import time

# --- 1. GLOBAL CONFIG & DATABASE MOCK ---
# In a real-world lab, this 'db' would be a Google Sheet. 
# For this prototype, we use Streamlit's 'cache' to simulate a shared database.
if 'lab_database' not in st.session_state:
    st.session_state.lab_database = []

# Master Data for the Task
MASTER_DATA = [
    {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
    {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
    {"id": "TRX-901", "val": 332.11}
]

# --- 2. ROLE SELECTION ---
if 'role' not in st.session_state:
    st.title("Behavioral Accounting Lab")
    st.subheader("Welcome to the Interactive Workflow Study")
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
        st.title("Sender Portal: Data Entry")
        st.info(f"**Pay:** {st.session_state.pay} | **Recipient:** {st.session_state.receiver_type}")
        st.write(f"""
        **The Workflow:** You will enter transaction data. Once you submit, your work will appear 
        in the dashboard of a **{st.session_state.receiver_type}**. 
        They must then fix any errors you leave before the final report is generated.
        """)
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
                st.session_state[f"ans_{item['id']}"] = c2.text_input("Amt", key=f"s_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button(f"Forward to {st.session_state.receiver_type}"):
                # Save to 'Database'
                submission = {
                    "sender_id": random.randint(1000, 9999),
                    "pay": st.session_state.pay,
                    "receiver_type": st.session_state.receiver_type,
                    "data": {item['id']: st.session_state.get(f"s_{item['id']}") for item in MASTER_DATA},
                    "timestamp": time.time()
                }
                st.session_state.lab_database.append(submission)
                st.session_state.stage = "done"
                st.rerun()

    elif st.session_state.stage == "done":
        st.success("Work submitted. It is now being reviewed by the receiver.")
        if st.button("Return to Role Selection"):
            del st.session_state.role
            st.rerun()

# --- 4. RECEIVER WORKFLOW ---
elif st.session_state.role == "receiver":
    st.title("Receiver Portal: Correction Desk")
    
    if not st.session_state.lab_database:
        st.warning("No files currently in the queue. Please wait for a Sender to submit work.")
        if st.button("Refresh Queue"): st.rerun()
        if st.button("Back"): del st.session_state.role; st.rerun()
    
    else:
        # Show the most recent submission
        job = st.session_state.lab_database[-1]
        st.info(f"**New Task Assigned:** Reviewing file from Sender #{job['sender_id']}")
        st.write("Below are the Sender's entries. Correct any discrepancies based on the Master Log.")
        
        with st.form("receiver_form"):
            errors_found = 0
            for item in MASTER_DATA:
                sender_val = job['data'].get(item['id'], "")
                c1, c2, c3 = st.columns([1, 1, 1])
                c1.write(f"**Master:** `${item['val']}`")
                c2.write(f"**Sender Entered:** `{sender_val}`")
                # Receiver fixes it here
                st.session_state[f"fix_{item['id']}"] = c3.text_input("Corrected Val", value=sender_val, key=f"r_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button("Finalize & Submit Report"):
                st.success("Report Finalized. Data logged for researcher.")
                # Logic for Researcher
                st.session_state.role = "admin_view"
                st.rerun()

# --- 5. ADMIN VIEW (For you to see results) ---
if st.session_state.get('role') == "admin_view":
    st.title("Experiment Results")
    st.write(st.session_state.lab_database)
    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
