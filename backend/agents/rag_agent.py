import re
import json
import os
from typing import List, Dict
import uuid

class RAGAgent:
    def __init__(self):
        # Version simplifiée - recherche par mots-clés
        print("✅ Agent RAG initialisé - version légère (recherche par mots-clés)")
        
        # Stockage des textes de CV
        self.cv_texts = {}
        
        # Mots-clés pour la recherche sémantique
        self.synonyms = {
            "expérience": ["experience", "ans", "années", "travaillé", "poste", "mission"],
            "compétence": ["competence", "skill", "technologie", "maîtrise", "connais"],
            "management": ["lead", "manager", "encadré", "équipe", "team", "responsable", "coordinateur", "chef"],
            "projet": ["project", "réalisation", "mission", "développé", "créé", "implementé"],
            "formation": ["diplôme", "diplome", "école", "université", "master", "bachelor", "licence", "bac"],
            "python": ["python", "django", "flask", "data"],
            "react": ["react", "redux", "frontend", "javascript"],
            "aws": ["aws", "amazon", "cloud", "ec2", "s3"],
            "docker": ["docker", "container", "kubernetes", "k8s"],
            "sql": ["sql", "postgresql", "mysql", "base de données", "database"]
        }
    
    def index_cv(self, candidate_id: str, cv_text: str, cv_data: Dict):
        """Indexe le CV dans la mémoire"""
        self.cv_texts[candidate_id] = {
            "text": cv_text,
            "data": cv_data,
            "chunks": self._chunk_text(cv_text)
        }
        print(f"✅ CV indexé pour {candidate_id} - {len(self.cv_texts[candidate_id]['chunks'])} chunks")
    
    def _chunk_text(self, text: str, chunk_size: int = 800) -> List[str]:
        """Découpe le texte en chunks"""
        text = re.sub(r'\s+', ' ', text)
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        
        return chunks if chunks else [text[:500]]
    
    def search(self, candidate_id: str, question: str, top_k: int = 3) -> Dict:
        """Recherche par mots-clés dans le CV"""
        if candidate_id not in self.cv_texts:
            return {"found": False, "passages": [], "candidate_data": {}}
        
        cv_data = self.cv_texts[candidate_id]
        question_lower = question.lower()
        
        # Extraire les mots-clés importants de la question
        keywords = self._extract_keywords(question_lower)
        
        # Rechercher dans les chunks
        passages = []
        for chunk in cv_data["chunks"]:
            chunk_lower = chunk.lower()
            score = 0
            
            for kw in keywords:
                if kw in chunk_lower:
                    score += 1
                # Vérifier les synonymes
                if kw in self.synonyms:
                    for syn in self.synonyms[kw]:
                        if syn in chunk_lower:
                            score += 0.5
            
            if score > 0:
                passages.append({
                    "text": chunk,
                    "score": score,
                    "metadata": {"candidate_id": candidate_id}
                })
        
        # Trier par score
        passages.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "found": len(passages) > 0,
            "passages": passages[:top_k],
            "candidate_data": cv_data["data"]
        }
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extrait les mots-clés importants de la question"""
        # Mots vides à ignorer
        stop_words = {'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'ou', 'pour', 'dans', 'sur', 'avec', 'par', 'est', 'sont', 'a', 'au', 'aux', 'ce', 'ces', 'cet', 'cette', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on', 'with', 'by', 'is', 'are', 'to', 'que', 'qui', 'quoi', 'dont', 'où', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles'}
        
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def generate_answer(self, question: str, search_result: Dict) -> str:
        """Génère une réponse basée sur les passages trouvés"""
        if not search_result["found"]:
            return self._generate_fallback_answer(question, search_result["candidate_data"])
        
        passages = search_result["passages"]
        candidate_data = search_result["candidate_data"]
        question_lower = question.lower()
        
        # Analyser le type de question
        if any(word in question_lower for word in ["expérience", "experience", "ans", "années"]):
            exp_years = candidate_data.get("annees_experience", 0)
            if exp_years > 0:
                return f"✅ **{exp_years} ans d'expérience**\n\nD'après le CV de {candidate_data.get('nom', 'le candidat')}, il/elle possède {exp_years} ans d'expérience professionnelle.\n\n📄 Extrait: {passages[0]['text'][:300]}..."
            else:
                return self._extract_info_from_passage(passages, "expérience")
        
        elif any(word in question_lower for word in ["compétence", "competence", "sait", "maîtrise", "technologie"]):
            skills = candidate_data.get("competences", [])
            if skills:
                return f"✅ **Compétences détectées**\n\n{', '.join(skills[:8])}\n\n📄 Extrait: {passages[0]['text'][:300]}..."
            else:
                return self._extract_info_from_passage(passages, "compétences")
        
        elif any(word in question_lower for word in ["management", "manager", "lead", "encadré", "équipe"]):
            return self._check_management_from_passage(passages)
        
        elif any(word in question_lower for word in ["formation", "diplôme", "diplome", "école", "université"]):
            return self._extract_education_from_passage(passages)
        
        elif any(word in question_lower for word in ["projet", "project", "réalisé", "mission"]):
            return self._extract_project_from_passage(passages)
        
        else:
            return self._extract_info_from_passage(passages, "la question")
    
    def _extract_info_from_passage(self, passages: List[Dict], topic: str) -> str:
        """Extrait des informations des passages"""
        if not passages:
            return f"❌ Je n'ai pas trouvé d'informations sur {topic} dans le CV."
        
        return f"📄 **Information trouvée dans le CV:**\n\n{passages[0]['text'][:500]}..."
    
    def _check_management_from_passage(self, passages: List[Dict]) -> str:
        """Vérifie l'expérience en management"""
        if not passages:
            return "❌ Le CV ne mentionne pas explicitement d'expérience en management."
        
        # Chercher des mots-clés de management
        management_keywords = ["lead", "manager", "encadré", "équipe", "responsable"]
        found = []
        for kw in management_keywords:
            if kw in passages[0]['text'].lower():
                found.append(kw)
        
        if found:
            return f"✅ **Expérience en management détectée**\n\nMots-clés trouvés: {', '.join(found)}\n\n📄 Extrait: {passages[0]['text'][:400]}..."
        else:
            return f"📄 **Extrait du CV:**\n\n{passages[0]['text'][:400]}..."
    
    def _extract_education_from_passage(self, passages: List[Dict]) -> str:
        """Extrait la formation"""
        if not passages:
            return "❌ Je n'ai pas trouvé d'informations sur la formation."
        
        education_keywords = ["master", "bachelor", "licence", "diplôme", "université", "école"]
        found = [kw for kw in education_keywords if kw in passages[0]['text'].lower()]
        
        if found:
            return f"✅ **Formation détectée**\n\nMots-clés: {', '.join(found)}\n\n📄 Extrait: {passages[0]['text'][:400]}..."
        else:
            return f"📄 **Extrait du CV:**\n\n{passages[0]['text'][:400]}..."
    
    def _extract_project_from_passage(self, passages: List[Dict]) -> str:
        """Extrait les projets"""
        if not passages:
            return "❌ Je n'ai pas trouvé d'informations sur les projets."
        
        return f"📄 **Extrait concernant les projets:**\n\n{passages[0]['text'][:500]}..."
    
    def _generate_fallback_answer(self, question: str, candidate_data: Dict) -> str:
        """Génère une réponse quand rien n'est trouvé"""
        name = candidate_data.get('nom', 'le candidat')
        skills = candidate_data.get('competences', [])
        
        if skills:
            return f"❓ Je n'ai pas trouvé d'information spécifique sur cette question.\n\n**Ce que je sais sur {name}:**\n• Compétences: {', '.join(skills[:5])}\n• Expérience: {candidate_data.get('annees_experience', 0)} ans\n\nPouvez-vous reformuler votre question ?"
        
        return f"❓ Je n'ai pas trouvé d'information spécifique sur cette question dans le CV de {name}. Voulez-vous poser une autre question ?"
    
    def delete_cv(self, candidate_id: str):
        """Supprime un CV de l'index"""
        if candidate_id in self.cv_texts:
            del self.cv_texts[candidate_id]
            print(f"🗑️ CV supprimé de l'index: {candidate_id}")