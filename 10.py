"""
CA Talent Connect — Recruitment platform connecting CA firms with CA professionals.
Run:  pip install streamlit pandas
      streamlit run CA_Talent_Connect.py

NOTE ON AUTH: This demo uses a simple in-memory username/password store held in
st.session_state. It resets whenever the app restarts and is NOT secure (this is a
prototype, not production auth). For real deployment, use a database + password
hashing (e.g. bcrypt) and a proper auth/session provider.
"""

import re
import hashlib
from datetime import date, datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="CA Talent Connect | Professional Recruitment", page_icon="💼", layout="wide", initial_sidebar_state="expanded")

# ----------------------------------------------------------------------
# STYLES — Apna-style: bold blue header, orange CTA accents, chip tags,
# avatar-initial cards, rounded pill buttons.
# ----------------------------------------------------------------------
st.markdown("""<style>
:root{
  --navy:#0B1F3A; --blue:#1D4ED8; --blue2:#2563EB; --blue-soft:#EFF6FF;
  --ink:#172033; --muted:#64748B; --line:#E2E8F0; --surface:#FFFFFF;
  --bg:#F6F8FC; --success:#15803D; --success-bg:#F0FDF4; --warning:#B45309; --warning-bg:#FFFBEB;
  --shadow:0 8px 28px rgba(15,23,42,.07); --radius:16px;
}
html,body,[class*="css"]{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;}
.stApp{background:var(--bg);color:var(--ink);}
.block-container{max-width:1280px;padding-top:1.5rem;padding-bottom:3rem;}
header[data-testid="stHeader"]{background:rgba(246,248,252,.85);}
section[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line);}
section[data-testid="stSidebar"] > div{padding-top:1.2rem;}
/* Brand header */
.topnav{background:linear-gradient(135deg,#0B1F3A 0%,#123A73 55%,#1D4ED8 100%);border:1px solid rgba(255,255,255,.08);border-radius:18px;padding:20px 26px;margin:0 0 24px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 12px 32px rgba(11,31,58,.18);position:relative;overflow:hidden;}
.topnav:after{content:"";position:absolute;width:300px;height:300px;right:-110px;top:-150px;border-radius:50%;background:rgba(255,255,255,.08);}
.topnav > div{position:relative;z-index:1;}
.topnav h1{color:#fff!important;font-size:24px;line-height:1.2;margin:0;font-weight:800;letter-spacing:-.4px;}
.topnav p{color:#D9E7FA;font-size:13px;margin:5px 0 0;}
/* Section headings */
h1,h2,h3,h4{color:var(--ink);letter-spacing:-.25px;}
[data-testid="stMarkdownContainer"] h4{margin-bottom:.35rem;}
/* Cards */
.job-card,.candidate-card{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:var(--radius);padding:20px 22px;margin:0 0 14px;box-shadow:var(--shadow);transition:transform .15s ease,box-shadow .15s ease;}
.job-card:hover,.candidate-card:hover{transform:translateY(-1px);box-shadow:0 12px 34px rgba(15,23,42,.10);}
.candidate-card{border-left-color:#7C3AED;}
.job-top{display:flex;gap:14px;align-items:flex-start;}
.avatar-circle{min-width:48px;height:48px;border-radius:14px;background:var(--blue-soft);color:#1D4ED8;font-weight:800;font-size:15px;display:flex;align-items:center;justify-content:center;flex-shrink:0;border:1px solid #DBEAFE;}
.avatar-circle.purple{background:#F5F3FF;color:#7C3AED;border-color:#EDE9FE;}
.job-card h4,.candidate-card h4{color:var(--ink);margin:0 0 4px;font-size:17px;font-weight:750;}
.job-firm{color:#334155;font-size:13.5px;font-weight:650;margin-bottom:3px;}
.job-meta{color:var(--muted);font-size:12.5px;margin-bottom:10px;}
.badge-hiring{display:inline-block;background:var(--success-bg);color:var(--success);border:1px solid #BBF7D0;border-radius:999px;font-size:10.5px;font-weight:750;padding:3px 9px;margin-left:6px;vertical-align:2px;}
.tag{display:inline-block;background:#F1F5F9;color:#334155;border:1px solid #E2E8F0;border-radius:999px;padding:4px 10px;font-size:11.5px;font-weight:650;margin-right:5px;margin-bottom:4px;}
.tag-salary{background:#FFF7ED;color:#C2410C;border-color:#FED7AA;}.tag-exp{background:#EFF6FF;color:#1D4ED8;border-color:#DBEAFE;}.tag-city{background:#F0FDFA;color:#0F766E;border-color:#CCFBF1;}.tag-area{background:#F5F3FF;color:#6D28D9;border-color:#EDE9FE;}
/* Buttons */
div.stButton>button,div.stFormSubmitButton>button{border-radius:10px;border:1px solid #1D4ED8;background:#1D4ED8;color:#fff;min-height:42px;font-weight:700;box-shadow:0 4px 12px rgba(29,78,216,.16);transition:.15s ease;}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{background:#1E40AF;border-color:#1E40AF;transform:translateY(-1px);}
button[kind="secondary"]{background:#fff!important;color:#1D4ED8!important;border:1px solid #CBD5E1!important;box-shadow:none!important;}
/* Inputs */
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{border-radius:10px!important;border-color:#CBD5E1!important;background:#fff!important;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:#2563EB!important;box-shadow:0 0 0 2px rgba(37,99,235,.12)!important;}
label{font-weight:650!important;color:#334155!important;font-size:13px!important;}
/* Tabs */
.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{height:44px;padding:0 16px;font-weight:700;color:#64748B;}
.stTabs [aria-selected="true"]{color:#1D4ED8!important;}
.stTabs [data-baseweb="tab-highlight"]{background:#1D4ED8;height:3px;border-radius:3px;}
/* Metrics */
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow);}
div[data-testid="stMetricLabel"]{color:#64748B;font-weight:650;}
div[data-testid="stMetricValue"]{color:#0F172A;font-weight:800;}
/* Alerts / expanders / tables */
div[data-testid="stAlert"]{border-radius:12px;border:1px solid var(--line);}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:12px;background:#fff;overflow:hidden;}
.stDataFrame{border:1px solid var(--line);border-radius:12px;overflow:hidden;}
/* File uploader */
section[data-testid="stFileUploaderDropzone"]{border:1px dashed #94A3B8;border-radius:12px;background:#F8FAFC;}
/* Popover */
button[data-testid="stPopoverButton"]{border-radius:10px;border:1px solid #CBD5E1;background:#fff;font-weight:700;}
/* Hide Streamlit chrome */
#MainMenu{visibility:hidden;}footer{visibility:hidden;}
@media(max-width:800px){.block-container{padding:1rem .8rem 2rem}.topnav{padding:18px}.topnav h1{font-size:20px}.job-card,.candidate-card{padding:16px}.stTabs [data-baseweb="tab"]{padding:0 9px;font-size:12px;}}
</style>""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SESSION STATE (in-memory data store)
# ----------------------------------------------------------------------
if "jobs" not in st.session_state:
    st.session_state.jobs = [
        dict(id=1, title="Audit Manager", firm="Sharma & Associates", location="Mumbai",
             role="Audit & Assurance", exp="3-5 years", ctc="12-16 LPA",
             qual="CA", posted=date(2026, 9, 2), posted_by="demo@platform.local",
             desc="Lead statutory and internal audit engagements for listed clients; "
                  "review working papers and mentor article assistants."),
        dict(id=2, title="Direct Tax Associate", firm="Mehta Consultants LLP", location="Pune",
             role="Direct Taxation", exp="0-2 years", ctc="7-9 LPA",
             qual="CA", posted=date(2026, 9, 8), posted_by="demo@platform.local",
             desc="Handle ITR filings, tax audits under 44AB, TDS compliance and "
                  "assessment proceedings for corporate clients."),
        dict(id=3, title="Article Assistant", firm="Nashik Accounting Services", location="Nashik",
             role="Articleship", exp="Fresher", ctc="Stipend as per ICAI",
             qual="CA Inter", posted=date(2026, 9, 12), posted_by="demo@platform.local",
             desc="Exposure across audit, GST and income tax compliance with "
                  "direct partner mentorship."),
    ]

if "applications" not in st.session_state:
    st.session_state.applications = []          # each: job_id, title, firm, posted_by, name, email, note, applied
if "candidate_profiles" not in st.session_state:
    st.session_state.candidate_profiles = {}     # email -> profile dict (one profile per candidate account)

if "employer_accounts" not in st.session_state:
    st.session_state.employer_accounts = {}      # email -> {password_hash, firm_name}
if "employee_accounts" not in st.session_state:
    st.session_state.employee_accounts = {}      # email -> {password_hash, full_name}
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "role": None, "email": None, "display_name": None}

ROLES = ["Audit & Assurance", "Direct Taxation", "Indirect Taxation (GST)",
         "Accounting & Compliance", "Finance / FP&A", "Articleship"]
QUALS = ["CA", "CA Inter", "CA Final (Pursuing)", "CMA", "B.Com / M.Com"]
EXP = ["Fresher", "0-2 years", "3-5 years", "6-10 years", "10+ years"]

def valid_email(e):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", e))

def valid_phone(p):
    return bool(re.fullmatch(r"[6-9]\d{9}", p))

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", name.strip()) if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def do_logout():
    st.session_state.auth = {"logged_in": False, "role": None, "email": None, "display_name": None}

# ----------------------------------------------------------------------
# LOGIN / SIGN UP GATE — must authenticate before anything else loads
# ----------------------------------------------------------------------
def render_login_gate():
    st.markdown("""<div class="topnav">
    <div>
    <h1>📇 CA Talent Connect</h1>
    <p>Recruitment platform connecting Chartered Accountancy firms with qualified professionals</p>
    </div>
    <svg width="120" height="80" viewBox="0 0 120 80" style="position:relative;z-index:1">
      <circle cx="90" cy="22" r="16" fill="#FFC98A" opacity="0.9"/>
      <rect x="18" y="30" width="54" height="38" rx="6" fill="#FFFFFF" opacity="0.95"/>
      <rect x="18" y="30" width="54" height="10" rx="6" fill="#FF7A1A"/>
      <rect x="30" y="18" width="30" height="14" rx="3" fill="#FFFFFF" opacity="0.95"/>
      <line x1="38" y1="18" x2="38" y2="12" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
      <line x1="52" y1="18" x2="52" y2="12" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
      <circle cx="30" cy="55" r="4" fill="#7B4FE0"/>
      <circle cx="45" cy="55" r="4" fill="#0FA3A3"/>
      <circle cx="60" cy="55" r="4" fill="#12357A"/>
    </svg>
    </div>""", unsafe_allow_html=True)

    st.info("Please log in or sign up to continue. Both employers and candidates need "
            "an account to access the platform.")

    role_tab = st.radio("I am a", ["Employer (Firm)", "Candidate"], horizontal=True)
    account_store = (st.session_state.employer_accounts if role_tab == "Employer (Firm)"
                      else st.session_state.employee_accounts)
    role_key = "employer" if role_tab == "Employer (Firm)" else "employee"

    login_tab, signup_tab = st.tabs(["🔐 Log In", "📝 Sign Up"])

    with login_tab:
        with st.form(f"login_form_{role_key}"):
            email = st.text_input("Email", key=f"login_email_{role_key}")
            pw = st.text_input("Password", type="password", key=f"login_pw_{role_key}")
            submitted = st.form_submit_button("Log In")
            if submitted:
                email_clean = email.strip().lower()
                acct = account_store.get(email_clean)
                if not acct or acct["password_hash"] != hash_pw(pw):
                    st.error("Invalid email or password.")
                else:
                    st.session_state.auth = {
                        "logged_in": True,
                        "role": role_key,
                        "email": email_clean,
                        "display_name": acct.get("firm_name") or acct.get("full_name"),
                    }
                    st.rerun()

    with signup_tab:
        with st.form(f"signup_form_{role_key}"):
            name_label = "Firm / Company Name *" if role_key == "employer" else "Full Name *"
            display_name = st.text_input(name_label, key=f"su_name_{role_key}")
            su_email = st.text_input("Email *", key=f"su_email_{role_key}")
            su_pw = st.text_input("Password *", type="password", key=f"su_pw_{role_key}")
            su_pw2 = st.text_input("Confirm Password *", type="password", key=f"su_pw2_{role_key}")
            submitted = st.form_submit_button("Create Account")
            if submitted:
                errors = []
                email_clean = su_email.strip().lower()
                if not display_name.strip():
                    errors.append("Name is required.")
                if not valid_email(email_clean):
                    errors.append("A valid email address is required.")
                if email_clean in account_store:
                    errors.append("An account with this email already exists. Please log in instead.")
                if len(su_pw) < 6:
                    errors.append("Password must be at least 6 characters.")
                if su_pw != su_pw2:
                    errors.append("Passwords do not match.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    record = {"password_hash": hash_pw(su_pw)}
                    if role_key == "employer":
                        record["firm_name"] = display_name.strip()
                        record["contact_person"] = ""
                        record["contact_phone"] = ""
                        record["address"] = ""
                        record["city"] = ""
                        record["pincode"] = ""
                        record["profile_complete"] = False
                    else:
                        record["full_name"] = display_name.strip()
                    account_store[email_clean] = record
                    st.success("Account created! Please log in using the 'Log In' tab.")

# ----------------------------------------------------------------------
# HEADER with top-right profile popover (replaces the old header)
# ----------------------------------------------------------------------
def render_header():
    auth = st.session_state.auth
    role_label = "Employer" if auth["role"] == "employer" else "Candidate"

    left, right = st.columns([5, 1.1])
    with left:
        st.markdown(f"""<div class="topnav">
        <div>
        <h1>📇 CA Talent Connect</h1>
        <p>Recruitment platform connecting Chartered Accountancy firms with qualified professionals</p>
        </div></div>""", unsafe_allow_html=True)
    with right:
        st.write("")
        popover_label = f"👤 {initials(auth['display_name'])}"
        with st.popover(popover_label, use_container_width=True):
            st.markdown(f"**{auth['display_name']}**")
            st.caption(f"{role_label} · {auth['email']}")
            st.divider()
            if auth["role"] == "employee":
                render_candidate_profile_form()
            else:
                render_employer_profile_form()
            st.divider()
            if st.button("Log Out", key="logout_btn", use_container_width=True):
                do_logout()
                st.rerun()

def render_candidate_profile_form():
    auth = st.session_state.auth
    existing = st.session_state.candidate_profiles.get(auth["email"], {})
    st.markdown("**Edit Profile**")
    with st.form("candidate_profile_form"):
        phone = st.text_input("Mobile Number *", value=existing.get("phone", ""),
                               max_chars=10, placeholder="10-digit number")
        city = st.text_input("Preferred Location *", value=existing.get("city", ""))
        qual = st.selectbox("Qualification *", QUALS,
                             index=QUALS.index(existing["qual"]) if existing.get("qual") in QUALS else 0)
        exp = st.selectbox("Experience *", EXP,
                            index=EXP.index(existing["exp"]) if existing.get("exp") in EXP else 0)
        membership = st.text_input("ICAI Membership No. (optional)", value=existing.get("membership", ""))
        areas = st.multiselect("Areas of Interest *", ROLES, default=existing.get("areas_list", []))
        resume = st.file_uploader("Upload Résumé (PDF)", type=["pdf"])
        consent = st.checkbox("I consent to share my details with hiring firms.",
                               value=existing.get("consent", False))

        if st.form_submit_button("Save Profile", use_container_width=True):
            errors = []
            if not valid_phone(phone):
                errors.append("Mobile number must be 10 digits starting with 6-9.")
            if not city.strip():
                errors.append("Preferred location is required.")
            if not areas:
                errors.append("Select at least one area of interest.")
            if not consent:
                errors.append("Consent is required to save your profile.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                profile = {
                    "name": auth["display_name"],
                    "email": auth["email"],
                    "phone": phone.strip(),
                    "city": city.strip(),
                    "qual": qual,
                    "exp": exp,
                    "membership": membership.strip() or "—",
                    "areas_list": areas,
                    "areas": ", ".join(areas),
                    "consent": True,
                    "updated": datetime.now(),
                }
                # keep previously uploaded resume if no new one was provided
                if resume is not None:
                    profile["resume_name"] = resume.name
                    profile["resume_bytes"] = resume.getvalue()
                else:
                    profile["resume_name"] = existing.get("resume_name", "Not uploaded")
                    profile["resume_bytes"] = existing.get("resume_bytes")

                st.session_state.candidate_profiles[auth["email"]] = profile
                st.success("Profile saved.")

    existing_resume = st.session_state.candidate_profiles.get(auth["email"], {}).get("resume_name")
    if existing_resume and existing_resume != "Not uploaded":
        st.caption(f"📄 Current résumé on file: {existing_resume}")

EMPLOYER_REQUIRED_FIELDS = ["contact_person", "contact_phone", "address", "city", "pincode"]

def employer_profile_is_complete(acct: dict) -> bool:
    return all(acct.get(f, "").strip() for f in EMPLOYER_REQUIRED_FIELDS)

def _employer_details_fields(acct: dict, key_prefix: str):
    """Shared form fields for employer firm/contact details. Returns the entered values."""
    f1, f2 = st.columns(2)
    firm_name = f1.text_input("Firm / Company Name *", value=acct.get("firm_name", ""),
                               key=f"{key_prefix}_firm")
    contact_person = f2.text_input("Contact Person Name *", value=acct.get("contact_person", ""),
                                    key=f"{key_prefix}_person")
    f3, f4 = st.columns(2)
    contact_phone = f3.text_input("Contact Phone Number *", value=acct.get("contact_phone", ""),
                                   max_chars=10, placeholder="10-digit number", key=f"{key_prefix}_phone")
    pincode = f4.text_input("Pincode *", value=acct.get("pincode", ""), max_chars=6,
                             key=f"{key_prefix}_pincode")
    city = st.text_input("City *", value=acct.get("city", ""), key=f"{key_prefix}_city")
    address = st.text_area("Office Address *", value=acct.get("address", ""), height=80,
                            key=f"{key_prefix}_address")
    return dict(firm_name=firm_name, contact_person=contact_person, contact_phone=contact_phone,
                pincode=pincode, city=city, address=address)

def render_employer_profile_form():
    auth = st.session_state.auth
    acct = st.session_state.employer_accounts[auth["email"]]
    st.markdown("**Firm & Contact Details**")
    with st.form("employer_profile_form"):
        vals = _employer_details_fields(acct, "ep")
        if st.form_submit_button("Save", use_container_width=True):
            errors = []
            if not vals["firm_name"].strip():
                errors.append("Firm / company name is required.")
            if not vals["contact_person"].strip():
                errors.append("Contact person name is required.")
            if not valid_phone(vals["contact_phone"]):
                errors.append("Contact phone must be 10 digits starting with 6-9.")
            if not re.fullmatch(r"\d{6}", vals["pincode"].strip()):
                errors.append("Pincode must be 6 digits.")
            if not vals["city"].strip():
                errors.append("City is required.")
            if not vals["address"].strip():
                errors.append("Office address is required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                acct.update({k: v.strip() for k, v in vals.items()})
                acct["profile_complete"] = employer_profile_is_complete(acct)
                st.session_state.auth["display_name"] = acct["firm_name"]
                st.success("Details updated.")
                st.rerun()

def render_employer_onboarding():
    """Mandatory gate shown right after an employer logs in until their profile is complete."""
    auth = st.session_state.auth
    st.markdown("""<div class="topnav">
    <div>
    <h1>📇 CA Talent Connect</h1>
    <p>Recruitment platform connecting Chartered Accountancy firms with qualified professionals</p>
    </div></div>""", unsafe_allow_html=True)

    st.warning("Please complete your firm's profile to continue. This information helps candidates "
               "and keeps your account verified.")
    acct = st.session_state.employer_accounts[auth["email"]]
    with st.form("employer_onboarding_form"):
        vals = _employer_details_fields(acct, "onb")
        submitted = st.form_submit_button("Save & Continue", use_container_width=True)
        if submitted:
            errors = []
            if not vals["firm_name"].strip():
                errors.append("Firm / company name is required.")
            if not vals["contact_person"].strip():
                errors.append("Contact person name is required.")
            if not valid_phone(vals["contact_phone"]):
                errors.append("Contact phone must be 10 digits starting with 6-9.")
            if not re.fullmatch(r"\d{6}", vals["pincode"].strip()):
                errors.append("Pincode must be 6 digits.")
            if not vals["city"].strip():
                errors.append("City is required.")
            if not vals["address"].strip():
                errors.append("Office address is required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                acct.update({k: v.strip() for k, v in vals.items()})
                acct["profile_complete"] = True
                st.session_state.auth["display_name"] = acct["firm_name"]
                st.success("Profile complete!")
                st.rerun()

    if st.button("Log Out"):
        do_logout()
        st.rerun()

# ----------------------------------------------------------------------
# CANDIDATE VIEW
# ----------------------------------------------------------------------
def render_candidate_app():
    auth = st.session_state.auth
    tab_jobs, tab_dash = st.tabs(["🔍 Browse Openings", "📊 My Dashboard"])

    with tab_jobs:
        st.markdown("### Find your next opportunity")
        st.caption("Search verified-style recruitment listings across audit, taxation, GST, accounting and articleship roles.")
        c1, c2, c3 = st.columns(3)
        f_role = c1.selectbox("Practice Area", ["All"] + ROLES)
        f_loc = c2.text_input("Location contains", "")
        f_exp = c3.selectbox("Experience", ["All"] + EXP)

        jobs = st.session_state.jobs
        if f_role != "All":
            jobs = [j for j in jobs if j["role"] == f_role]
        if f_loc.strip():
            jobs = [j for j in jobs if f_loc.strip().lower() in j["location"].lower()]
        if f_exp != "All":
            jobs = [j for j in jobs if j["exp"] == f_exp]

        st.caption(f"{len(jobs)} opening(s) found")
        if not jobs:
            st.info("No openings match your filters. Try widening the criteria.")

        for job in sorted(jobs, key=lambda j: j["posted"], reverse=True):
            st.markdown(f"""<div class="job-card">
            <div class="job-top">
            <div class="avatar-circle">{initials(job['firm'])}</div>
            <div>
            <h4>{job['title']} <span class="badge-hiring">● Actively Hiring</span></h4>
            <div class="job-firm">{job['firm']}</div>
            <div class="job-meta">📍 {job['location']} &nbsp;•&nbsp; Posted {job['posted'].strftime('%d %b %Y')}</div>
            <span class="tag tag-salary">💰 {job['ctc']}</span>
            <span class="tag tag-exp">🧭 {job['exp']}</span>
            <span class="tag">{job['role']}</span>
            <span class="tag">{job['qual']}</span>
            </div></div>
            <p style="margin-top:12px;color:#333;font-size:14px">{job['desc']}</p>
            </div>""", unsafe_allow_html=True)

            already_applied = any(
                a["job_id"] == job["id"] and a["email"] == auth["email"]
                for a in st.session_state.applications
            )
            if already_applied:
                st.caption("✅ You've already applied to this opening.")
            else:
                with st.expander(f"Apply to: {job['title']} — {job['firm']}"):
                    profile = st.session_state.candidate_profiles.get(auth["email"], {})
                    with st.form(f"apply_{job['id']}"):
                        a1, a2 = st.columns(2)
                        ap_name = a1.text_input("Full Name", value=profile.get("name", auth["display_name"]),
                                                 key=f"n{job['id']}")
                        ap_email = a2.text_input("Email", value=profile.get("email", auth["email"]),
                                                  key=f"e{job['id']}")
                        ap_note = st.text_area("Brief note to the firm", key=f"m{job['id']}", height=80)
                        if not profile.get("resume_bytes"):
                            st.caption("💡 Tip: add a résumé in your Profile (top-right) so employers can download it.")
                        if st.form_submit_button("Submit Application"):
                            if not ap_name.strip():
                                st.error("Please enter your name.")
                            elif not valid_email(ap_email):
                                st.error("Please enter a valid email address.")
                            else:
                                st.session_state.applications.append(dict(
                                    job_id=job["id"], title=job["title"], firm=job["firm"],
                                    posted_by=job.get("posted_by"), name=ap_name.strip(),
                                    email=ap_email.strip(), note=ap_note.strip(),
                                    applied=datetime.now()))
                                st.success(f"Application submitted to {job['firm']}.")
                                st.rerun()

    with tab_dash:
        st.markdown("#### My Dashboard")
        my_apps = [a for a in st.session_state.applications if a["email"] == auth["email"]]
        profile = st.session_state.candidate_profiles.get(auth["email"])

        m1, m2 = st.columns(2)
        m1.metric("Applications Submitted", len(my_apps))
        m2.metric("Profile Status", "Complete ✅" if profile else "Incomplete ⚠️")

        if not profile:
            st.warning("Your profile is incomplete. Open the profile menu (top-right) to add your "
                       "details and résumé — employers can't see or download your résumé until you do.")

        st.markdown("##### My Applications")
        if my_apps:
            df = pd.DataFrame([{
                "Job Title": a["title"], "Firm": a["firm"],
                "Applied On": a["applied"].strftime("%d %b %Y %I:%M %p"),
                "Note": a["note"] or "—",
            } for a in sorted(my_apps, key=lambda a: a["applied"], reverse=True)])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("You haven't applied to any openings yet.")

# ----------------------------------------------------------------------
# EMPLOYER VIEW
# ----------------------------------------------------------------------
def render_employer_app():
    auth = st.session_state.auth
    tab_post, tab_cands, tab_dash = st.tabs(
        ["🏢 Post an Opening", "👥 All Candidates", "📊 My Dashboard"]
    )

    with tab_post:
        st.markdown("### Find the right talent for your firm")
        st.caption("Create a professional vacancy and connect with qualified CA professionals.")
        with st.form("job_form", clear_on_submit=True):
            j1, j2 = st.columns(2)
            j_title = j1.text_input("Position Title *")
            j_firm = j2.text_input("Firm Name *", value=auth["display_name"])
            j3, j4 = st.columns(2)
            j_loc = j3.text_input("Location *")
            j_ctc = j4.text_input("CTC Range *", placeholder="e.g. 8-12 LPA")
            j5, j6, j7 = st.columns(3)
            j_role = j5.selectbox("Practice Area *", ROLES)
            j_exp = j6.selectbox("Experience Required *", EXP)
            j_qual = j7.selectbox("Minimum Qualification *", QUALS)
            j_desc = st.text_area("Role Description *", height=110)

            if st.form_submit_button("Publish Opening"):
                missing = [lbl for lbl, val in [
                    ("Position Title", j_title), ("Firm Name", j_firm),
                    ("Location", j_loc), ("CTC Range", j_ctc),
                    ("Role Description", j_desc)] if not val.strip()]
                if missing:
                    st.error("Please complete: " + ", ".join(missing))
                else:
                    st.session_state.jobs.append(dict(
                        id=max((j["id"] for j in st.session_state.jobs), default=0) + 1,
                        title=j_title.strip(), firm=j_firm.strip(), location=j_loc.strip(),
                        role=j_role, exp=j_exp, ctc=j_ctc.strip(), qual=j_qual,
                        posted=date.today(), posted_by=auth["email"], desc=j_desc.strip()))
                    st.success("Opening published. View it under 'My Dashboard'.")

    with tab_cands:
        st.markdown("#### Talent Pool — All Registered Candidates")
        all_profiles = [p for p in st.session_state.candidate_profiles.values() if p.get("consent")]

        c1, c2, c3, c4 = st.columns(4)
        f_qual = c1.selectbox("Qualification", ["All"] + QUALS, key="cand_f_qual")
        f_exp = c2.selectbox("Experience", ["All"] + EXP, key="cand_f_exp")
        f_area = c3.selectbox("Area of Interest", ["All"] + ROLES, key="cand_f_area")
        f_city = c4.text_input("City contains", "", key="cand_f_city")

        filtered = all_profiles
        if f_qual != "All":
            filtered = [p for p in filtered if p.get("qual") == f_qual]
        if f_exp != "All":
            filtered = [p for p in filtered if p.get("exp") == f_exp]
        if f_area != "All":
            filtered = [p for p in filtered if f_area in p.get("areas_list", [])]
        if f_city.strip():
            filtered = [p for p in filtered if f_city.strip().lower() in p.get("city", "").lower()]

        st.caption(f"{len(filtered)} candidate(s) found out of {len(all_profiles)} registered")

        if not all_profiles:
            st.info("No candidates have completed their profile yet.")
        elif not filtered:
            st.info("No candidates match your filters. Try widening the criteria.")

        for i, p in enumerate(sorted(filtered, key=lambda p: p.get("updated", datetime.min), reverse=True)):
            area_tags = "".join(f'<span class="tag tag-area">{a}</span>' for a in p.get("areas_list", []))
            st.markdown(f"""<div class="candidate-card">
            <div class="job-top">
            <div class="avatar-circle purple">{initials(p.get('name','?'))}</div>
            <div>
            <h4>{p.get('name','—')}</h4>
            <div class="job-meta">✉️ {p.get('email','—')} &nbsp;•&nbsp; 📞 {p.get('phone','—')}</div>
            <span class="tag tag-city">📍 {p.get('city','—')}</span>
            <span class="tag tag-exp">🧭 {p.get('exp','—')}</span>
            <span class="tag">🎓 {p.get('qual','—')}</span>
            {area_tags}
            </div></div>
            </div>""", unsafe_allow_html=True)

            cc1, cc2 = st.columns([4, 1])
            cc1.caption(f"ICAI Membership: {p.get('membership','—')}")
            if p.get("resume_bytes"):
                cc2.download_button("⬇ Résumé", data=p["resume_bytes"],
                                     file_name=p.get("resume_name", f"{p.get('name','candidate')}_resume.pdf"),
                                     mime="application/pdf", key=f"pool_resume_{i}",
                                     use_container_width=True)
            else:
                cc2.caption("No résumé")

        if filtered:
            pool_df = pd.DataFrame([{
                "Name": p.get("name", "—"), "Email": p.get("email", "—"),
                "Phone": p.get("phone", "—"), "City": p.get("city", "—"),
                "Qualification": p.get("qual", "—"), "Experience": p.get("exp", "—"),
                "Areas of Interest": p.get("areas", "—"), "Membership": p.get("membership", "—"),
            } for p in filtered])
            st.download_button("⬇ Export Candidate List (CSV)", pool_df.to_csv(index=False),
                                "all_candidates.csv", "text/csv", key="export_all_candidates")

    with tab_dash:
        st.markdown("#### My Dashboard")
        my_jobs = [j for j in st.session_state.jobs if j.get("posted_by") == auth["email"]]
        my_apps = [a for a in st.session_state.applications if a.get("posted_by") == auth["email"]]

        m1, m2, m3 = st.columns(3)
        m1.metric("My Active Postings", len(my_jobs))
        m2.metric("Total Applicants", len(my_apps))
        m3.metric("Practice Areas Covered", len({j["role"] for j in my_jobs}))

        if my_jobs:
            st.markdown("##### Openings by Practice Area")
            counts = pd.Series([j["role"] for j in my_jobs]).value_counts()
            st.bar_chart(counts)

        st.markdown("##### My Postings")
        if not my_jobs:
            st.caption("You haven't posted any openings yet. Use the 'Post an Opening' tab to get started.")
        for job in sorted(my_jobs, key=lambda j: j["posted"], reverse=True):
            applicants = [a for a in my_apps if a["job_id"] == job["id"]]
            st.markdown(f"""<div class="job-card">
            <div class="job-top">
            <div class="avatar-circle">{initials(job['firm'])}</div>
            <div>
            <h4>{job['title']}</h4>
            <div class="job-meta">📍 {job['location']} &nbsp;•&nbsp; Posted {job['posted'].strftime('%d %b %Y')}
            &nbsp;•&nbsp; {len(applicants)} applicant(s)</div>
            <span class="tag tag-salary">💰 {job['ctc']}</span>
            <span class="tag tag-exp">🧭 {job['exp']}</span>
            <span class="tag">{job['role']}</span>
            </div></div>
            </div>""", unsafe_allow_html=True)

            with st.expander(f"View {len(applicants)} applicant(s) for {job['title']}"):
                if not applicants:
                    st.caption("No applications yet for this opening.")
                else:
                    for i, a in enumerate(sorted(applicants, key=lambda a: a["applied"], reverse=True)):
                        prof = st.session_state.candidate_profiles.get(a["email"], {})
                        cols = st.columns([3, 2, 2, 2])
                        cols[0].markdown(f"**{a['name']}**\n\n{a['email']}")
                        cols[1].markdown(f"📞 {prof.get('phone', '—')}\n\n📍 {prof.get('city', '—')}")
                        cols[2].markdown(f"🎓 {prof.get('qual', '—')}\n\n🧭 {prof.get('exp', '—')}")
                        if a["note"]:
                            cols[2].caption(f"Note: {a['note']}")
                        resume_bytes = prof.get("resume_bytes")
                        if resume_bytes:
                            cols[3].download_button(
                                "⬇ Résumé", data=resume_bytes,
                                file_name=prof.get("resume_name", f"{a['name']}_resume.pdf"),
                                mime="application/pdf",
                                key=f"resume_{job['id']}_{i}",
                                use_container_width=True,
                            )
                        else:
                            cols[3].caption("No résumé on file")
                        st.divider()

                    export_rows = []
                    for a in applicants:
                        prof = st.session_state.candidate_profiles.get(a["email"], {})
                        export_rows.append({
                            "Name": a["name"], "Email": a["email"],
                            "Phone": prof.get("phone", "—"), "City": prof.get("city", "—"),
                            "Qualification": prof.get("qual", "—"), "Experience": prof.get("exp", "—"),
                            "Applied On": a["applied"].strftime("%d %b %Y %I:%M %p"),
                            "Note": a["note"] or "—",
                        })
                    exp_df = pd.DataFrame(export_rows)
                    st.download_button(
                        "⬇ Export Applicant List (CSV)", exp_df.to_csv(index=False),
                        f"applicants_{job['id']}.csv", "text/csv", key=f"export_{job['id']}",
                    )

# ----------------------------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------------------------
if not st.session_state.auth["logged_in"]:
    render_login_gate()
elif (st.session_state.auth["role"] == "employer"
      and not st.session_state.employer_accounts[st.session_state.auth["email"]].get("profile_complete")):
    render_employer_onboarding()
else:
    render_header()
    if st.session_state.auth["role"] == "employee":
        render_candidate_app()
    else:
        render_employer_app()
