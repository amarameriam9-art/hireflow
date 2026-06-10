# HireFlow - Plateforme de Recrutement pilotée par IA

![HireFlow](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.14-green)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)

## 📌 Description

HireFlow est une plateforme de recrutement innovante qui utilise 5 agents IA autonomes pour automatiser tout le pipeline de recrutement :

- **Analyse de CV** → Extraction automatique des compétences et expériences
- **Matching intelligent** → Scoring sémantique entre CV et offre d'emploi
- **Questions personnalisées** → Génération de questions d'entretien basées sur les gaps
- **Rapport PDF** → Export professionnel complet
- **Chat intelligent** → RAG pour interroger les CV en langage naturel

## 🎯 Fonctionnalités

| Module | Description |
|--------|-------------|
| 🔐 Authentification | JWT, inscription/connexion |
| 📄 Upload CV | Batch upload (PDF, DOCX, TXT) |
| 📊 Pipeline Kanban | Visualisation 3 colonnes |
| 👥 Gestion candidats | CRUD, sélection multiple, export CSV |
| 📅 Agenda entretiens | Planning, modification, emails automatiques |
| 📈 Analytics | Graphiques, top compétences, insights |
| 🌓 Mode sombre/clair | Interface adaptable |
| 💬 Chat IA | RAG pour questions intelligentes |

## 🛠️ Technologies

### Backend
- **FastAPI** - API REST
- **SQLite** - Base de données
- **JWT** - Auth# HireFlow - Plateforme de Recrutement pilotée par IA

![HireFlow](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/Python-3.14-green)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)

## 📌 Description

HireFlow est une plateforme de recrutement innovante qui utilise 5 agents IA autonomes pour automatiser tout le pipeline de recrutement :

- **Analyse de CV** → Extraction automatique des compétences et expériences
- **Matching intelligent** → Scoring sémantique entre CV et offre d'emploi
- **Questions personnalisées** → Génération de questions d'entretien basées sur les gaps
- **Rapport PDF** → Export professionnel complet
- **Chat intelligent** → RAG pour interroger les CV en langage naturel

## 🎯 Fonctionnalités

| Module | Description |
|--------|-------------|
| 🔐 Authentification | JWT, inscription/connexion |
| 📄 Upload CV | Batch upload (PDF, DOCX, TXT) |
| 📊 Pipeline Kanban | Visualisation 3 colonnes |
| 👥 Gestion candidats | CRUD, sélection multiple, export CSV |
| 📅 Agenda entretiens | Planning, modification, emails automatiques |
| 📈 Analytics | Graphiques, top compétences, insights |
| 🌓 Mode sombre/clair | Interface adaptable |
| 💬 Chat IA | RAG pour questions intelligentes |

## 🛠️ Technologies

### Backend
- **FastAPI** - API REST
- **SQLite** - Base de données
- **JWT** - Authentification
- **Sentence Transformers** - Embeddings sémantiques
- **ReportLab** - Génération PDF

### Frontend
- **React 18** - Framework UI
- **TailwindCSS** - Styling
- **Lucide React** - Icônes
- **Chart.js** - Graphiques

## 🚀 Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- Git

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000entification
- **Sentence Transformers** - Embeddings sémantiques
- **ReportLab** - Génération PDF

### Frontend
- **React 18** - Framework UI
- **TailwindCSS** - Styling
- **Lucide React** - Icônes
- **Chart.js** - Graphiques

## 🚀 Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- Git

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
