from app.services.analyzer import analyze_application, extract_skills


def test_extract_skills_finds_common_backend_keywords():
    skills = extract_skills("Python FastAPI PostgreSQL Docker Git pytest")
    assert "python" in skills
    assert "fastapi" in skills
    assert "postgresql" in skills
    assert "docker" in skills


def test_analysis_returns_missing_keywords():
    result = analyze_application(
        company="Example Corp",
        job_title="Junior Backend Developer",
        cv_text="I know Python, FastAPI, SQL and Git. I built a backend API project.",
        job_description="We need Python, FastAPI, Docker, PostgreSQL and REST API skills.",
    )
    assert result.fit_score > 0
    assert "python" in result.matched_keywords
    assert "docker" in result.missing_keywords
