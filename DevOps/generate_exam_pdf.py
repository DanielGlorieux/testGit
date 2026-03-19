from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
SOURCE_PDFS = [ROOT / "Cours_DevOps.pdf", ROOT / "PPT_DevOps.pdf"]
OUTPUT_PDF = ROOT / "Examen_Controle_DevOps_V2.pdf"


def extract_text(pdf_paths: Iterable[Path]) -> str:
    chunks: list[str] = []
    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def infer_topics(content: str) -> list[str]:
    topic_keywords = {
        "Culture DevOps": ["culture", "collaboration", "communication", "silo"],
        "CI/CD": ["ci/cd", "intégration continue", "livraison continue", "jenkins", "pipeline"],
        "Conteneurisation": ["docker", "conteneur", "vm", "image"],
        "Orchestration": ["kubernetes", "orchestration", "pod", "déploiement"],
        "Configuration as Code": ["ansible", "playbook", "configuration", "automatisation"],
    }
    lowered = content.lower()
    topics = [name for name, keys in topic_keywords.items() if any(key in lowered for key in keys)]
    return topics or ["Fondamentaux DevOps"]


def draw_multiline_text(pdf: canvas.Canvas, lines: list[str], x: float, y: float, line_height: float) -> float:
    current_y = y
    for line in lines:
        if current_y < 2 * cm:
            pdf.showPage()
            pdf.setFont("Helvetica", 11)
            current_y = A4[1] - 2 * cm
        pdf.drawString(x, current_y, line)
        current_y -= line_height
    return current_y


def build_exam(topics: list[str]) -> tuple[list[str], list[str]]:
    topics_text = ", ".join(topics)
    exam_lines = [
        "EXAMEN DE CONTROLE DE CONNAISSANCES - DEVOPS (VERSION 2)",
        "",
        "Nom & Prénom: ______________________    Classe: ________    Date: __/__/____",
        "",
        "Instructions:",
        "- Durée: 1h30",
        "- Répondez de manière concise et argumentée.",
        "- Cette version 2 combine QCM, questions ouvertes et cas pratique.",
        "- L'examen couvre les notions du cours Cours_DevOps.pdf et PPT_DevOps.pdf.",
        f"- Thèmes détectés automatiquement depuis les supports: {topics_text}.",
        "",
        "PARTIE A - QCM (10 points, 2 points par question)",
        "1) Le DevOps est avant tout:",
        "   A. Un outil de déploiement   B. Une culture de collaboration Dev/Ops",
        "   C. Un type de base de données D. Une méthode sans automatisation",
        "2) La CI (Intégration Continue) consiste principalement à:",
        "   A. Déployer en prod sans tests   B. Intégrer et tester fréquemment",
        "   C. Faire uniquement du monitoring D. Supprimer les revues de code",
        "3) Docker permet principalement:",
        "   A. De remplacer Git   B. D'orchestrer des clusters seul",
        "   C. De packager une app et ses dépendances dans un conteneur   D. D'écrire des playbooks",
        "4) Kubernetes est utilisé surtout pour:",
        "   A. Orchestrer les conteneurs   B. Gérer les tickets",
        "   C. Compresser les images      D. Remplacer les tests",
        "5) Ansible sert principalement à:",
        "   A. Gérer la configuration par code   B. Écrire du front-end",
        "   C. Faire du versioning Git            D. Simuler des bases SQL",
        "",
        "PARTIE B - Questions ouvertes (12 points, 4 points par question)",
        "6) Différencier CI, CD (livraison continue) et déploiement continu avec un exemple concret.",
        "7) Proposer un pipeline Jenkins type (étapes + objectif de chaque étape).",
        "8) Donner trois bonnes pratiques de fiabilité/sécurité dans un pipeline CI/CD.",
        "",
        "PARTIE C - Conteneurs, orchestration et configuration (8 points)",
        "9) Comparer conteneur Docker et machine virtuelle (VM): 3 différences majeures.",
        "10) Citer et expliquer 4 concepts Kubernetes utiles en production.",
        "11) Expliquer comment Ansible industrialise la gestion de configuration.",
        "",
        "PARTIE D - Cas pratique intégré (10 points)",
        "12) Contexte: une application web est livrée avec des incidents fréquents en production.",
        "    Proposez une démarche DevOps complète de la conception au run.",
        "    Exigences minimales dans votre réponse:",
        "    - workflow Git + revue de code",
        "    - pipeline CI/CD avec quality gates",
        "    - conteneurisation Docker",
        "    - déploiement progressif Kubernetes",
        "    - monitoring, alerting, rollback et amélioration continue",
        "",
        "Barème global: /40",
    ]

    correction_lines = [
        "CORRECTION (VERSION 2 - ÉLÉMENTS ATTENDUS)",
        "",
        "QCM:",
        "1) B  2) B  3) C  4) A  5) A",
        "",
        "Questions ouvertes:",
        "6) CI: intégration + tests fréquents; CD: artefact toujours déployable;",
        "   déploiement continu: mise en production automatique après validation.",
        "7) Exemple pipeline: lint -> tests -> build -> scan sécurité -> package -> deploy staging -> deploy prod.",
        "8) Bonnes pratiques attendues (3 minimum):",
        "   tests automatisés, quality gates, scans sécurité, pipeline as code, secrets management, rollback.",
        "",
        "Conteneurs / orchestration / config:",
        "9) Docker vs VM: légèreté, vitesse de démarrage, partage noyau, portabilité, densité supérieure.",
        "10) Concepts Kubernetes attendus (4): Pods, Deployments, Services, Ingress, HPA, ConfigMaps/Secrets.",
        "11) Ansible: playbooks déclaratifs, idempotence, standardisation, reproductibilité, traçabilité.",
        "",
        "Cas pratique:",
        "12) Réponse attendue:",
        "   - Branching + revue de code + tests unitaires/intégration",
        "   - Pipeline CI/CD Jenkins avec quality gates",
        "   - Build image Docker versionnée",
        "   - Déploiement Kubernetes progressif (staging -> production)",
        "   - Supervision/monitoring + alerting + boucle d'amélioration continue",
        "   - Stratégie de rollback et post-mortem des incidents",
        "",
        "Notation suggérée: QCM /10, Ouvertes /12, Conteneurs/K8s/Ansible /8, Cas pratique /10.",
    ]
    return exam_lines, correction_lines


def generate_exam_pdf() -> None:
    course_content = extract_text(SOURCE_PDFS)
    topics = infer_topics(course_content)
    exam_lines, correction_lines = build_exam(topics)

    pdf = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    pdf.setTitle("Examen de controle de connaissances - DevOps - Version 2")
    pdf.setAuthor("Generation automatique depuis supports DevOps")
    pdf.setFont("Helvetica", 11)

    top_y = A4[1] - 2 * cm
    y = draw_multiline_text(pdf, exam_lines, x=2 * cm, y=top_y, line_height=0.6 * cm)
    y -= 0.8 * cm
    draw_multiline_text(pdf, correction_lines, x=2 * cm, y=y, line_height=0.6 * cm)
    pdf.save()


if __name__ == "__main__":
    generate_exam_pdf()
    print(f"PDF généré: {OUTPUT_PDF}")
