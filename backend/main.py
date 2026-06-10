from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import json
import sqlite3

# ========== IMPORT DES AGENTS ==========
from agents.parser_simple import SimpleParser
from agents.matcher import MatcherAgent
from agents.interviewer import InterviewerAgent
from agents.synthesizer import SynthesizerAgent
from agents.rag_agent import RAGAgent
from database import db
from auth import (
    UserCreate, UserLogin, authenticate_user, create_access_token,
    get_current_user, user_db
)

# ========== CRÉATION DE L'APPLICATION ==========
app = FastAPI(title="HireFlow API")

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== SECURITY ==========
security = HTTPBearer()

# ========== INITIALISATION ==========
parser = SimpleParser()
matcher = MatcherAgent()
interviewer = InterviewerAgent()
synthesizer = SynthesizerAgent()
rag_agent = RAGAgent()

# ========== STOCKAGE TEMPORAIRE (pour les contenus binaires) ==========
temp_storage = {}

# ========== MODÈLES ==========
class JobOffer(BaseModel):
    title: str
    required_skills: List[str]
    experience_years: int

class ChatRequest(BaseModel):
    question: str

class InterviewCreate(BaseModel):
    candidate_id: str
    candidate_name: str
    date: str
    time: str
    duration: int = 30
    type: str = "video"
    meeting_link: str = ""
    notes: str = ""

class InterviewUpdate(BaseModel):
    date: str
    time: str
    duration: int
    type: str
    status: str
    meeting_link: str
    notes: str

class EmailRequest(BaseModel):
    candidate_id: str
    subject: str
    body: str

# ========== DÉPENDANCE D'AUTHENTIFICATION ==========
async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    return user

# ========== CHARGEMENT DE L'OFFRE DEPUIS LA DB ==========
def load_job_offer():
    saved_offer = db.get_job_offer()
    if saved_offer:
        return saved_offer
    return {
        "title": "Lead Dev Full Stack",
        "required_skills": ["Python", "React", "AWS", "Docker", "PostgreSQL", "TypeScript"],
        "experience_years": 5
    }

current_job_offer = load_job_offer()

# ========== ENDPOINTS PUBLICS (sans authentification) ==========

@app.get("/")
def root():
    return {"message": "HireFlow API is running!", "status": "ok", "version": "1.5.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/auth/register")
async def register(user: UserCreate):
    existing_user = user_db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email")
    new_user = user_db.create_user(user)
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": new_user["id"], "email": new_user["email"], "name": new_user["name"], "company": new_user.get("company")}
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    user_data = authenticate_user(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user_data["id"], "email": user_data["email"], "name": user_data["name"], "company": user_data.get("company")}
    }

@app.post("/api/auth/logout")
async def logout():
    return {"message": "Déconnecté avec succès"}

@app.get("/api/auth/me")
async def get_me(user = Depends(get_current_user_from_token)):
    return {"id": user["id"], "email": user["email"], "name": user["name"], "company": user.get("company")}

# ========== ENDPOINTS PROTÉGÉS ==========

@app.post("/api/upload")
async def upload_cv(file: UploadFile = File(...), user = Depends(get_current_user_from_token)):
    content = await file.read()
    candidate_id = str(uuid.uuid4())[:8]
    temp_storage[candidate_id] = content
    candidate = {"id": candidate_id, "filename": file.filename, "status": "pending", "score": None, "skills": [], "name": None, "email": "", "experience_years": 0}
    db.save_candidate(candidate, user["id"])
    return {"candidate_id": candidate_id, "filename": file.filename, "message": "Fichier uploadé avec succès"}

@app.post("/api/upload-batch")
async def upload_batch(files: List[UploadFile] = File(...), user = Depends(get_current_user_from_token)):
    results = []
    for file in files:
        content = await file.read()
        candidate_id = str(uuid.uuid4())[:8]
        temp_storage[candidate_id] = content
        candidate = {"id": candidate_id, "filename": file.filename, "status": "pending", "score": None, "skills": [], "name": None, "email": "", "experience_years": 0}
        db.save_candidate(candidate, user["id"])
        results.append({"candidate_id": candidate_id, "filename": file.filename, "status": "queued"})
    return {"total": len(files), "queued": len(files), "candidates": results}

@app.post("/api/process/{candidate_id}")
async def process_candidate(candidate_id: str, user = Depends(get_current_user_from_token)):
    candidate_from_db = db.get_candidate(candidate_id, user["id"])
    if not candidate_from_db:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    content = temp_storage.get(candidate_id, b"")
    filename = candidate_from_db.get("filename", "")
    try:
        parsed_data = parser.parse(content, filename)
        cv_full_text = ""
        if filename.endswith('.txt'):
            try:
                cv_full_text = content.decode('utf-8', errors='ignore')
            except:
                cv_full_text = parsed_data.get("texte_complet", "")
        else:
            cv_full_text = parser.extract_text(content, filename)
        if not cv_full_text:
            cv_full_text = parsed_data.get("texte_complet", "")
        rag_agent.index_cv(candidate_id, cv_full_text, parsed_data)
        db.save_cv_text(candidate_id, cv_full_text)
        match_result = await matcher.match(parsed_data, current_job_offer)
        questions = interviewer.generate_questions(parsed_data, current_job_offer, match_result)
        candidate_from_db.update({
            "status": "completed", "score": match_result["overall_score"],
            "skills": parsed_data.get("competences", []),
            "name": parsed_data.get("nom", filename.split(".")[0]),
            "email": parsed_data.get("email", ""),
            "experience_years": match_result.get("experience_match", {}).get("experience_cv", 0),
            "match_result": match_result, "interview_questions": questions,
            "job_matched": current_job_offer["title"]
        })
        db.save_candidate(candidate_from_db, user["id"])
        if candidate_id in temp_storage:
            del temp_storage[candidate_id]
        return {
            "candidate_id": candidate_id, "score": match_result["overall_score"],
            "status_label": match_result["status_label"], "justification": match_result["justification"],
            "matched_skills": match_result["skill_match"]["matched_skills"],
            "missing_skills": match_result["skill_match"]["missing_skills"],
            "skills": parsed_data.get("competences", []),
            "name": parsed_data.get("nom", filename.split(".")[0]),
            "questions_count": len(questions.get("questions", [])), "status": "completed"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/process-all")
async def process_all_candidates(user = Depends(get_current_user_from_token)):
    all_candidates = db.get_all_candidates(user["id"])
    pending_ids = [c["id"] for c in all_candidates if c.get("status") == "pending"]
    results = []
    for cid in pending_ids:
        result = await process_candidate(cid, user)
        results.append(result)
    return {"processed": len(pending_ids), "results": results}

@app.get("/api/candidates")
async def list_candidates(user = Depends(get_current_user_from_token)):
    candidates = db.get_all_candidates(user["id"])
    clean_list = []
    for c in candidates:
        clean_list.append({
            "id": c.get("id"), "name": c.get("name"), "filename": c.get("filename"),
            "score": c.get("score"), "skills": c.get("skills", []), "status": c.get("status"),
            "experience_years": c.get("experience_years", 0),
            "questions_count": len(c.get("interview_questions", {}).get("questions", [])) if c.get("interview_questions") else 0,
            "email": c.get("email", ""), "created_at": c.get("created_at")
        })
    return clean_list

@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str, user = Depends(get_current_user_from_token)):
    candidate = db.get_candidate(candidate_id, user["id"])
    if not candidate:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    return candidate

@app.get("/api/candidates/{candidate_id}/questions")
async def get_interview_questions(candidate_id: str, user = Depends(get_current_user_from_token)):
    candidate = db.get_candidate(candidate_id, user["id"])
    if not candidate:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    if candidate.get("interview_questions"):
        return candidate["interview_questions"]
    cv_data = {"nom": candidate.get("name", ""), "competences": candidate.get("skills", []), "annees_experience": candidate.get("experience_years", 0)}
    match_result = candidate.get("match_result", {})
    questions = interviewer.generate_questions(cv_data, current_job_offer, match_result)
    candidate["interview_questions"] = questions
    db.save_candidate(candidate, user["id"])
    return questions

@app.get("/api/candidates/{candidate_id}/export-pdf")
async def export_candidate_pdf(candidate_id: str, user = Depends(get_current_user_from_token)):
    candidate = db.get_candidate(candidate_id, user["id"])
    if not candidate:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    candidate_data = {"id": candidate.get("id"), "name": candidate.get("name"), "email": candidate.get("email", "Non spécifié"),
                      "experience_years": candidate.get("experience_years", 0), "skills": candidate.get("skills", [])}
    match_result = candidate.get("match_result", {})
    interview_questions = candidate.get("interview_questions", {"questions": [], "summary": ""})
    pdf_path = synthesizer.generate_report_pdf(candidate_data=candidate_data, job_offer=current_job_offer,
                                                match_result=match_result, questions=interview_questions)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"rapport_{candidate.get('name', 'candidat').replace(' ', '_')}.pdf")

@app.post("/api/chat/{candidate_id}")
async def chat_with_candidate(candidate_id: str, request: ChatRequest, user = Depends(get_current_user_from_token)):
    candidate = db.get_candidate(candidate_id, user["id"])
    if not candidate:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    question = request.question
    if not question:
        return JSONResponse(status_code=400, content={"error": "Question vide"})
    cv_text = db.get_cv_text(candidate_id)
    if cv_text and candidate_id not in rag_agent.cv_texts:
        cv_data = {"nom": candidate.get("name", ""), "competences": candidate.get("skills", []), "annees_experience": candidate.get("experience_years", 0)}
        rag_agent.index_cv(candidate_id, cv_text, cv_data)
    search_result = rag_agent.search(candidate_id, question)
    answer = rag_agent.generate_answer(question, search_result)
    return {"answer": answer, "candidate_name": candidate.get("name", "Candidat")}

@app.delete("/api/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str, user = Depends(get_current_user_from_token)):
    if db.get_candidate(candidate_id, user["id"]):
        rag_agent.delete_cv(candidate_id)
        db.delete_candidate(candidate_id, user["id"])
        return {"message": "Candidat supprimé"}
    return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})

@app.delete("/api/candidates")
async def delete_all_candidates(user = Depends(get_current_user_from_token)):
    count = db.delete_all_candidates(user["id"])
    return {"message": f"{count} candidats supprimés"}

@app.get("/api/job-offer")
async def get_job_offer():
    return current_job_offer

@app.post("/api/job-offer")
async def update_job_offer(offer: JobOffer):
    global current_job_offer
    current_job_offer = offer.dict()
    db.save_job_offer(offer.title, offer.required_skills, offer.experience_years)
    return {"message": "Offre mise à jour", "offer": current_job_offer}

# ========== ENDPOINTS POUR LES ENTRETIENS ==========

@app.post("/api/interviews")
async def create_interview(interview: InterviewCreate, user = Depends(get_current_user_from_token)):
    interview_id = str(uuid.uuid4())[:8]
    interview_dict = interview.dict()
    interview_dict["id"] = interview_id
    interview_dict["status"] = "scheduled"
    db.save_interview(interview_dict, user["id"])
    return {"id": interview_id, "message": "Entretien créé"}

@app.get("/api/interviews")
async def get_interviews(user = Depends(get_current_user_from_token)):
    interviews = db.get_all_interviews(user["id"])
    return interviews

@app.put("/api/interviews/{interview_id}")
async def update_interview(interview_id: str, interview: InterviewUpdate, user = Depends(get_current_user_from_token)):
    db.update_interview(interview_id, user["id"], interview.dict())
    return {"message": "Entretien mis à jour"}

@app.delete("/api/interviews/{interview_id}")
async def delete_interview(interview_id: str, user = Depends(get_current_user_from_token)):
    db.delete_interview(interview_id, user["id"])
    return {"message": "Entretien supprimé"}

# ========== ENDPOINTS POUR LES EMAILS ==========

@app.post("/api/send-email")
async def send_email(email_data: EmailRequest, user = Depends(get_current_user_from_token)):
    candidate = db.get_candidate(email_data.candidate_id, user["id"])
    if not candidate:
        return JSONResponse(status_code=404, content={"error": "Candidat non trouvé"})
    # Simulation d'envoi d'email (à remplacer par un vrai service comme SendGrid, Resend, etc.)
    print(f"📧 Email envoyé à {candidate.get('email')}")
    print(f"   Sujet: {email_data.subject}")
    print(f"   Corps: {email_data.body}")
    return {"message": "Email envoyé avec succès"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)