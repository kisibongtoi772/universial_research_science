import os

def write_report(session_id: str, report_name: str, content: str) -> str:
    """
    Writes a markdown report to the sessions directory.
    """
    if not report_name.endswith(".md"):
        report_name += ".md"
        
    base_dir = os.path.join(".sessions", session_id, "reports")
    os.makedirs(base_dir, exist_ok=True)
    
    report_path = os.path.join(base_dir, report_name)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return f"Report successfully written to {report_path}"
