import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import uuid

class SynthesizerAgent:
    def __init__(self):
        print("✅ Agent Synthétiseur initialisé - génération de rapports PDF")
    
    def generate_report_pdf(self, candidate_data: dict, job_offer: dict, match_result: dict, questions: dict, output_path: str = None) -> str:
        """
        Génère un rapport PDF pour un candidat
        """
        if output_path is None:
            output_path = f"reports/cv_{candidate_data.get('id', uuid.uuid4().hex[:8])}.pdf"
        
        # Créer le dossier reports s'il n'existe pas
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "reports", exist_ok=True)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=30,
            alignment=0
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=20
        )
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=8
        )
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            spaceAfter=6
        )
        
        # Création du PDF
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # En-tête
        story.append(Paragraph("HireFlow - Rapport d'évaluation candidat", title_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a56db'), spaceAfter=20))
        
        # Date
        story.append(Paragraph(f"Date du rapport: {datetime.now().strftime('%d/%m/%Y à %H:%M')}", normal_style))
        story.append(Spacer(1, 10))
        
        # ========== 1. INFORMATIONS CANDIDAT ==========
        story.append(Paragraph("1. Informations du candidat", heading_style))
        
        candidate_info = [
            ["Nom:", candidate_data.get('name', 'Non spécifié')],
            ["Email:", candidate_data.get('email', 'Non spécifié')],
            ["Expérience:", f"{candidate_data.get('experience_years', 0)} ans"],
            ["Compétences:", ", ".join(candidate_data.get('skills', [])[:10]) if candidate_data.get('skills') else "Aucune compétence détectée"],
        ]
        
        info_table = Table(candidate_info, colWidths=[4*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        
        # ========== 2. RÉSULTAT DU MATCHING ==========
        story.append(Paragraph("2. Résultat du matching", heading_style))
        
        score = match_result.get('overall_score', 0)
        score_color = '#10b981' if score >= 75 else '#f59e0b' if score >= 50 else '#ef4444'
        
        score_table = [
            ["Score de compatibilité:", f"{score}%"],
            ["Statut:", match_result.get('status_label', 'Non évalué')],
            ["Justification:", match_result.get('justification', 'Aucune justification')],
        ]
        
        score_table_obj = Table(score_table, colWidths=[4*cm, 10*cm])
        score_table_obj.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor(score_color)),
            ('FONTWEIGHT', (1, 0), (1, 0), 'BOLD'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(score_table_obj)
        
        # ========== 3. ANALYSE DES COMPÉTENCES ==========
        story.append(Paragraph("3. Analyse des compétences", heading_style))
        
        skill_match = match_result.get('skill_match', {})
        matched_skills = skill_match.get('matched_skills', [])
        missing_skills = skill_match.get('missing_skills', [])
        
        if matched_skills:
            story.append(Paragraph(f"<b>✅ Compétences maîtrisées ({len(matched_skills)}) :</b>", subheading_style))
            story.append(Paragraph(", ".join(matched_skills), normal_style))
        
        if missing_skills:
            story.append(Paragraph(f"<b>⚠️ Compétences à développer ({len(missing_skills)}) :</b>", subheading_style))
            story.append(Paragraph(", ".join(missing_skills), normal_style))
        
        story.append(Spacer(1, 10))
        
        # Détail des scores par compétence
        skill_details = skill_match.get('details', [])
        if skill_details:
            story.append(Paragraph("<b>Détail des scores par compétence :</b>", subheading_style))
            detail_data = [["Compétence requise", "Score", "Statut"]]
            for sd in skill_details[:8]:
                status = "✅" if sd.get('score', 0) >= 70 else "⚠️" if sd.get('score', 0) >= 40 else "❌"
                detail_data.append([
                    sd.get('skill_requis', ''),
                    f"{sd.get('score', 0)}%",
                    status
                ])
            
            detail_table = Table(detail_data, colWidths=[6*cm, 3*cm, 2*cm])
            detail_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ]))
            story.append(detail_table)
        
        # ========== 4. QUESTIONS D'ENTRETIEN ==========
        story.append(Paragraph("4. Questions d'entretien recommandées", heading_style))
        
        questions_list = questions.get('questions', [])
        for idx, q in enumerate(questions_list[:6], 1):
            story.append(Paragraph(f"<b>{idx}. {q.get('question', '')}</b>", normal_style))
            story.append(Paragraph(f"<i>Pourquoi: {q.get('pourquoi', 'Évaluer la compétence')}</i>", normal_style))
            story.append(Spacer(1, 5))
        
        if questions.get('summary'):
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Résumé des axes d'évaluation :</b>", subheading_style))
            story.append(Paragraph(questions.get('summary', ''), normal_style))
        
        # ========== 5. RECOMMANDATION FINALE ==========
        story.append(Paragraph("5. Recommandation", heading_style))
        
        recommendation = match_result.get('recommendation', 'À évaluer')
        if score >= 75:
            rec_color = '#10b981'
            rec_icon = "✅"
        elif score >= 50:
            rec_color = '#f59e0b'
            rec_icon = "⚠️"
        else:
            rec_color = '#ef4444'
            rec_icon = "❌"
        
        story.append(Paragraph(f"{rec_icon} <font color='{rec_color}'><b>{recommendation}</b></font>", normal_style))
        
        # ========== 6. INFORMATIONS POSTE ==========
        story.append(Paragraph("6. Informations du poste", heading_style))
        
        job_info = [
            ["Poste:", job_offer.get('title', 'Non spécifié')],
            ["Expérience requise:", f"{job_offer.get('experience_years', 0)} ans"],
            ["Compétences requises:", ", ".join(job_offer.get('required_skills', []))],
        ]
        
        job_table = Table(job_info, colWidths=[4*cm, 10*cm])
        job_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4b5563')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(job_table)
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#d1d5db'), spaceAfter=10))
        story.append(Paragraph(
            f"<font size='8' color='#9ca3af'>Document généré par HireFlow - Pipeline de recrutement piloté par IA - {datetime.now().strftime('%d/%m/%Y')}</font>",
            normal_style
        ))
        
        # Générer le PDF
        doc.build(story)
        return output_path