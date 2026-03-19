from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
SOURCE_PDFS = [ROOT / "Cours_DevOps.pdf", ROOT / "PPT_DevOps.pdf"]
OUTPUT_PDF = ROOT / "Examen_Controle_DevOps.pdf"


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
        "EXAMEN DE CONTROLE DE CONNAISSANCES - DEVOPS",
        "",
        "Instructions:",
        "- Durée: 1h30",
        "- Répondez de manière concise et argumentée.",
        "- L'examen couvre les notions du cours Cours_DevOps.pdf et PPT_DevOps.pdf.",
        f"- Thèmes détectés automatiquement depuis les supports: {topics_text}.",
        "",
        "PARTIE A - Questions de cours (10 points)",
        "1) Definir DevOps et expliquer en quoi il depasse un simple choix d'outils.",
        "2) Expliquer l'origine de DevOps: quels problemes organisationnels cherchait-on a resoudre?",
        "3) Donner trois avantages concrets de l'approche DevOps pour une entreprise.",
        "4) Decrire le role de la collaboration Dev/Ops dans la reduction des incidents en production.",
        "",
        "PARTIE B - CI/CD et automatisation (10 points)",
        "5) Différencier Intégration Continue (CI), Livraison Continue (CD) et Déploiement Continu.",
        "6) Expliquer le role d'un pipeline Jenkins et proposer des etapes typiques.",
        "7) Donner deux bonnes pratiques pour fiabiliser un pipeline CI/CD.",
        "8) Pourquoi l'automatisation des tests est-elle essentielle en DevOps?",
        "",
        "PARTIE C - Conteneurs, orchestration et configuration (10 points)",
        "9) Comparer conteneur Docker et machine virtuelle (VM): 2 differences majeures.",
        "10) Expliquer l'interet de Docker dans une chaine DevOps.",
        "11) Citer les concepts clés de Kubernetes utiles pour un déploiement applicatif.",
        "12) Expliquer comment Ansible aide a industrialiser la gestion de configuration.",
        "",
        "PARTIE D - Cas pratique (10 points)",
        "13) Vous devez livrer une application web rapidement sans dégrader la stabilité.",
        "    Proposer une demarche DevOps complete: de la phase de dev jusqu'au suivi en production.",
        "    Votre reponse doit mentionner: pipeline, tests, conteneurisation, deploiement, monitoring.",
    ]

    correction_lines = [
        "CORRECTION (elements attendus)",
        "",
        "1) DevOps: culture + pratiques + automatisation pour rapprocher Dev et Ops.",
        "2) Origine: résoudre les silos, conflits 'ça marche chez moi', lenteur et risque de déploiement.",
        "3) Exemples d'avantages: cycle de livraison plus rapide, meilleure fiabilité, feedback continu.",
        "4) Collaboration: responsabilité partagée, meilleure communication, incidents réduits.",
        "5) CI = integration/tests frequents; CD = logiciel toujours livrable;",
        "   Deploiement continu = mise en production automatique apres validation.",
        "6) Jenkins pipeline: build -> tests -> qualite -> package -> deploiement (staging/prod).",
        "7) Bonnes pratiques: pipeline as code, tests automatisés, contrôle de version, rollback.",
        "8) Les tests automatisés détectent vite les régressions et sécurisent les livraisons fréquentes.",
        "9) Docker vs VM: conteneur plus léger/rapide, partage le noyau OS, démarrage plus court.",
        "10) Docker: reproductibilité des environnements, portabilité, déploiement cohérent.",
        "11) Kubernetes: pods, deployments, services, scaling, auto-healing, rolling updates.",
        "12) Ansible: configuration as code via playbooks, idempotence, standardisation, traçabilité.",
        "13) Cas pratique attendu:",
        "   - Branching + revue de code + tests unitaires/integration",
        "   - Pipeline CI/CD Jenkins avec quality gate",
        "   - Build image Docker versionnée",
        "   - Deploiement Kubernetes progressif (staging puis production)",
        "   - Supervision/monitoring + alerting + boucle d'amélioration continue",
    ]
    return exam_lines, correction_lines


def generate_exam_pdf() -> None:
    course_content = extract_text(SOURCE_PDFS)
    topics = infer_topics(course_content)
    exam_lines, correction_lines = build_exam(topics)

    pdf = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    pdf.setTitle("Examen de controle de connaissances - DevOps")
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
