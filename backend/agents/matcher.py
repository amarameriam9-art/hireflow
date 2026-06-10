import numpy as np
from typing import Dict, List
import re

class MatcherAgent:
    def __init__(self):
        # Version simplifiée - utilise des mots-clés et similarité basique
        print("✅ Agent Matcher initialisé (version légère)")
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text
    
    def compute_keyword_overlap(self, text1: str, text2: str) -> float:
        """Calcule le chevauchement de mots-clés"""
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def compute_skill_match(self, cv_skills: List[str], job_skills: List[str]) -> Dict:
        """Calcule le match entre les compétences"""
        skill_scores = []
        matched_skills = []
        missing_skills = []
        
        for job_skill in job_skills:
            job_skill_norm = self.normalize_text(job_skill)
            best_score = 0
            best_match = ""
            
            for cv_skill in cv_skills:
                cv_skill_norm = self.normalize_text(cv_skill)
                
                # Vérifier correspondance exacte ou partielle
                if job_skill_norm == cv_skill_norm:
                    score = 1.0
                elif job_skill_norm in cv_skill_norm or cv_skill_norm in job_skill_norm:
                    score = 0.8
                else:
                    # Vérifier les mots communs
                    words_job = set(job_skill_norm.split())
                    words_cv = set(cv_skill_norm.split())
                    common = words_job.intersection(words_cv)
                    if common:
                        score = 0.5 * (len(common) / max(len(words_job), 1))
                    else:
                        score = 0.0
                
                if score > best_score:
                    best_score = score
                    best_match = cv_skill
            
            score_percent = round(best_score * 100, 1)
            skill_scores.append({
                "skill_requis": job_skill,
                "skill_trouve": best_match if best_score > 0.3 else None,
                "score": score_percent
            })
            
            if best_score >= 0.6:
                matched_skills.append(job_skill)
            else:
                missing_skills.append(job_skill)
        
        avg_skill_score = np.mean([s['score'] for s in skill_scores]) if skill_scores else 0
        
        return {
            "skill_scores": skill_scores,
            "avg_skill_score": round(avg_skill_score, 1),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_rate": round(len(matched_skills) / len(job_skills) * 100, 1) if job_skills else 0
        }
    
    def compute_experience_match(self, cv_exp: int, job_exp: int) -> Dict:
        """Calcule le match sur l'expérience"""
        if cv_exp >= job_exp:
            exp_score = 100
            exp_level = "excellent"
        elif cv_exp > 0:
            exp_score = round((cv_exp / job_exp) * 100, 1) if job_exp > 0 else 50
            exp_level = "acceptable" if exp_score >= 60 else "insuffisant"
        else:
            exp_score = 0
            exp_level = "insuffisant"
        
        return {
            "experience_cv": cv_exp,
            "experience_requise": job_exp,
            "score": exp_score,
            "niveau": exp_level
        }
    
    async def match(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Compare un CV avec une offre d'emploi"""
        
        cv_skills = [s.lower() for s in cv_data.get('competences', [])]
        cv_exp = cv_data.get('annees_experience', 0)
        
        job_skills = job_data.get('required_skills', [])
        job_exp = job_data.get('experience_years', 0)
        job_title = job_data.get('title', 'Poste')
        
        # 1. Match des compétences (poids 60%)
        skill_match = self.compute_skill_match(cv_skills, job_skills)
        
        # 2. Match de l'expérience (poids 30%)
        exp_match = self.compute_experience_match(cv_exp, job_exp)
        
        # 3. Match du titre (poids 10%)
        title_score = self.compute_keyword_overlap(job_title, cv_data.get('nom', '')) * 100
        
        # Score final pondéré
        overall_score = round(
            (skill_match['avg_skill_score'] * 0.6) +
            (exp_match['score'] * 0.3) +
            (title_score * 0.1), 1
        )
        
        # Déterminer le statut
        if overall_score >= 75:
            status = "preselected"
            status_label = "Présélectionné"
        elif overall_score >= 50:
            status = "interview"
            status_label = "À interviewer"
        else:
            status = "rejected"
            status_label = "Refusé"
        
        # Générer la justification
        justification = self.generate_justification(skill_match, exp_match)
        
        return {
            "overall_score": overall_score,
            "status": status,
            "status_label": status_label,
            "justification": justification,
            "skill_match": {
                "score": skill_match['avg_skill_score'],
                "match_rate": skill_match['match_rate'],
                "matched_skills": skill_match['matched_skills'],
                "missing_skills": skill_match['missing_skills'],
                "details": skill_match['skill_scores']
            },
            "experience_match": exp_match,
            "recommendation": self.get_recommendation(overall_score, skill_match, exp_match)
        }
    
    def generate_justification(self, skill_match: Dict, exp_match: Dict) -> str:
        """Génère une justification textuelle"""
        parts = []
        
        if skill_match['match_rate'] >= 70:
            parts.append(f"✅ {skill_match['match_rate']}% des compétences maîtrisées")
        elif skill_match['match_rate'] >= 50:
            parts.append(f"⚠️ {skill_match['match_rate']}% des compétences maîtrisées")
        else:
            parts.append(f"❌ {skill_match['match_rate']}% des compétences maîtrisées")
        
        if exp_match['niveau'] == "excellent":
            parts.append(f"✅ {exp_match['experience_cv']} ans d'expérience")
        elif exp_match['niveau'] == "acceptable":
            parts.append(f"⚠️ {exp_match['experience_cv']} ans d'expérience")
        else:
            parts.append(f"❌ Expérience: {exp_match['experience_cv']} ans requis: {exp_match['experience_requise']}")
        
        if skill_match['missing_skills']:
            parts.append(f"📚 Manque: {', '.join(skill_match['missing_skills'][:3])}")
        
        return " | ".join(parts)
    
    def get_recommendation(self, overall_score: float, skill_match: Dict, exp_match: Dict) -> str:
        """Génère une recommandation"""
        if overall_score >= 85:
            return "Candidat excellent - À convoquer en entretien prioritaire"
        elif overall_score >= 75:
            return "Bon candidat - À convoquer en entretien"
        elif overall_score >= 60:
            return "Candidat potentiel - À étudier"
        elif overall_score >= 50:
            return "Candidat à surveiller"
        else:
            return "Candidat non recommandé pour ce poste"