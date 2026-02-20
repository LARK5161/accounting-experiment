import streamlit as st
import pandas as pd
import random
import time

# --- 1. EXPERIMENTAL INITIALIZATION ---
if 'experiment_started' not in st.session_state:
    pay_schemes = ["Fixed Pay ($10.00)", "Bonus Contract ($5.00 Base + Accuracy Bonus)"]
    receivers = ["Peer Associate (Junior Clerk)", "Accounting Supervisor"]
    
    st.session_state.pay_condition = random.choice(pay_schemes)
    st.session_state.receiver_condition = random.choice(receivers)
    st.session_state.experiment_started = True
    st.session_state.stage = "intro"
    # Create a dictionary to hold user inputs so they don't disappear
    st.session_state.user_answers = {}

def draw_header():
    st.sidebar.markdown("### Workgroup Status")
    st.sidebar.info(f"**Pay Scheme:** \n{st.session_state.pay_condition}")
    st.sidebar.warning(f"**Next in Chain:** \n{st.session_state.receiver_condition}")

# --- 2. STAGE: INTRODUCTION ---
if st.session_state.stage == "intro":
    st.title("Financial Journal Processing Portal")
    draw_header()
    
    st.markdown("### Participant Instructions")
    st.write("""
    You are performing the first stage of a two-part accounting workflow. Your task is to input 
    transaction data into the system ledger.
    """)
    
    st.info(f"""
    **Workflow Interdependence & Correction:**
    The numbers you enter here will be used directly by the **{st.session_state.receiver_condition}** to create the final report. 
    
    Because your entries are the raw data for their work, the **{st.session_state.receiver_condition}** is 
    **required to manually review and correct every single entry** you submit. If you leave 
    errors, they will fix them before the final submission.
    """)
    
    st.markdown(f"**Compensation:** Your payment for this session is: **{st.session_state.pay_condition}**.")
    
    if st.button("I understand. Start Task"):
        st.session_state.stage = "task"
        st.session_state.start_time = time.time()
        st.rerun()

# --- 3. STAGE: THE TASK (New Row-Based Layout) ---
elif st.session_state.stage == "task":
    st.title("Ledger Entry Task")
    draw_header()
    
    st.write(f"Copy the amounts from the left into the entry boxes on the right. The **{st.session_state.receiver_condition}** will review and fix these entries after you submit.")

    # Data to be entered
    master_data = [
        {"id": "TRX-882", "val": 14290.55}, {"id": "TRX-109", "val": 882.10},
        {"id": "TRX-441", "val": 5600.00}, {"id": "TRX-229", "val": 12481.93},
        {"id": "TRX-901", "val": 332.11}, {"id": "TRX-776", "val": 4410.50},
        {"id": "TRX-332", "val": 9921.05}, {"id": "TRX-115", "val": 220.40},
        {"id": "TRX-667", "val": 7550.00}, {"id": "TRX-554", "val": 1022.88}
    ]

    # Use a loop to create rows. This fixes the "alignment" issue.
    for item in master_data:
        cols = st.columns([2, 3]) # Label column and Input column
        with cols[0]:
            st.markdown(f"**{item['id']}**: `${item['val']}`")
        with cols[1]:
            # Save input directly into session state so it's "sticky"
            st.session_state.user_answers[item['id']] = st.text_input(
                f"Enter for {item['id']}", 
                label_visibility="collapsed", 
                key=f"input_{item['id']}"
            )

    st.markdown("---")
    if st.button(f"Submit Final Data to {st.session_state.receiver_condition}"):
        # SCORING LOGIC
        error_count = 0
        for item in master_data:
            user_val = st.session_state.user_answers.get(item['id'], "")
            try:
                # Clean the user input (remove spaces, commas, dollar signs)
                clean_val = user_val.replace('$', '').replace(',', '').strip()
                if float(clean_val) != item['val']:
                    error_count += 1
            except ValueError:
                # If they left it blank or typed letters, it's an error
                error_count += 1
        
        # Log the results
        st.session_state.results = {
            "Condition_Pay": st.session_state.pay_condition,
            "Condition_Receiver": st.session_state.receiver_condition,
            "Total_Errors": error_count,
            "Accuracy_Percent": f"{(10 - error_count) * 10}%",
            "Seconds_Taken": round(time.time() - st.session_state.start_time, 2)
        }
        st.session_state.stage = "complete"
        st.rerun()

# --- 4. STAGE: COMPLETION ---
elif st.session_state.stage == "complete":
    st.title("Submission Received")
    st.success(f"Your ledger has been sent to the **{st.session_state.receiver_condition}** for correction and finalization.")
    
    st.write("### Research Data Summary")
    df = pd.DataFrame([st.session_state.results])
    st.table(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Participation Token", data=csv, file_name="session_results.csv")
