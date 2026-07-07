import json
import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PATH = Path(__file__).resolve().parents[2] / "data" / "technology_taxonomy.json"

with open(PATH, "r", encoding="utf-8") as file:
    taxonomy = json.load(file)

TECH_KEYWORDS = sorted(set(taxonomy["keywords"]))
ALIASES = taxonomy["aliases"]

@dataclass
class AnalysisResult:
    fit_score: float
    similarity_score: float
    skill_coverage: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendations: list[str]
    outreach_message: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    escaped = re.escape(phrase.lower())
    return re.search(rf"(?<![a-z0-9+#]){escaped}(?![a-z0-9+#])", text) is not None


def extract_skills(text: str) -> set[str]:
    normalized = _normalize(text)
    found: set[str] = set()

    for keyword in TECH_KEYWORDS:
        variants = ALIASES.get(keyword, [keyword])
        if any(_contains_phrase(normalized, variant) for variant in variants):
            found.add(keyword)

    return found


def calculate_similarity(cv_text: str, job_description: str) -> float:
    documents = [cv_text.strip(), job_description.strip()]
    if not all(documents):
        return 0.0

    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=1500).fit_transform(documents)
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except ValueError:
        return 0.0


def generate_recommendations(missing_keywords: list[str], matched_keywords: list[str], fit_score: float) -> list[str]:
    recommendations: list[str] = []

    if fit_score < 45:
        recommendations.append(
            "This offer is currently a weak match. Apply only if it is an internship or junior role.")
    elif fit_score < 70:
        recommendations.append("This is a realistic application, but the CV should be tailored before sending.")
    else:
        recommendations.append("This offer looks like a strong match. Prepare a personalized message and apply.")

    if missing_keywords:
        recommendations.append(
            "Add evidence for these missing skills if you really know them: " + ", ".join(missing_keywords[:8]) + ".")
        recommendations.append("Build one small GitHub feature using: " + ", ".join(missing_keywords[:3]) + ".")

    if matched_keywords:
        recommendations.append(
            "Keep these keywords visible in your CV/GitHub README: " + ", ".join(matched_keywords[:8]) + ".")

    return recommendations


def generate_consent_message(company: str, job_title: str) -> str:
    return (
        f"I hereby consent to the processing of my personal data for the purpose "
        f"of conducting the recruitment process for the {job_title} position at {company}."
    )


def analyze_application(company: str, job_title: str, cv_text: str, job_description: str) -> AnalysisResult:
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_description)

    matched = sorted(cv_skills & job_skills)
    missing = sorted(job_skills - cv_skills)

    similarity = calculate_similarity(cv_text, job_description)
    skill_coverage = round((len(matched) / len(job_skills)) * 100, 2) if job_skills else 0.0
    fit_score = round((skill_coverage * 0.7) + (similarity * 0.3), 2)

    return AnalysisResult(
        fit_score=fit_score,
        similarity_score=similarity,
        skill_coverage=skill_coverage,
        matched_keywords=matched,
        missing_keywords=missing,
        recommendations=generate_recommendations(missing, matched, fit_score),
        outreach_message=generate_consent_message(company, job_title),
    )
