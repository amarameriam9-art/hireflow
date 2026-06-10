import re
from typing import Dict
from pypdf import PdfReader
from docx import Document
from io import BytesIO

class SimpleParser:
    """Parseur amélioré avec extraction d'expérience"""
    
    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        text = ""
        try:
            if filename.lower().endswith('.pdf'):
                reader = PdfReader(BytesIO(file_bytes))
                for page in reader.pages:
                    text += page.extract_text() or ""
            elif filename.lower().endswith('.docx'):
                doc = Document(BytesIO(file_bytes))
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                text = file_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Erreur extraction: {e}")
        return text
    
    def extract_name(self, text: str) -> str:
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and len(line) < 50 and not any(x in line.lower() for x in ['comp', 'skill', 'exper', 'email', 'tel', 'cv', 'resume']):
                return line
        return "Candidat"
    
    def extract_email(self, text: str) -> str:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""
    
    def extract_experience_years(self, text: str) -> int:
        """Extrait le nombre d'années d'expérience de manière robuste"""
        text_lower = text.lower()
        
        # Patterns pour trouver l'expérience
        patterns = [
            # "7 ans d'expérience", "7 ans expérience", "7 ans"
            r'(\d+)\s*(?:ans|années|years?)(?:\s*(?:d\'|de\s+)?expérience?)?',
            r'expérience(?:\s*(?:professionnelle)?)?\s*:?\s*(\d+)\s*(?:ans|années)',
            r'experience(?:\s*(?:professionnelle)?)?\s*:?\s*(\d+)\s*(?:years?)',
            # "7+ ans", "7+ years"
            r'(\d+)\+\s*(?:ans|years?)',
            # Dans une phrase: "7 ans dans le domaine"
            r'(\d+)\s*(?:ans|années|years?)\s*(?:dans|en|de)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        # Chercher dans les bullet points d'expérience
        exp_lines = re.findall(r'(?:expérience|experience).*?(\d+).*?(?:ans|années|years?)', text_lower)
        if exp_lines:
            return int(exp_lines[0])
        
        return 0
    
    def extract_skills(self, text: str) -> list:
        skills_keywords = [
            "python", "java", "javascript", "react", "vue", "angular",
            "sql", "mysql", "postgresql", "mongodb", "docker", "kubernetes",
            "aws", "azure", "gcp", "git", "agile", "scrum", "typescript",
            "node.js", "django", "flask", "spring", "html", "css", "php",
            "ruby", "go", "rust", "c++", "c#", "swift", "kotlin", "terraform",
            "jenkins", "gitlab", "github", "jira", "confluence", "figma"
        ]
        found_skills = []
        text_lower = text.lower()
        for skill in skills_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.append(skill)
        return list(set(found_skills))
    
    def parse(self, file_bytes: bytes, filename: str) -> Dict:
        text = self.extract_text(file_bytes, filename)
        
        if not text:
            return {
                "nom": "Inconnu",
                "email": "",
                "competences": [],
                "annees_experience": 0,
                "erreur": "Impossible de lire le fichier"
            }
        
        return {
            "nom": self.extract_name(text),
            "email": self.extract_email(text),
            "competences": self.extract_skills(text),
            "annees_experience": self.extract_experience_years(text)
        }