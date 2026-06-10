import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class Database:
    def __init__(self, db_path: str = "hireflow.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données avec toutes les tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    company TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des candidats
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS candidates (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    filename TEXT,
                    name TEXT,
                    email TEXT,
                    score REAL,
                    skills TEXT,
                    experience_years INTEGER,
                    status TEXT,
                    match_result TEXT,
                    interview_questions TEXT,
                    job_matched TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des offres d'emploi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_offer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    required_skills TEXT,
                    experience_years INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des textes CV pour le RAG
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cv_texts (
                    candidate_id TEXT PRIMARY KEY,
                    cv_text TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
                )
            ''')
            
            # Table des entretiens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interviews (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    candidate_id TEXT,
                    candidate_name TEXT,
                    date TEXT,
                    time TEXT,
                    duration INTEGER,
                    type TEXT,
                    status TEXT,
                    meeting_link TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                )
            ''')
            
            # Table des templates d'emails
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_templates (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    name TEXT,
                    subject TEXT,
                    body TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des emails programmés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    candidate_id TEXT,
                    template_id TEXT,
                    recipient_email TEXT,
                    subject TEXT,
                    body TEXT,
                    scheduled_date TEXT,
                    status TEXT,
                    sent_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Créer les index
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidates_user_id ON candidates(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interviews_user_id ON interviews(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_interviews_date ON interviews(date)')
            
            conn.commit()
            print("✅ Base de données initialisée")
    
    # ========== CANDIDATS ==========
    
    def save_candidate(self, candidate: Dict, user_id: str) -> bool:
        """Sauvegarde un candidat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO candidates 
                    (id, user_id, filename, name, email, score, skills, experience_years, status, match_result, interview_questions, job_matched, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    candidate.get("id"),
                    user_id,
                    candidate.get("filename", ""),
                    candidate.get("name", ""),
                    candidate.get("email", ""),
                    candidate.get("score"),
                    json.dumps(candidate.get("skills", [])),
                    candidate.get("experience_years", 0),
                    candidate.get("status", "pending"),
                    json.dumps(candidate.get("match_result", {})),
                    json.dumps(candidate.get("interview_questions", {})),
                    candidate.get("job_matched", "")
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur sauvegarde candidat: {e}")
            return False
    
    def get_all_candidates(self, user_id: str) -> List[Dict]:
        """Récupère tous les candidats d'un utilisateur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM candidates WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
                rows = cursor.fetchall()
                candidates = []
                for row in rows:
                    candidates.append({
                        "id": row[0],
                        "filename": row[2],
                        "name": row[3],
                        "email": row[4],
                        "score": row[5],
                        "skills": json.loads(row[6]) if row[6] else [],
                        "experience_years": row[7],
                        "status": row[8],
                        "match_result": json.loads(row[9]) if row[9] else {},
                        "interview_questions": json.loads(row[10]) if row[10] else {},
                        "job_matched": row[11],
                        "created_at": row[12],
                        "updated_at": row[13]
                    })
                return candidates
        except Exception as e:
            print(f"Erreur récupération candidats: {e}")
            return []
    
    def get_candidate(self, candidate_id: str, user_id: str) -> Optional[Dict]:
        """Récupère un candidat par son ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM candidates WHERE id = ? AND user_id = ?', (candidate_id, user_id))
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "filename": row[2],
                        "name": row[3],
                        "email": row[4],
                        "score": row[5],
                        "skills": json.loads(row[6]) if row[6] else [],
                        "experience_years": row[7],
                        "status": row[8],
                        "match_result": json.loads(row[9]) if row[9] else {},
                        "interview_questions": json.loads(row[10]) if row[10] else {},
                        "job_matched": row[11],
                        "created_at": row[12],
                        "updated_at": row[13]
                    }
                return None
        except Exception as e:
            print(f"Erreur récupération candidat: {e}")
            return None
    
    def delete_candidate(self, candidate_id: str, user_id: str) -> bool:
        """Supprime un candidat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM candidates WHERE id = ? AND user_id = ?', (candidate_id, user_id))
                cursor.execute('DELETE FROM cv_texts WHERE candidate_id = ?', (candidate_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur suppression candidat: {e}")
            return False
    
    def delete_all_candidates(self, user_id: str) -> int:
        """Supprime tous les candidats d'un utilisateur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM candidates WHERE user_id = ?', (user_id,))
                count = cursor.rowcount
                conn.commit()
                return count
        except Exception as e:
            print(f"Erreur suppression tous candidats: {e}")
            return 0
    
    # ========== CV TEXTS POUR RAG ==========
    
    def save_cv_text(self, candidate_id: str, cv_text: str) -> bool:
        """Sauvegarde le texte du CV pour le RAG"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO cv_texts (candidate_id, cv_text)
                    VALUES (?, ?)
                ''', (candidate_id, cv_text))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur sauvegarde CV text: {e}")
            return False
    
    def get_cv_text(self, candidate_id: str) -> Optional[str]:
        """Récupère le texte du CV"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT cv_text FROM cv_texts WHERE candidate_id = ?', (candidate_id,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            print(f"Erreur récupération CV text: {e}")
            return None
    
    # ========== OFFRE D'EMPLOI ==========
    
    def save_job_offer(self, title: str, required_skills: List[str], experience_years: int) -> bool:
        """Sauvegarde l'offre d'emploi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM job_offer')
                cursor.execute('''
                    INSERT INTO job_offer (title, required_skills, experience_years)
                    VALUES (?, ?, ?)
                ''', (title, json.dumps(required_skills), experience_years))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur sauvegarde offre: {e}")
            return False
    
    def get_job_offer(self) -> Optional[Dict]:
        """Récupère l'offre d'emploi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT title, required_skills, experience_years FROM job_offer ORDER BY id DESC LIMIT 1')
                row = cursor.fetchone()
                if row:
                    return {
                        "title": row[0],
                        "required_skills": json.loads(row[1]) if row[1] else [],
                        "experience_years": row[2]
                    }
                return None
        except Exception as e:
            print(f"Erreur récupération offre: {e}")
            return None
    
    # ========== ENTRETIENS ==========
    
    def save_interview(self, interview: Dict, user_id: str) -> bool:
        """Sauvegarde un entretien"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO interviews 
                    (id, user_id, candidate_id, candidate_name, date, time, duration, type, status, meeting_link, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interview.get("id"),
                    user_id,
                    interview.get("candidate_id"),
                    interview.get("candidate_name"),
                    interview.get("date"),
                    interview.get("time"),
                    interview.get("duration", 30),
                    interview.get("type", "video"),
                    interview.get("status", "scheduled"),
                    interview.get("meeting_link", ""),
                    interview.get("notes", "")
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur sauvegarde entretien: {e}")
            return False
    
    def get_all_interviews(self, user_id: str) -> List[Dict]:
        """Récupère tous les entretiens d'un utilisateur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM interviews WHERE user_id = ? ORDER BY date, time', (user_id,))
                rows = cursor.fetchall()
                interviews = []
                for row in rows:
                    interviews.append({
                        "id": row[0],
                        "candidate_id": row[2],
                        "candidate_name": row[3],
                        "date": row[4],
                        "time": row[5],
                        "duration": row[6],
                        "type": row[7],
                        "status": row[8],
                        "meeting_link": row[9],
                        "notes": row[10],
                        "created_at": row[11]
                    })
                return interviews
        except Exception as e:
            print(f"Erreur récupération entretiens: {e}")
            return []
    
    def update_interview(self, interview_id: str, user_id: str, interview: Dict) -> bool:
        """Met à jour un entretien"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE interviews 
                    SET date=?, time=?, duration=?, type=?, status=?, meeting_link=?, notes=?
                    WHERE id=? AND user_id=?
                ''', (
                    interview.get("date"),
                    interview.get("time"),
                    interview.get("duration"),
                    interview.get("type"),
                    interview.get("status"),
                    interview.get("meeting_link"),
                    interview.get("notes"),
                    interview_id,
                    user_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur mise à jour entretien: {e}")
            return False
    
    def delete_interview(self, interview_id: str, user_id: str) -> bool:
        """Supprime un entretien"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM interviews WHERE id = ? AND user_id = ?', (interview_id, user_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erreur suppression entretien: {e}")
            return False

# Instance globale
db = Database()