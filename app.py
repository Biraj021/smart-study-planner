import streamlit as st
from datetime import date
import time

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="📘",
    layout="centered"
)

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
defaults = {
    "logged_in": False,
    "username": "",
    "college": "",
    "phone": "",
    "subjects": [],
    "topics": {},
    "notes": {},
    "doubts": [],
    "timer_running": False,
    "start_time": 0.0,
    "elapsed": 0.0
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------
if not st.session_state.logged_in:
    st.title("🔐 Student Login")

    name = st.text_input("👤 Name")
    college = st.text_input("🏫 College / School")
    phone = st.text_input("📱 Phone Number", placeholder="10-digit number")

    if st.button("➡️ Login"):
        if not name or not college or not phone:
            st.warning("Please fill all details")
        elif not phone.isdigit() or len(phone) != 10:
            st.error("Enter a valid 10-digit phone number")
        else:
            st.session_state.logged_in = True
            st.session_state.username = name
            st.session_state.college = college
            st.session_state.phone = phone
            st.rerun()

    st.stop()

# -------------------------------------------------
# DASHBOARD HEADER
# -------------------------------------------------
st.title("📚 Smart Study Planner")
st.write(f"👋 Welcome **{st.session_state.username}**")
st.write(f"🏫 {st.session_state.college} | 📱 {st.session_state.phone}")

st.divider()

# -------------------------------------------------
# EXAM PLANNING
# -------------------------------------------------
st.header("📅 Exam Planning")
exam_date = st.date_input("Exam Date", min_value=date.today())
daily_hours = st.slider("Daily Study Hours", 1, 12, 6)

st.divider()

# -------------------------------------------------
# SUBJECT MANAGER
# -------------------------------------------------
st.header("📘 Subject Manager")

new_subject = st.text_input("Add a subject")

if st.button("➕ Add Subject"):
    if new_subject.strip() == "":
        st.warning("Subject name cannot be empty")
    elif new_subject in st.session_state.subjects:
        st.warning("Subject already exists")
    else:
        st.session_state.subjects.append(new_subject)
        st.session_state.topics[new_subject] = {}
        st.session_state.notes[new_subject] = ""
        st.success("Subject added")

if st.session_state.subjects:
    for s in st.session_state.subjects:
        st.write("•", s)
else:
    st.info("No subjects added yet")

st.divider()

# -------------------------------------------------
# TOPICS, NOTES & PROGRESS (PER SUBJECT)
# -------------------------------------------------
st.header("📖 Topics, Notes & Progress")

for subject in st.session_state.subjects:
    st.subheader(f"📘 {subject}")

    # Notes
    st.session_state.notes[subject] = st.text_area(
        "📝 Notes",
        value=st.session_state.notes.get(subject, ""),
        key=f"note_{subject}"
    )

    # Add topic
    topic = st.text_input(
        f"Add topic for {subject}",
        key=f"topic_{subject}"
    )

    if st.button(f"Add Topic ({subject})", key=f"btn_{subject}"):
        if topic.strip() == "":
            st.warning("Topic name cannot be empty")
        elif topic in st.session_state.topics[subject]:
            st.warning("Topic already exists")
        else:
            st.session_state.topics[subject][topic] = False
            st.success("Topic added")

    completed = 0
    total = len(st.session_state.topics[subject])

    for t in st.session_state.topics[subject]:
        checked = st.checkbox(
            t,
            value=st.session_state.topics[subject][t],
            key=f"{subject}_{t}"
        )
        st.session_state.topics[subject][t] = checked
        if checked:
            completed += 1

    if total > 0:
        percent = int((completed / total) * 100)
        st.progress(percent)
        st.write(f"Progress: {completed}/{total} ({percent}%)")
    else:
        st.info("No topics added yet")

    st.divider()

# -------------------------------------------------
# OVERALL PROGRESS
# -------------------------------------------------
st.header("📊 Overall Progress")

overall_completed = 0
overall_total = 0

for subject in st.session_state.subjects:
    overall_total += len(st.session_state.topics[subject])
    overall_completed += sum(
        1 for v in st.session_state.topics[subject].values() if v
    )

if overall_total > 0:
    overall_percent = int((overall_completed / overall_total) * 100)
    st.progress(overall_percent)
    st.success(
        f"Total Progress: {overall_completed}/{overall_total} topics ({overall_percent}%)"
    )
else:
    st.info("Add topics to see progress")

st.divider()

# -------------------------------------------------
# STUDY TIMER
# -------------------------------------------------
st.header("⏲ Study Timer")

c1, c2 = st.columns(2)

with c1:
    if st.button("▶ Start"):
        st.session_state.start_time = time.time()
        st.session_state.timer_running = True

with c2:
    if st.button("⏹ Stop"):
        if st.session_state.timer_running:
            st.session_state.elapsed += time.time() - st.session_state.start_time
            st.session_state.timer_running = False

elapsed = st.session_state.elapsed
if st.session_state.timer_running:
    elapsed += time.time() - st.session_state.start_time

st.success(f"⏳ Total Study Time: {int(elapsed // 60)} minutes")

st.divider()

# -------------------------------------------------
# WEEKLY STUDY SUMMARY
# -------------------------------------------------
st.header("📈 Weekly Study Summary")

pending = overall_total - overall_completed
study_minutes = int(elapsed // 60)

col1, col2 = st.columns(2)

with col1:
    st.metric("📘 Subjects", len(st.session_state.subjects))
    st.metric("📖 Topics", overall_total)
    st.metric("✅ Completed", overall_completed)

with col2:
    st.metric("⏳ Pending", pending)
    st.metric("⏱ Study Time (min)", study_minutes)

st.divider()

# -------------------------------------------------
# SMART STUDY SUGGESTIONS
# -------------------------------------------------
st.header("🧠 Smart Suggestions")

if daily_hours >= 10:
    st.warning("⚠️ Too many study hours. Take breaks to avoid burnout.")

if overall_total > 0:
    percent = (overall_completed / overall_total) * 100

    if percent < 40:
        st.info("📉 Low progress. Start with easy topics.")
    elif percent < 75:
        st.success("👍 Good progress. Stay consistent.")
    else:
        st.balloons()
        st.success("🎉 Excellent! You are exam ready.")

st.divider()

# -------------------------------------------------
# DOUBT NOTEBOOK WITH RESOURCES
# -------------------------------------------------
st.header("❓ Doubt Notebook")

doubt = st.text_area("Write your doubt")

if st.button("📌 Save Doubt"):
    if doubt.strip():
        st.session_state.doubts.append(doubt)
        st.success("Doubt saved")
    else:
        st.warning("Doubt cannot be empty")

if st.session_state.doubts:
    st.subheader("📒 Saved Doubts")

    for i, d in enumerate(st.session_state.doubts, 1):
        st.write(f"**{i}.** {d}")

        q = d.replace(" ", "+")
        st.markdown(
            f"""
            🔍 [Google](https://www.google.com/search?q={q}) |
            ▶️ [YouTube](https://www.youtube.com/results?search_query={q}) |
            📘 [GeeksForGeeks](https://www.geeksforgeeks.org/?s={q})
            """
        )

st.divider()
