import streamlit as st
import pandas as pd
import random
import time

# --- 1. INITIALIZATION ---
if 'exp' not in st.session_state:
    pay_schemes = ["Fixed Pay ($10.00)", "Bonus Contract ($5.00 Base + Accuracy Bonus)"]
    receivers = ["Peer Associate (Junior Clerk)", "Accounting Supervisor"]
    st.session_state.exp = {
        "pay": random.choice(pay_schemes),
        "receiver": random.choice(receivers),
        "stage": "intro",
        "start_time": None
    }

# --- 2. INTRO STAGE ---
if st.session_state.exp["stage"] == "intro":
    st.title("Financial Journal Portal")
    st.info(f"**Current Condition:** {st.session_state.exp['pay']} | **Recipient:** {st.session_state.exp['receiver']}")
    
    st.markdown("### Instructions")
    st.write(f"""
    You are entering raw data for the **{st.session_state.exp['receiver']}**. 
    They will use your entries to build the final departmental report. 
    
    **Workflow Context:** The **{st.session_state.exp['receiver']}** will manually review and 
    correct every entry you submit to ensure the final report is accurate.
    """)
    
    if st.button("Begin Task"):
        st.session_state.exp["stage"] = "task"
        st.session_state.exp["start_time"] = time.time()
        st.rerun()

# --- 3. TASK STAGE ---
elif st.session_state.exp["stage"] == "task":
    st.title("Data Entry Ledger")
    st.caption(f"Forwarding to: {st.session_state.exp['receiver']}")

    master_data = [
        {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
        {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
        {"id": "TRX-901", "val": 332.11}, {"id": "TRX-776", "val": 4410.50},
        {"id": "TRX-332", "val": 9921.05}, {"id": "TRX-115", "val": 220.40},
        {"id": "TRX-667", "val": 7550.00}, {"id": "TRX-554", "val": 1022.88}
    ]

    # Form used for stable data entry
    with st.form("ledger_form"):
        st.write("**Please copy the amounts exactly.**")
        
        # We loop to create rows
        for item in master_data:
            c1, c2 = st.columns([1, 1])
            c1.markdown(f"**{item['id']}**: `${item['val']}`")
            # By giving each input a 'key', Streamlit handles the saving automatically
            c2.text_input("Amount", key=f"ans_{item['id']}", label_visibility="collapsed")

        st.markdown("---")
        submit = st.form_submit_button(f"Submit Final Ledger to {st.session_state.exp['receiver']}")

    if submit:
        errors = 0
        for item in master_data:
            # We pull the answer directly from session_state using the key we defined
            user_input = st.session_state.get(f"ans_{item['id']}", "")
            try:
                clean = user_input.replace('$', '').replace(',', '').strip()
                if not clean or float(clean) != item['val']:
                    errors += 1
            except:
                errors += 1
        
        st.session_state.results = {
            "Pay": st.session_state.exp["pay"],
            "Receiver": st.session_state.exp["receiver"],
            "Errors": errors,
            "Seconds": round(time.time() - st.session_state.exp["start_time"], 2)
        }
        st.session_state.exp["stage"] = "done"
        st.rerun()

# --- 4. DONE STAGE ---
elif st.session_state.exp["stage"] == "done":
    st.title("Submission Successful")
    st.success(f"Work forwarded. The **{st.session_state.exp['receiver']}** is now correcting the entries.")
    
    st.write("### Participation Summary")
    df = pd.DataFrame([st.session_state.results])
    st.table(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data Token", data=csv, file_name="results.csv")

    st.divider()
    if st.button("Restart Experiment (Tester Only)"):
        # Reset everything
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
