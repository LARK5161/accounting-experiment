import streamlit as st
import pandas as pd
import random
import time

# --- 1. EXPERIMENTAL INITIALIZATION ---
if 'experiment_started' not in st.session_state:
    # Defining the 2x2 Matrix
    pay_schemes = ["Fixed Pay ($10.00)", "Bonus Contract ($5.00 Base + Accuracy Bonus)"]
    receivers = ["Peer Associate (Junior Clerk)", "Accounting Supervisor"]
    
    st.session_state.pay_condition = random.choice(pay_schemes)
    st.session_state.receiver_condition = random.choice(receivers)
    st.session_state.experiment_started = True
    st.session_state.start_time = None
    st.session_state.stage = "intro"

# Helper for UI styling
def draw_header():
    st.sidebar.markdown("### System Status")
    st.sidebar.info(f"**Pay Scheme:** \n{st.session_state.pay_condition}")
    st.sidebar.warning(f"**Next in Chain:** \n{st.session_state.receiver_condition}")

# --- 2. STAGE: INTRODUCTION ---
if st.session_state.stage == "intro":
    st.title("Financial Journal Processing Portal")
    draw_header()
    
    st.markdown("### Participant Instructions")
    st.write("You are acting as a Data Entry Clerk for a corporate accounting firm. Your task is to transfer transaction data from the digital logs into the system ledger.")
    
    st.markdown("---")
    st.markdown(f"**Your Compensation:** You will be paid via **{st.session_state.pay_condition}**.")
    st.markdown(f"**Workflow:** Upon submission, your work will be forwarded to the **{st.session_state.receiver_condition}**. They are responsible for reviewing your entries and correcting any errors before final filing.")
    
    if st.button("I understand. Start Task"):
        st.session_state.stage = "task"
        st.session_state.start_time = time.time()
        st.rerun()

# --- 3. STAGE: THE TASK ---
elif st.session_state.stage == "task":
    st.title("Ledger Entry Task")
    draw_header()
    
    st.write(f"Please enter the following 10 transactions accurately. Once finished, click 'Submit to {st.session_state.receiver_condition}'.")
    
    # Realistic Accounting Data
    master_data = [
        {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
        {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
        {"id": "TRX-901", "val": 332.11}, {"id": "TRX-776", "val": 4410.50},
        {"id": "TRX-332", "val": 9921.05}, {"id": "TRX-115", "val": 220.40},
        {"id": "TRX-667", "val": 7550.00}, {"id": "TRX-554", "val": 1022.88}
    ]
    
    user_responses = []
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Source Log**")
        for item in master_data:
            st.code(f"ID: {item['id']} | AMT: ${item['val']}")

    with col2:
        st.markdown("**System Entry**")
        for i in range(len(master_data)):
            res = st.text_input(f"Enter Amt for {master_data[i]['id']}:", key=f"input_{i}")
            user_responses.append(res)

    if st.button(f"Submit Final Log to {st.session_state.receiver_condition}"):
        # Scoring Logic
        errors = 0
        for i, item in enumerate(master_data):
            try:
                if float(user_responses[i].replace('$', '').replace(',', '')) != item['val']:
                    errors += 1
            except:
                errors += 1
        
        # Save results to session
        st.session_state.results = {
            "Pay_Condition": st.session_state.pay_condition,
            "Receiver_Condition": st.session_state.receiver_condition,
            "Errors": errors,
            "Time_Seconds": round(time.time() - st.session_state.start_time, 2),
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.stage = "complete"
        st.rerun()

# --- 4. STAGE: COMPLETION ---
elif st.session_state.stage == "complete":
    st.balloons()
    st.title("Task Submitted")
    st.success(f"Your journal entries have been forwarded to the **{st.session_state.receiver_condition}**.")
    
    st.write("### Data Summary (For Researcher)")
    res_df = pd.DataFrame([st.session_state.results])
    st.table(res_df)
    
    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Participation Data",
        data=csv,
        file_name="lab_results.csv",
        mime="text/csv"
    )
