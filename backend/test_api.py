import requests
import json

# Tester l'API avec un fichier CV factice
files = {
    'file': ('test_cv.txt', """
    Nom: Jean Martin
    Email: jean.martin@email.com
    
    COMPÉTENCES:
    - Python (3 ans)
    - React (2 ans)
    - SQL (4 ans)
    - Docker (1 an)
    
    EXPÉRIENCES:
    - Développeur Full Stack chez TechCorp (2022-2024): Développement d'applications web avec Python/Django et React
    - Data Analyst chez DataCo (2020-2022): Analyse de données avec SQL et Python
    
    FORMATIONS:
    - Master Informatique, Université Paris-Saclay, 2020
    
    ANNÉES EXPÉRIENCE: 4
    """)
}

data = {
    'job_title': 'Développeur Full Stack Senior',
    'job_skills': 'Python, React, PostgreSQL, Docker, AWS',
    'job_exp': 3
}

response = requests.post('http://localhost:8000/api/process-cv', files=files, data=data)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))