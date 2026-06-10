import random
from typing import Dict, List

class InterviewerAgent:
    def __init__(self):
        print("✅ Agent Interviewer initialisé - génération de questions personnalisées")
    
    def generate_questions(self, cv_data: Dict, job_data: Dict, match_result: Dict) -> Dict:
        """
        Génère des questions d'entretien PERSONNALISÉES basées sur:
        - Les compétences manquantes du candidat
        - Les compétences existantes à approfondir
        - L'expérience du candidat vs requise
        - Le niveau du poste
        """
        
        # Extraire les données
        missing_skills = match_result.get("skill_match", {}).get("missing_skills", [])
        matched_skills = match_result.get("skill_match", {}).get("matched_skills", [])
        exp_level = match_result.get("experience_match", {}).get("niveau", "acceptable")
        cv_exp = cv_data.get("annees_experience", 0)
        job_exp = job_data.get("experience_years", 5)
        job_title = job_data.get("title", "")
        cv_skills = cv_data.get("competences", [])
        
        all_questions = []
        
        # ============================================================
        # 1. QUESTIONS SUR LES COMPÉTENCES MANQUANTES (PERSONNALISÉES)
        # ============================================================
        for skill in missing_skills[:3]:
            question = self._generate_missing_skill_question(skill, job_title)
            all_questions.append({
                "question": question,
                "cible": skill,
                "categorie": "technique_manquante",
                "pourquoi": f"Compétence clé pour le poste non détectée dans votre CV",
                "niveau_importance": "élevée"
            })
        
        # ============================================================
        # 2. QUESTIONS D'APPROFONDISSEMENT SUR COMPÉTENCES EXISTANTES
        # ============================================================
        for skill in matched_skills[:3]:
            question = self._generate_deep_question(skill, cv_exp, job_title)
            all_questions.append({
                "question": question,
                "cible": skill,
                "categorie": "technique_approfondissement",
                "pourquoi": f"Pour évaluer votre niveau réel sur {skill}",
                "niveau_importance": "moyenne"
            })
        
        # ============================================================
        # 3. QUESTIONS SUR L'EXPÉRIENCE (PERSONNALISÉES)
        # ============================================================
        if exp_level == "insuffisant":
            question = f"Vous avez {cv_exp} ans d'expérience, alors que {job_exp} ans sont généralement requis pour ce poste. Quelles sont vos réalisations qui pourraient compenser ce gap d'expérience ?"
            all_questions.append({
                "question": question,
                "cible": "experience",
                "categorie": "comportementale",
                "pourquoi": f"Votre expérience ({cv_exp} ans) est inférieure à l'exigence ({job_exp} ans)",
                "niveau_importance": "élevée"
            })
        else:
            question = self._generate_experience_question(cv_exp, cv_skills, job_title)
            all_questions.append({
                "question": question,
                "cible": "experience",
                "categorie": "comportementale",
                "pourquoi": f"Pour valider la profondeur de votre expérience de {cv_exp} ans",
                "niveau_importance": "moyenne"
            })
        
        # ============================================================
        # 4. QUESTIONS DE MISE EN SITUATION (CONTEXTE DU POSTE)
        # ============================================================
        situation_questions = self._generate_situation_questions(job_title, cv_exp, missing_skills)
        for sq in situation_questions[:2]:
            all_questions.append(sq)
        
        # ============================================================
        # 5. QUESTION SUR LA MOTIVATION (PERSONNALISÉE)
        # ============================================================
        motivation_q = {
            "question": f"Pourquoi postulez-vous spécifiquement pour ce poste de {job_title} ? Qu'est-ce qui vous attire dans cette mission ?",
            "cible": "motivation",
            "categorie": "comportementale",
            "pourquoi": "Évaluer l'adéquation du candidat avec le poste et l'entreprise",
            "niveau_importance": "moyenne"
        }
        all_questions.append(motivation_q)
        
        # Mélanger pour un ordre naturel, mais garder les prioritaires en haut
        high_priority = [q for q in all_questions if q.get("niveau_importance") == "élevée"]
        other_questions = [q for q in all_questions if q.get("niveau_importance") != "élevée"]
        random.shuffle(other_questions)
        
        final_questions = high_priority + other_questions[:5]
        
        # Générer le résumé personnalisé
        summary = self._generate_personalized_summary(missing_skills, matched_skills, exp_level, cv_exp, job_exp)
        
        return {
            "questions": final_questions[:6],
            "summary": summary,
            "candidate_profile": {
                "missing_skills": missing_skills,
                "matched_skills": matched_skills,
                "experience_gap": job_exp - cv_exp if cv_exp < job_exp else 0
            }
        }
    
    def _generate_missing_skill_question(self, skill: str, job_title: str) -> str:
        """Génère une question personnalisée pour une compétence manquante"""
        
        questions_by_skill = {
            "python": f"Le poste de {job_title} nécessite Python. Pouvez-vous me parler d'un projet Python que vous avez mené ?",
            "react": f"React est essentiel pour ce poste. Décrivez votre expérience avec React et les hooks que vous utilisez.",
            "aws": f"Quelle est votre expérience avec AWS ? Quels services avez-vous utilisés en production ?",
            "docker": f"Comment construisez-vous et optimisez-vous des images Docker pour la production ?",
            "kubernetes": f"Avez-vous déployé des applications sur Kubernetes ? Décrivez le processus.",
            "postgresql": f"Comment optimisez-vous les requêtes PostgreSQL ? Connaissez-vous les index et les partitions ?",
            "typescript": f"Quels sont les avantages de TypeScript et comment l'utilisez-vous dans vos projets ?",
            "nodejs": f"Comment gérez-vous l'asynchrone en Node.js ? Parlez-moi des promesses et async/await.",
            "vue": f"Quelle est votre expérience avec Vue.js ? Parlez-moi du système de réactivité.",
            "mongodb": f"Comment modélisez-vous les données dans MongoDB ? Quels index utilisez-vous ?",
            "java": f"Décrivez votre expérience Java. Connaissez-vous les streams et les lambdas ?",
            "git": f"Comment gérez-vous les branches Git dans une équipe ? Parlez-moi de votre workflow Git.",
            "ci/cd": f"Quelle est votre expérience avec les pipelines CI/CD ? Quels outils utilisez-vous ?"
        }
        
        if skill.lower() in questions_by_skill:
            return questions_by_skill[skill.lower()]
        
        return f"Le poste de {job_title} requiert {skill}. Pouvez-vous nous parler de votre expérience avec cette technologie ?"
    
    def _generate_deep_question(self, skill: str, cv_exp: int, job_title: str) -> str:
        """Génère une question d'approfondissement pour une compétence existante"""
        
        deep_questions = {
            "python": f"Avec {cv_exp} ans d'expérience en Python, quel a été votre projet le plus complexe ? Quels défis avez-vous rencontrés ?",
            "react": f"Comment gérez-vous l'état global dans une application React complexe ? (Redux, Context, Zustand ?)",
            "aws": f"Comment assurez-vous la sécurité et la haute disponibilité sur AWS ?",
            "docker": f"Quelles bonnes pratiques suivez-vous pour vos Dockerfiles ? Comment réduisez-vous la taille des images ?",
            "javascript": f"Parlez-moi des différences entre var, let et const. Comment gérez-vous l'asynchrone ?",
            "typescript": f"Comment utilisez-vous les types avancés TypeScript (generics, utility types) ?",
            "sql": f"Comment gérez-vous les performances SQL sur de gros volumes de données ?"
        }
        
        if skill.lower() in deep_questions:
            return deep_questions[skill.lower()]
        
        return f"Vous maîtrisez {skill}. Quel est le projet le plus complexe que vous avez réalisé avec cette compétence ?"
    
    def _generate_experience_question(self, cv_exp: int, skills: List[str], job_title: str) -> str:
        """Génère une question sur l'expérience personnalisée"""
        if cv_exp >= 8:
            return f"Avec {cv_exp} ans d'expérience, vous avez probablement encadré des équipes. Parlez-moi de votre expérience en management technique."
        elif cv_exp >= 5:
            top_skill = skills[0] if skills else "développement"
            return f"Vous avez {cv_exp} ans d'expérience dont {skills[0] if skills else 'développement'}. Décrivez-nous un projet dont vous êtes particulièrement fier."
        else:
            return f"Avec {cv_exp} ans d'expérience, comment avez-vous acquis vos compétences techniques ? Quel est votre rythme d'apprentissage ?"
    
    def _generate_situation_questions(self, job_title: str, cv_exp: int, missing_skills: List[str]) -> List[Dict]:
        """Génère des questions de mise en situation basées sur le contexte"""
        questions = []
        
        # Leadership pour postes seniors
        if "lead" in job_title.lower() or cv_exp >= 5:
            questions.append({
                "question": "Avez-vous déjà encadré des développeurs juniors ? Comment abordez-vous le mentorat et la montée en compétence ?",
                "cible": "leadership",
                "categorie": "mise_en_situation",
                "pourquoi": "Le poste nécessite des compétences d'encadrement",
                "niveau_importance": "élevée"
            })
        
        # Gestion de crise
        questions.append({
            "question": "Décrivez une situation où un projet était en retard. Comment avez-vous réagi et quelles actions avez-vous menées ?",
            "cible": "gestion_crise",
            "categorie": "mise_en_situation",
            "pourquoi": "Évaluer la gestion du stress et des priorités",
            "niveau_importance": "moyenne"
        })
        
        # Apprentissage si compétences manquantes
        if missing_skills:
            questions.append({
                "question": f"Ce poste nécessite {', '.join(missing_skills[:2])} que vous ne maîtrisez pas encore. Comment comptez-vous acquérir ces compétences ?",
                "cible": "apprentissage",
                "categorie": "mise_en_situation",
                "pourquoi": "Évaluer la capacité d'apprentissage et l'autonomie",
                "niveau_importance": "élevée"
            })
        
        # Conflit
        questions.append({
            "question": "Comment gérez-vous un désaccord technique avec un collègue plus expérimenté ?",
            "cible": "conflit",
            "categorie": "mise_en_situation",
            "pourquoi": "Évaluer les compétences relationnelles",
            "niveau_importance": "moyenne"
        })
        
        return questions
    
    def _generate_personalized_summary(self, missing_skills: List[str], matched_skills: List[str], exp_level: str, cv_exp: int, job_exp: int) -> str:
        """Génère un résumé personnalisé pour le recruteur"""
        
        summary = "🎯 **AXES D'ÉVALUATION PRIORITAIRES**\n\n"
        
        if missing_skills:
            summary += f"**🔴 Compétences à vérifier en priorité:**\n"
            for skill in missing_skills[:3]:
                summary += f"   • {skill} (non détecté dans le CV)\n"
            summary += "\n"
        
        if matched_skills:
            summary += f"**🟢 Compétences à approfondir:**\n"
            for skill in matched_skills[:3]:
                summary += f"   • {skill} (présent dans le CV - vérifier le niveau réel)\n"
            summary += "\n"
        
        if exp_level == "insuffisant":
            summary += f"**⚠️ Expérience:** {cv_exp} ans (requis: {job_exp} ans) - Vérifier si l'expérience compense le gap\n\n"
        elif cv_exp > job_exp:
            summary += f"**✅ Expérience:** {cv_exp} ans (excellent - au-delà des {job_exp} ans requis)\n\n"
        
        summary += "**📋 Points à vérifier en entretien:**\n"
        summary += "   • Capacité d'apprentissage et autonomie\n"
        summary += "   • Travail en équipe et communication\n"
        summary += "   • Résolution de problèmes complexes\n"
        
        return summary