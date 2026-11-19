"""Feature 3 – classes, subjects, courses and student enrollment (admin only)."""
import pandas as pd
import streamlit as st

import api_client
import components as ui

st.title("🏫 Classes & Courses")


def run(action, success):
    try:
        action()
        st.toast(success)
        st.rerun()
    except api_client.AuthExpired as e:
        api_client.show_error_and_stop(e)
    except api_client.APIError as e:
        st.error(str(e))


classes = ui.load(api_client.get, "/api/classes")["items"]
subjects = ui.load(api_client.get, "/api/subjects")["items"]
courses = ui.load(api_client.get, "/api/courses")["items"]
teachers = ui.load(api_client.get, "/api/users", role="teacher")["items"]

class_names = {c["id"]: c["name"] for c in classes}
subject_names = {s["id"]: f"{s['code']} – {s['name']}" for s in subjects}
teacher_names = {t["id"]: t["name"] for t in teachers}
teacher_options = [None] + list(teacher_names)

tab_classes, tab_subjects, tab_courses, tab_enroll = st.tabs(["Classes", "Subjects", "Courses", "Enrollment"])

# ---------------------------------------------------------------- classes
with tab_classes:
    if classes:
        df = pd.DataFrame(classes)[["name", "academic_year", "description", "student_count", "course_count"]]
        df.columns = ["Class", "Academic year", "Description", "Students", "Courses"]
        st.dataframe(df, width="stretch", hide_index=True)
    with st.form("add_class", clear_on_submit=True):
        st.markdown("**Add a class**")
        name = st.text_input("Class name *", placeholder="e.g. M1-A")
        year = st.text_input("Academic year", placeholder="2026-2027")
        desc = st.text_input("Description")
        if st.form_submit_button("Create class", type="primary"):
            run(lambda: api_client.post("/api/classes", {"name": name, "academic_year": year, "description": desc}),
                "Class created")
    if classes:
        with st.expander("Edit or delete a class"):
            cid = st.selectbox("Class", list(class_names), format_func=class_names.get, key="edit_class")
            current = next(c for c in classes if c["id"] == cid)
            new_name = st.text_input("Name", value=current["name"], key=f"cn_{cid}")
            new_year = st.text_input("Academic year", value=current["academic_year"], key=f"cy_{cid}")
            c1, c2, _ = st.columns([1, 1, 4])
            if c1.button("Save", key="save_class", type="primary"):
                run(lambda: api_client.put(f"/api/classes/{cid}", {"name": new_name, "academic_year": new_year}),
                    "Class updated")
            if c2.button("Delete", key="del_class"):
                run(lambda: api_client.delete(f"/api/classes/{cid}"), "Class deleted")
            st.caption("A class that still has courses cannot be deleted.")

# ---------------------------------------------------------------- subjects
with tab_subjects:
    if subjects:
        st.dataframe(pd.DataFrame(subjects)[["code", "name"]].rename(columns={"code": "Code", "name": "Subject"}),
                     width="stretch", hide_index=True)
    with st.form("add_subject", clear_on_submit=True):
        st.markdown("**Add a subject**")
        code = st.text_input("Code *", placeholder="e.g. PY101")
        name = st.text_input("Name *", placeholder="e.g. Python Programming")
        if st.form_submit_button("Create subject", type="primary"):
            run(lambda: api_client.post("/api/subjects", {"code": code, "name": name}), "Subject created")
    if subjects:
        with st.expander("Delete a subject"):
            sid = st.selectbox("Subject", list(subject_names), format_func=subject_names.get, key="del_subject_id")
            if st.button("Delete subject"):
                run(lambda: api_client.delete(f"/api/subjects/{sid}"), "Subject deleted")

# ---------------------------------------------------------------- courses
with tab_courses:
    st.caption("A course = one subject taught to one class by one teacher. Attendance is recorded per course.")
    if courses:
        df = pd.DataFrame(courses)[["class_name", "subject_name", "teacher_name", "schedule"]]
        df.columns = ["Class", "Subject", "Teacher", "Schedule"]
        st.dataframe(df, width="stretch", hide_index=True)
    if not classes or not subjects:
        st.info("Create at least one class and one subject first.")
    else:
        with st.form("add_course", clear_on_submit=True):
            st.markdown("**Add a course**")
            class_id = st.selectbox("Class", list(class_names), format_func=class_names.get)
            subject_id = st.selectbox("Subject", list(subject_names), format_func=subject_names.get)
            teacher_id = st.selectbox("Teacher", teacher_options,
                                      format_func=lambda x: "— unassigned —" if x is None else teacher_names[x])
            schedule = st.text_input("Schedule", placeholder="Mon & Wed 08:00-10:00")
            if st.form_submit_button("Create course", type="primary"):
                run(lambda: api_client.post("/api/courses", {"class_id": class_id, "subject_id": subject_id,
                                                             "teacher_id": teacher_id, "schedule": schedule}),
                    "Course created")
    if courses:
        with st.expander("Change teacher / schedule, or delete a course"):
            labels = {c["id"]: f"{c['subject_name']} — {c['class_name']}" for c in courses}
            course_id = st.selectbox("Course", list(labels), format_func=labels.get, key="edit_course")
            current = next(c for c in courses if c["id"] == course_id)
            t_index = teacher_options.index(current["teacher_id"]) if current["teacher_id"] in teacher_options else 0
            new_teacher = st.selectbox("Teacher", teacher_options, index=t_index, key=f"ct_{course_id}",
                                       format_func=lambda x: "— unassigned —" if x is None else teacher_names[x])
            new_schedule = st.text_input("Schedule", value=current["schedule"], key=f"cs_{course_id}")
            c1, c2, _ = st.columns([1, 1, 4])
            if c1.button("Save", key="save_course", type="primary"):
                run(lambda: api_client.put(f"/api/courses/{course_id}",
                                           {"teacher_id": new_teacher, "schedule": new_schedule}), "Course updated")
            if c2.button("Delete", key="del_course"):
                run(lambda: api_client.delete(f"/api/courses/{course_id}"), "Course deleted")
            st.caption("A course that already has attendance records cannot be deleted.")

# ---------------------------------------------------------------- enrollment
with tab_enroll:
    st.caption("Students in a class are automatically enrolled in every course of that class.")
    if not classes:
        st.info("Create a class first.")
    else:
        cid = st.selectbox("Class", list(class_names), format_func=class_names.get, key="enroll_class")
        detail = ui.load(api_client.get, f"/api/classes/{cid}")
        members = {s["id"]: f"{s['student_code']} – {s['name']}" for s in detail["students"]}
        everyone = ui.load(api_client.get, "/api/students", limit=1000)["items"]
        others = {s["id"]: f"{s['student_code']} – {s['name']}"
                  + (f"  (now in {s['class_name']})" if s["class_name"] else "  (no class)")
                  for s in everyone if s["id"] not in members}

        left, right = st.columns(2)
        with left:
            st.markdown(f"**Add students to {class_names[cid]}**")
            to_add = st.multiselect("Students", list(others), format_func=others.get, key=f"add_{cid}")
            if st.button("Enrol selected", disabled=not to_add):
                run(lambda: api_client.post(f"/api/classes/{cid}/enroll", {"student_ids": to_add}), "Students enrolled")
        with right:
            st.markdown(f"**Remove students from {class_names[cid]}**  ({len(members)} now)")
            to_remove = st.multiselect("Students", list(members), format_func=members.get, key=f"rm_{cid}")
            if st.button("Remove selected", disabled=not to_remove):
                run(lambda: api_client.post(f"/api/classes/{cid}/unenroll", {"student_ids": to_remove}),
                    "Students removed")
