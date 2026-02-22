import streamlit as st
import pandas as pd
import random
import time

# --- 1. SHARED DATABASE SIMULATION ---
# This 'lab_database' acts as the bridge between Sender and Receiver.
if 'lab_database' not in st.session_state:
    st.session_state.lab_database = []

MASTER_DATA = [
    {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
    {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
    {"id": "TRX-901", "val": 332.11}
]

# --- 2. ROLE SELECTION ---
if 'role' not in st.session_state:
    st.title("Collaborative Accounting Study")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enter as SENDER", use_container_width=True):
            st.session_state.role = "sender"
            st.session_state.pay = random.choice(["Fixed Pay", "Bonus Contract"])
            st.session_state.receiver_type = random.choice(["Peer Associate", "Supervisor"])
            st.session_state.stage = "intro"
            st.rerun()
    with col2:
        if st.button("Enter as RECEIVER", use_container_width=True):
            st.session_state.role = "receiver"
            st.session_state.stage = "queue"
            st.rerun()
    st.stop()

# --- 3. SENDER WORKFLOW ---
if st.session_state.role == "sender":
    if st.session_state.stage == "intro":
        st.title("Sender Portal")
        st.info(f"**Pay:** {st.session_state.pay} | **Recipient:** {st.session_state.receiver_type}")
        if st.button("Start Task"):
            st.session_state.stage = "task"
            st.session_state.start_time = time.time()
            st.rerun()

    elif st.session_state.stage == "task":
        st.title("Data Entry")
        # Fixed: Form now has a mandatory submit button to avoid image_15a579.png error
        with st.form("sender_entry_form"):
            sender_inputs = {}
            for item in MASTER_DATA:
                c1, c2 = st.columns([1, 1])
                c1.write(f"**{item['id']}**: `${item['val']}`")
                sender_inputs[item['id']] = c2.text_input("Amount", key=f"s_in_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button(f"Send to {st.session_state.receiver_type}"):
                submission = {
                    "sender_id": random.randint(1000, 9999),
                    "pay": st.session_state.pay,
                    "receiver_type": st.session_state.receiver_type,
                    "sender_data": sender_inputs,
                    "status": "Pending Review",
                    "corrections": None
                }
                st.session_state.lab_database.append(submission)
                st.session_state.stage = "done"
                st.rerun()

    elif st.session_state.stage == "done":
        st.success("File sent to the queue. Thank you.")
        if st.button("Back to Role Selection"): 
            st.session_state.clear()
            st.rerun()

# --- 4. RECEIVER WORKFLOW ---
elif st.session_state.role == "receiver":
    st.title("Receiver Correction Desk")
    pending = [j for j in st.session_state.lab_database if j['status'] == "Pending Review"]
    
    if not pending:
        st.warning("No files currently in the queue.")
        if st.button("Refresh Queue"): st.rerun()
        if st.button("Back"): st.session_state.clear(); st.rerun()
    else:
        job = pending[0]
        st.info(f"Reviewing File from Sender #{job['sender_id']}")
        
        with st.form("receiver_correction_form"):
            st.write("Correct any errors below:")
            receiver_fixes = {}
            for item in MASTER_DATA:
                s_val = job['sender_data'].get(item['id'], "")
                c1, c2, c3 = st.columns([1, 1, 1])
                c1.write(f"**Master:** `${item['val']}`")
                c2.write(f"**Sender Entered:** `{s_val}`")
                receiver_fixes[item['id']] = c3.text_input("Fix", value=s_val, key=f"r_fix_{item['id']}", label_visibility="collapsed")
            
            if st.form_submit_button("Finalize Report"):
                # Update the database item directly
                job['corrections'] = receiver_fixes
                job['status'] = "Finalized"
                st.session_state.role = "admin_view"
                st.rerun()

# --- 5. ADMIN/RESULTS VIEW ---
elif st.session_state.role == "admin_view":
    st.title("Experiment Final Results")
    # Show the table of interactions
    for entry in st.session_state.lab_database:
        with st.expander(f"Interaction: {entry['sender_id']} → {entry['receiver_type']}"):
            st.write(f"**Pay:** {entry['pay']} | **Status:** {entry['status']}")
            # Build comparison table
            results = []
            for item in MASTER_DATA:
                results.append({
                    "ID": item['id'],
                    "Truth": item['val'],
                    "Sender": entry['sender_data'].get(item['id']),
                    "Receiver Fixed": entry['corrections'].get(item['id']) if entry['corrections'] else "N/A"
                })
            st.table(pd.DataFrame(results))

    if st.button("Restart Study"):
        st.session_state.clear()
        st.rerun()
