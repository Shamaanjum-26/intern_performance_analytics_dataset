from flask import Flask, request, redirect, render_template_string
import pandas as pd
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "intern_final_dataset.xlsx")

def load_df():
    return pd.read_excel(EXCEL_FILE)

def save_df(df):
    df.to_excel(EXCEL_FILE, index=False)

def calc_task_completion(tasks_assigned, tasks_completed):
    try:
        return round((int(tasks_completed) / int(tasks_assigned)) * 100, 2)
    except:
        return 0.0

def calc_performance_level(task_pct, comm, tech, teamwork, problem):
    try:
        avg_score = (int(comm) + int(tech) + int(teamwork) + int(problem)) / 4
        if task_pct >= 90 and avg_score >= 3.5:
            return "High"
        elif task_pct >= 60 and avg_score >= 2.5:
            return "Medium"
        else:
            return "Low"
    except:
        return "Low"

def calc_rating(performance_level):
    return {"High": 5, "Medium": 3, "Low": 1}[performance_level]

def calc_productivity_score(attendance, meetings, tasks_pct, comm, tech, teamwork, problem):
    try:
        return round(
            float(attendance) * 0.3 +
            float(tasks_pct) * 0.3 +
            (int(comm) + int(tech) + int(teamwork) + int(problem)) / 4 * 10 * 0.4,
            2
        )
    except:
        return 0.0

def calc_productivity_level(score):
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"

def calc_risk_status(attendance, late_submissions, task_pct):
    try:
        if float(attendance) < 75 or int(late_submissions) > 3 or float(task_pct) < 50:
            return "At Risk"
        else:
            return "Safe"
    except:
        return "At Risk"

BASE_STYLE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InternTrack — Intern Management System</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #13131a;
    --surface2: #1c1c27;
    --border: #2a2a3a;
    --accent: #7c5cfc;
    --accent2: #fc5c7d;
    --teal: #00d4aa;
    --amber: #ffb347;
    --text: #e8e8f0;
    --muted: #7a7a9a;
    --high: #00d4aa;
    --med: #ffb347;
    --low: #fc5c7d;
    --safe: #00d4aa;
    --risk: #fc5c7d;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    background-image: radial-gradient(ellipse at 20% 20%, rgba(124,92,252,0.08) 0%, transparent 60%),
                      radial-gradient(ellipse at 80% 80%, rgba(252,92,125,0.06) 0%, transparent 60%);
  }
  /* NAV */
  .navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 40px;
    background: rgba(19,19,26,0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
  }
  .logo {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }
  .logo span { -webkit-text-fill-color: var(--text); }
  .nav-links a {
    color: var(--muted); text-decoration: none; font-size: 14px;
    font-weight: 500; margin-left: 28px;
    transition: color 0.2s;
  }
  .nav-links a:hover, .nav-links a.active { color: var(--text); }
  /* CONTAINER */
  .container { max-width: 1200px; margin: 0 auto; padding: 40px 24px; }
  /* STATS ROW */
  .stats-row {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px;
  }
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 20px 24px;
    position: relative; overflow: hidden;
    transition: transform 0.2s, border-color 0.2s;
  }
  .stat-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  }
  .stat-card.purple::before { background: linear-gradient(90deg, var(--accent), transparent); }
  .stat-card.pink::before   { background: linear-gradient(90deg, var(--accent2), transparent); }
  .stat-card.teal::before   { background: linear-gradient(90deg, var(--teal), transparent); }
  .stat-card.amber::before  { background: linear-gradient(90deg, var(--amber), transparent); }
  .stat-label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
  .stat-value { font-family: 'Syne', sans-serif; font-size: 32px; font-weight: 700; }
  .stat-card.purple .stat-value { color: var(--accent); }
  .stat-card.pink .stat-value   { color: var(--accent2); }
  .stat-card.teal .stat-value   { color: var(--teal); }
  .stat-card.amber .stat-value  { color: var(--amber); }
  /* PAGE HEADER */
  .page-header {
    display: flex; align-items: center; justify-content: space-between; margin-bottom: 28px;
  }
  .page-title {
    font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 700;
  }
  /* BUTTON */
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 12px 24px; border-radius: 12px; font-size: 14px;
    font-weight: 500; cursor: pointer; text-decoration: none;
    border: none; transition: all 0.2s; font-family: 'DM Sans', sans-serif;
  }
  .btn-primary {
    background: linear-gradient(135deg, var(--accent), #9b7cff);
    color: white;
    box-shadow: 0 4px 20px rgba(124,92,252,0.3);
  }
  .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(124,92,252,0.4); }
  .btn-sm {
    padding: 6px 14px; font-size: 12px; border-radius: 8px;
  }
  .btn-edit {
    background: rgba(124,92,252,0.15); color: var(--accent);
    border: 1px solid rgba(124,92,252,0.3);
  }
  .btn-edit:hover { background: rgba(124,92,252,0.25); }
  .btn-delete {
    background: rgba(252,92,125,0.15); color: var(--accent2);
    border: 1px solid rgba(252,92,125,0.3);
  }
  .btn-delete:hover { background: rgba(252,92,125,0.25); }
  /* SEARCH BAR */
  .search-bar {
    display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
  }
  .search-input {
    flex: 1; padding: 12px 16px;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; color: var(--text); font-size: 14px;
    font-family: 'DM Sans', sans-serif; outline: none;
    transition: border-color 0.2s;
  }
  .search-input:focus { border-color: var(--accent); }
  .search-input::placeholder { color: var(--muted); }
  /* TABLE */
  .table-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; overflow: hidden;
  }
  table { width: 100%; border-collapse: collapse; }
  thead { background: var(--surface2); }
  th {
    padding: 14px 18px; text-align: left;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px;
    color: var(--muted);
  }
  td { padding: 14px 18px; font-size: 13px; border-top: 1px solid var(--border); }
  tr:hover td { background: rgba(124,92,252,0.04); }
  .intern-name { font-weight: 500; color: var(--text); }
  .intern-id { color: var(--muted); font-size: 12px; }
  /* BADGES */
  .badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.5px;
  }
  .badge-high   { background: rgba(0,212,170,0.15); color: var(--high); border: 1px solid rgba(0,212,170,0.3); }
  .badge-medium { background: rgba(255,179,71,0.15); color: var(--med);  border: 1px solid rgba(255,179,71,0.3); }
  .badge-low    { background: rgba(252,92,125,0.15); color: var(--low);  border: 1px solid rgba(252,92,125,0.3); }
  .badge-safe   { background: rgba(0,212,170,0.15); color: var(--safe); border: 1px solid rgba(0,212,170,0.3); }
  .badge-risk   { background: rgba(252,92,125,0.15); color: var(--risk); border: 1px solid rgba(252,92,125,0.3); }
  /* PROGRESS BAR */
  .progress-wrap { display: flex; align-items: center; gap: 10px; }
  .progress-bar { flex: 1; height: 4px; background: var(--border); border-radius: 4px; overflow: hidden; }
  .progress-fill { height: 100%; border-radius: 4px; transition: width 0.5s; }
  .progress-text { font-size: 12px; color: var(--muted); min-width: 38px; text-align: right; }
  /* FORM PAGE */
  .form-page { max-width: 820px; margin: 0 auto; padding: 40px 24px; }
  .form-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 24px; padding: 40px; margin-top: 24px;
  }
  .form-title {
    font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 700; margin-bottom: 6px;
  }
  .form-subtitle { color: var(--muted); font-size: 14px; margin-bottom: 36px; }
  .form-section-title {
    font-family: 'Syne', sans-serif; font-size: 13px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1.5px; color: var(--accent);
    margin: 28px 0 16px; padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  .form-group.full { grid-column: 1 / -1; }
  label { font-size: 12px; font-weight: 500; color: var(--muted); letter-spacing: 0.5px; text-transform: uppercase; }
  input, select {
    padding: 12px 16px; background: var(--surface2);
    border: 1px solid var(--border); border-radius: 12px;
    color: var(--text); font-size: 14px;
    font-family: 'DM Sans', sans-serif; outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    -webkit-appearance: none;
  }
  input:focus, select:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(124,92,252,0.15);
  }
  input::placeholder { color: var(--muted); }
  select option { background: var(--surface2); }
  .score-group { display: flex; flex-direction: column; gap: 6px; }
  .score-label-row { display: flex; justify-content: space-between; align-items: center; }
  .score-display {
    font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: var(--accent);
  }
  input[type=range] {
    padding: 0; height: 6px; border-radius: 6px;
    background: var(--border); cursor: pointer; border: none;
    accent-color: var(--accent);
  }
  .auto-calc-notice {
    background: rgba(124,92,252,0.08); border: 1px solid rgba(124,92,252,0.2);
    border-radius: 12px; padding: 14px 18px; margin: 24px 0;
    font-size: 13px; color: var(--muted);
    display: flex; align-items: center; gap: 10px;
  }
  .auto-calc-notice span { color: var(--accent); font-weight: 600; }
  .form-actions { display: flex; gap: 12px; margin-top: 32px; justify-content: flex-end; }
  .btn-ghost {
    background: transparent; color: var(--muted);
    border: 1px solid var(--border);
  }
  .btn-ghost:hover { border-color: var(--text); color: var(--text); }
  /* BACK LINK */
  .back-link {
    display: inline-flex; align-items: center; gap: 8px;
    color: var(--muted); text-decoration: none; font-size: 13px;
    transition: color 0.2s; margin-bottom: 8px;
  }
  .back-link:hover { color: var(--text); }
  /* EMPTY STATE */
  .empty { text-align: center; padding: 60px; color: var(--muted); }
  /* RESPONSIVE */
  @media (max-width: 768px) {
    .stats-row { grid-template-columns: 1fr 1fr; }
    .form-grid, .form-grid-3 { grid-template-columns: 1fr; }
    .navbar { padding: 14px 20px; }
    .container { padding: 24px 16px; }
  }
</style>
</head>
"""

def navbar(active="list"):
    return f"""
    {BASE_STYLE}
    <body>
    <nav class="navbar">
      <div class="logo">Intern<span>Track</span></div>
      <div class="nav-links">
        <a href="/" class="{'active' if active=='list' else ''}">All Interns</a>
        <a href="/add" class="{'active' if active=='add' else ''}">+ Add Intern</a>
      </div>
    </nav>
    """

@app.route("/")
def index():
    df = load_df()
    total = len(df)
    high = len(df[df["Performance_Level"] == "High"])
    at_risk = len(df[df["Risk_Status"] == "At Risk"]) if "Risk_Status" in df.columns else 0
    avg_task = round(df["Task_Completion_%"].mean(), 1)

    rows = ""
    for _, r in df.iterrows():
        lvl = str(r.get("Performance_Level", "")).strip().capitalize()
        risk = str(r.get("Risk_Status", "Safe")).strip()
        task_pct = float(r.get("Task_Completion_%", 0))
        capped = min(task_pct, 100)
        if task_pct >= 80:
            bar_color = "var(--high)"
        elif task_pct >= 50:
            bar_color = "var(--med)"
        else:
            bar_color = "var(--low)"

        badge_lvl = f"badge-{lvl.lower()}"
        badge_risk = "badge-safe" if risk == "Safe" else "badge-risk"

        rows += f"""
        <tr>
          <td><div class="intern-id">#{r['Intern_ID']}</div></td>
          <td><div class="intern-name">{r['Intern_Name']}</div>
              <div style="font-size:11px;color:var(--muted)">{r.get('Department','')}</div></td>
          <td>{r.get('College_Name','')}</td>
          <td>{r.get('Mentor_Name','')}</td>
          <td>
            <div class="progress-wrap">
              <div class="progress-bar">
                <div class="progress-fill" style="width:{capped}%;background:{bar_color}"></div>
              </div>
              <div class="progress-text">{task_pct:.1f}%</div>
            </div>
          </td>
          <td><span class="badge {badge_lvl}">{lvl}</span></td>
          <td><span class="badge {badge_risk}">{risk}</span></td>
          <td>
            <div style="display:flex;gap:6px">
              <a href="/edit/{r['Intern_ID']}" class="btn btn-sm btn-edit">Edit</a>
              <a href="/delete/{r['Intern_ID']}"
                 onclick="return confirm('Delete {r['Intern_Name']}?')"
                 class="btn btn-sm btn-delete">Delete</a>
            </div>
          </td>
        </tr>"""

    return navbar("list") + f"""
    <div class="container">
      <div class="stats-row">
        <div class="stat-card purple">
          <div class="stat-label">Total Interns</div>
          <div class="stat-value">{total}</div>
        </div>
        <div class="stat-card teal">
          <div class="stat-label">High Performers</div>
          <div class="stat-value">{high}</div>
        </div>
        <div class="stat-card amber">
          <div class="stat-label">Avg Task Completion</div>
          <div class="stat-value">{avg_task}%</div>
        </div>
        <div class="stat-card pink">
          <div class="stat-label">At Risk</div>
          <div class="stat-value">{at_risk}</div>
        </div>
      </div>

      <div class="page-header">
        <div class="page-title">Intern Records</div>
        <div style="display:flex;gap:10px;align-items:center">
          <input class="search-input" id="searchInput" placeholder="🔍  Search by name, dept, mentor..."
                 oninput="filterTable()" style="width:280px">
          <a href="/add" class="btn btn-primary">＋ Add New Intern</a>
        </div>
      </div>

      <div class="table-wrap">
        <table id="internTable">
          <thead>
            <tr>
              <th>ID</th>
              <th>Intern</th>
              <th>College</th>
              <th>Mentor</th>
              <th>Task Completion</th>
              <th>Performance</th>
              <th>Risk</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>

    <script>
    function filterTable() {{
      const q = document.getElementById('searchInput').value.toLowerCase();
      document.querySelectorAll('#internTable tbody tr').forEach(row => {{
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
      }});
    }}
    </script>
    </body></html>"""

def render_form(action, values=None, intern_id=None):
    v = values or {}
    is_edit = intern_id is not None
    hidden = f'<input type="hidden" name="intern_id" value="{intern_id}">' if is_edit else ""

    def val(k, default=""):
        return v.get(k, default)

    def sel(field, options):
        current = str(val(field, "")).strip()
        opts = "".join(
            f'<option value="{o}" {"selected" if o == current else ""}>{o}</option>'
            for o in options
        )
        return f'<select name="{field}">{opts}</select>'

    def score_slider(field, label_text):
        cur = int(float(val(field, 3)))
        return f"""
        <div class="score-group">
          <div class="score-label-row">
            <label>{label_text}</label>
            <div class="score-display" id="disp_{field}">{cur}</div>
          </div>
          <input type="range" name="{field}" min="1" max="5" value="{cur}"
                 oninput="document.getElementById('disp_{field}').innerText=this.value">
        </div>"""

    return navbar("add" if not is_edit else "list") + f"""
    <div class="form-page">
      <a href="/" class="back-link">← Back to All Interns</a>

      <div class="form-card">
        <div class="form-title">{'Edit Intern Record' if is_edit else 'Add New Intern'}</div>
        <div class="form-subtitle">
          {'Update the intern details below.' if is_edit else 'Fill in the details to add a new intern to the system.'}
          Task Completion %, Performance Level, Risk Status and Productivity are calculated automatically.
        </div>

        <form method="POST" action="{action}">
          {hidden}

          <div class="form-section-title">Personal Information</div>
          <div class="form-grid">
            <div class="form-group">
              <label>Full Name</label>
              <input name="Intern_Name" value="{val('Intern_Name')}" placeholder="e.g. Anitha" required>
            </div>
            <div class="form-group">
              <label>Age</label>
              <input name="Age" type="number" value="{val('Age')}" placeholder="e.g. 21" min="18" max="30" required>
            </div>
            <div class="form-group">
              <label>Gender</label>
              {sel('Gender', ['Male', 'Female', 'Other'])}
            </div>
            <div class="form-group">
              <label>City</label>
              <input name="City" value="{val('City')}" placeholder="e.g. Chennai">
            </div>
          </div>

          <div class="form-section-title">Academic Details</div>
          <div class="form-grid">
            <div class="form-group full">
              <label>College Name</label>
              <input name="College_Name" value="{val('College_Name')}" placeholder="e.g. Anna University" required>
            </div>
            <div class="form-group">
              <label>Degree</label>
              {sel('Degree', ['B.Tech', 'B.Sc', 'BCA', 'MCA', 'M.Tech', 'MBA'])}
            </div>
            <div class="form-group">
              <label>Department</label>
              {sel('Department', ['Data Science', 'AI', 'Full Stack', 'Data Analyst', 'Cloud', 'ML'])}
            </div>
          </div>

          <div class="form-section-title">Internship Details</div>
          <div class="form-grid">
            <div class="form-group">
              <label>Internship Mode</label>
              {sel('Internship_Mode', ['Onsite', 'Remote', 'Hybrid'])}
            </div>
            <div class="form-group">
              <label>Duration (Months)</label>
              <input name="Intern_Duration" type="number" value="{val('Intern_Duration')}" placeholder="e.g. 3" min="1" max="12" required>
            </div>
            <div class="form-group">
              <label>Project Assigned</label>
              {sel('Project_Assigned', ['Intern Insight Dashboard','Sales Analytics','ML Prediction Model','Data Visualization','Customer Analysis'])}
            </div>
            <div class="form-group">
              <label>Mentor Name</label>
              {sel('Mentor_Name', ['Suresh','Anand','Ravi','Karthik','Prakash'])}
            </div>
            <div class="form-group">
              <label>Stipend (₹)</label>
              <input name="Stipend" type="number" value="{val('Stipend', 0)}" placeholder="e.g. 5000" min="0">
            </div>
          </div>

          <div class="form-section-title">Performance Metrics</div>
          <div class="form-grid">
            <div class="form-group">
              <label>Tasks Assigned</label>
              <input name="Tasks_Assigned" type="number" value="{val('Tasks_Assigned')}" placeholder="e.g. 20" min="1" required>
            </div>
            <div class="form-group">
              <label>Tasks Completed</label>
              <input name="Tasks_Completed" type="number" value="{val('Tasks_Completed')}" placeholder="e.g. 18" min="0" required>
            </div>
            <div class="form-group">
              <label>Attendance %</label>
              <input name="Attendance_Percentage" type="number" value="{val('Attendance_Percentage')}" placeholder="e.g. 90" min="0" max="100" required>
            </div>
            <div class="form-group">
              <label>Late Submissions</label>
              <input name="Late_Submissions" type="number" value="{val('Late_Submissions', 0)}" placeholder="e.g. 2" min="0">
            </div>
            <div class="form-group">
              <label>Meetings Attended</label>
              <input name="Meetings_Attended" type="number" value="{val('Meetings_Attended', 0)}" placeholder="e.g. 10" min="0">
            </div>
          </div>

          <div class="form-section-title">Skill Scores (1 = Low, 5 = High)</div>
          <div class="form-grid">
            {score_slider('Communication_Score', 'Communication')}
            {score_slider('Technical_Score', 'Technical')}
            {score_slider('Teamwork_Score', 'Teamwork')}
            {score_slider('Problem_Solving_Score', 'Problem Solving')}
          </div>

          <div class="form-section-title">Outcome</div>
          <div class="form-grid">
            <div class="form-group">
              <label>Certificate Eligible</label>
              {sel('Certificate_Eligible', ['Yes', 'No'])}
            </div>
            <div class="form-group">
              <label>Placement Recommended</label>
              {sel('Placement_Recommended', ['Yes', 'No'])}
            </div>
          </div>

          <div class="auto-calc-notice">
            ✦ <span>Auto-calculated on save:</span>
            Task Completion % · Performance Level · Risk Status · Productivity Score & Level · Final Rating
          </div>

          <div class="form-actions">
            <a href="/" class="btn btn-ghost">Cancel</a>
            <button type="submit" class="btn btn-primary">
              {'💾 Update Intern' if is_edit else '＋ Add Intern'}
            </button>
          </div>
        </form>
      </div>
    </div>
    </body></html>"""

@app.route("/add")
def add_page():
    return render_form("/add")

@app.route("/add", methods=["POST"])
def add_intern():
    d = request.form.to_dict()
    task_pct = calc_task_completion(d["Tasks_Assigned"], d["Tasks_Completed"])
    perf_level = calc_performance_level(
        task_pct,
        d["Communication_Score"], d["Technical_Score"],
        d["Teamwork_Score"], d["Problem_Solving_Score"]
    )
    prod_score = calc_productivity_score(
        d["Attendance_Percentage"], d["Meetings_Attended"], task_pct,
        d["Communication_Score"], d["Technical_Score"],
        d["Teamwork_Score"], d["Problem_Solving_Score"]
    )
    d["Task_Completion_%"] = task_pct
    d["Performance_Level"] = perf_level
    d["Final_Performance_Rating"] = calc_rating(perf_level)
    d["Risk_Status"] = calc_risk_status(d["Attendance_Percentage"], d["Late_Submissions"], task_pct)
    d["Productivity_Score"] = prod_score
    d["Productivity_Level"] = calc_productivity_level(prod_score)

    df = load_df()
    d["Intern_ID"] = int(df["Intern_ID"].max() or 0) + 1
    df = pd.concat([df, pd.DataFrame([d])], ignore_index=True)
    save_df(df)
    return redirect("/")

@app.route("/edit/<int:intern_id>")
def edit_page(intern_id):
    df = load_df()
    row = df[df["Intern_ID"] == intern_id].iloc[0]
    return render_form("/edit", values=row.to_dict(), intern_id=intern_id)

@app.route("/edit", methods=["POST"])
def edit_intern():
    d = request.form.to_dict()
    intern_id = int(d.pop("intern_id"))
    task_pct = calc_task_completion(d["Tasks_Assigned"], d["Tasks_Completed"])
    perf_level = calc_performance_level(
        task_pct,
        d["Communication_Score"], d["Technical_Score"],
        d["Teamwork_Score"], d["Problem_Solving_Score"]
    )
    prod_score = calc_productivity_score(
        d["Attendance_Percentage"], d["Meetings_Attended"], task_pct,
        d["Communication_Score"], d["Technical_Score"],
        d["Teamwork_Score"], d["Problem_Solving_Score"]
    )
    d["Task_Completion_%"] = task_pct
    d["Performance_Level"] = perf_level
    d["Final_Performance_Rating"] = calc_rating(perf_level)
    d["Risk_Status"] = calc_risk_status(d["Attendance_Percentage"], d["Late_Submissions"], task_pct)
    d["Productivity_Score"] = prod_score
    d["Productivity_Level"] = calc_productivity_level(prod_score)

    df = load_df()
    for key, value in d.items():
        if key in df.columns:
            df.loc[df["Intern_ID"] == intern_id, key] = value
    save_df(df)
    return redirect("/")

@app.route("/delete/<int:intern_id>")
def delete_intern(intern_id):
    df = load_df()
    df = df[df["Intern_ID"] != intern_id]
    save_df(df)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
