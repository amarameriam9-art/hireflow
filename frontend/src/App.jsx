import React, { useState, useEffect } from 'react';
import { 
  Upload, Users, LayoutDashboard, MessageSquare, Settings, BarChart3,
  CheckCircle, Clock, XCircle, TrendingUp, Briefcase, FileText,
  Sparkles, ArrowRight, Search, Filter, Download, Trash2,
  Zap, Star, Award, Target, Brain, Send, Menu, ChevronRight,
  AlertCircle, UserCheck, Activity, Cpu, Database, Code, GitBranch,
  Plus, Trash, HelpCircle, Sun, Moon, LogOut, Calendar
} from 'lucide-react';
import Login from './components/Login';

function App() {
  // Authentification
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const token = localStorage.getItem('token');
    return !!token;
  });
  const [currentUser, setCurrentUser] = useState(() => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  });

  const [activeTab, setActiveTab] = useState('pipeline');
  const [candidates, setCandidates] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState([]);
  const [backendStatus, setBackendStatus] = useState('connected');
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatResponse, setChatResponse] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Mode sombre/clair
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved !== null ? saved === 'true' : true;
  });
  
  // État pour les questions d'entretien
  const [interviewQuestions, setInterviewQuestions] = useState(null);
  const [showQuestionsModal, setShowQuestionsModal] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  
  // État pour l'offre d'emploi
  const [jobOffer, setJobOffer] = useState({
    title: "Lead Dev Full Stack",
    required_skills: ["Python", "React", "AWS", "Docker", "PostgreSQL", "TypeScript"],
    experience_years: 5
  });
  const [newSkill, setNewSkill] = useState("");
  const [savingOffer, setSavingOffer] = useState(false);
  const [offerMessage, setOfferMessage] = useState("");

  // Fonction pour les appels API authentifiés
  const authFetch = async (url, options = {}) => {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }
    return fetch(url, { ...options, headers });
  };

  // Sauvegarder la préférence du mode
  useEffect(() => {
    localStorage.setItem('darkMode', darkMode);
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchCandidates();
      fetchJobOffer();
      checkBackendStatus();
    }
  }, [isAuthenticated]);

  const checkBackendStatus = async () => {
    try {
      const response = await authFetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    } catch (error) {
      setBackendStatus('disconnected');
    }
  };

  const fetchCandidates = async () => {
    try {
      const response = await authFetch('http://localhost:8000/api/candidates');
      if (response.ok) {
        const data = await response.json();
        setCandidates(data);
      } else {
        setCandidates([]);
      }
    } catch (error) {
      console.error("Erreur chargement candidats:", error);
      setCandidates([]);
    }
  };

  const fetchJobOffer = async () => {
    try {
      const response = await authFetch('http://localhost:8000/api/job-offer');
      if (response.ok) {
        const data = await response.json();
        setJobOffer(data);
      }
    } catch (error) {
      console.log("Backend non disponible, offre par défaut");
    }
  };

  const saveJobOffer = async () => {
    setSavingOffer(true);
    setOfferMessage("");
    try {
      const response = await authFetch('http://localhost:8000/api/job-offer', {
        method: 'POST',
        body: JSON.stringify(jobOffer)
      });
      if (response.ok) {
        setOfferMessage("✅ Offre mise à jour avec succès !");
        setTimeout(() => setOfferMessage(""), 3000);
      } else {
        setOfferMessage("❌ Erreur lors de la sauvegarde");
      }
    } catch (error) {
      setOfferMessage("❌ Impossible de contacter le backend");
    } finally {
      setSavingOffer(false);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !jobOffer.required_skills.includes(newSkill.trim())) {
      setJobOffer({
        ...jobOffer,
        required_skills: [...jobOffer.required_skills, newSkill.trim()]
      });
      setNewSkill("");
    }
  };

  const removeSkill = (skillToRemove) => {
    setJobOffer({
      ...jobOffer,
      required_skills: jobOffer.required_skills.filter(s => s !== skillToRemove)
    });
  };

  const deleteCandidate = async (candidateId, event) => {
    if (event) event.stopPropagation();
    if (confirm('Êtes-vous sûr de vouloir supprimer ce candidat ?')) {
      try {
        const response = await authFetch(`http://localhost:8000/api/candidates/${candidateId}`, {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchCandidates();
          if (selectedCandidate && selectedCandidate.id === candidateId) {
            setSelectedCandidate(null);
            setChatResponse('');
          }
        }
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
      }
    }
  };

  const deleteAllCandidates = async () => {
    if (confirm('⚠️ Attention : Cette action supprimera TOUS les candidats. Êtes-vous sûr ?')) {
      try {
        const response = await authFetch('http://localhost:8000/api/candidates', {
          method: 'DELETE'
        });
        if (response.ok) {
          await fetchCandidates();
          setSelectedCandidate(null);
          setChatResponse('');
        }
      } catch (error) {
        console.error("Erreur lors de la suppression:", error);
      }
    }
  };

  const exportCandidatePDF = async (candidate, event) => {
    if (event) event.stopPropagation();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/candidates/${candidate.id}/export-pdf`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rapport_${candidate.name || 'candidat'}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        alert("Erreur lors de l'export du PDF");
      }
    } catch (error) {
      console.error("Erreur export PDF:", error);
      alert("Erreur de connexion au backend");
    }
  };

  const loadInterviewQuestions = async (candidate) => {
    setLoadingQuestions(true);
    setShowQuestionsModal(true);
    setSelectedCandidate(candidate);
    try {
      const response = await authFetch(`http://localhost:8000/api/candidates/${candidate.id}/questions`);
      if (response.ok) {
        const data = await response.json();
        setInterviewQuestions(data);
      } else {
        throw new Error("API error");
      }
    } catch (error) {
      console.error("Erreur chargement questions:", error);
      setInterviewQuestions({
        questions: [
          { question: "Parlez-moi de votre parcours professionnel", cible: "general", pourquoi: "Découverte du candidat" },
          { question: "Quelles sont vos principales compétences techniques ?", cible: "skills", pourquoi: "Évaluer le niveau technique" },
          { question: "Pourquoi souhaitez-vous rejoindre notre entreprise ?", cible: "motivation", pourquoi: "Évaluer la motivation" }
        ],
        summary: "🎯 Questions génériques d'entretien"
      });
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleChat = async () => {
    if (!chatMessage.trim() || !selectedCandidate) return;
    setIsChatLoading(true);
    setChatResponse("🔍 Recherche dans le CV...");
    try {
      const response = await authFetch(`http://localhost:8000/api/chat/${selectedCandidate.id}`, {
        method: 'POST',
        body: JSON.stringify({ question: chatMessage })
      });
      if (response.ok) {
        const data = await response.json();
        setChatResponse(data.answer);
      } else {
        setChatResponse("❌ Erreur lors de la recherche.");
      }
    } catch (error) {
      console.error("Erreur chat:", error);
      setChatResponse("❌ Impossible de contacter le serveur.");
    } finally {
      setIsChatLoading(false);
      setChatMessage("");
    }
  };

  const handleLogin = (user) => {
    setIsAuthenticated(true);
    setCurrentUser(user);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCandidates([]);
    setSelectedCandidate(null);
  };

  const stats = {
    total: candidates.length,
    preselected: candidates.filter(c => c.score >= 75).length,
    interview: candidates.filter(c => c.score >= 50 && c.score < 75).length,
    rejected: candidates.filter(c => c.score < 50).length,
    avgScore: candidates.length > 0 ? Math.round(candidates.reduce((a,b) => a + (b.score || 0), 0) / candidates.length) : 0,
    avgExperience: candidates.length > 0 ? Math.round(candidates.reduce((a,b) => a + (b.experience_years || 0), 0) / candidates.length) : 0
  };

  // Données de test pour Analytics (mock)
  const mockStats = {
    total: 12,
    preselected: 5,
    interview: 4,
    rejected: 3,
    avgScore: 68,
    avgExperience: 4.5
  };

  const mockSkills = [
    { skill: "Python", count: 8 },
    { skill: "JavaScript", count: 7 },
    { skill: "React", count: 6 },
    { skill: "AWS", count: 5 },
    { skill: "Docker", count: 4 },
    { skill: "TypeScript", count: 4 },
    { skill: "Node.js", count: 3 },
    { skill: "PostgreSQL", count: 3 }
  ];

  const mockExpDistribution = [
    { range: "0-2 ans", count: 2 },
    { range: "3-5 ans", count: 5 },
    { range: "6-8 ans", count: 3 },
    { range: "9-10 ans", count: 1 },
    { range: "10+ ans", count: 1 }
  ];

  const agents = [
    { name: "Parseur", status: "Actif", desc: "Extraction CV → JSON structuré", icon: Database, color: "blue" },
    { name: "Matcher", status: "Actif", desc: "Scoring sémantique via embeddings", icon: Target, color: "green" },
    { name: "Interviewer", status: "Actif", desc: "Questions ciblées par gaps détectés", icon: MessageSquare, color: "yellow" },
    { name: "Synthétiseur", status: "Actif", desc: "Rapport final forces/risques", icon: Activity, color: "purple" },
    { name: "RAG", status: "Actif", desc: "Chat intelligent sur les CV", icon: Brain, color: "pink" },
  ];

  const columns = {
    preselected: { title: "Présélectionnées", candidates: candidates.filter(c => c.score >= 75), count: candidates.filter(c => c.score >= 75).length },
    interview: { title: "À interviewer", candidates: candidates.filter(c => c.score >= 50 && c.score < 75), count: candidates.filter(c => c.score >= 50 && c.score < 75).length },
    rejected: { title: "Refusés", candidates: candidates.filter(c => c.score < 50), count: candidates.filter(c => c.score < 50).length },
  };

  // ==================== VUE GESTION DES CANDIDATS ====================
  const CandidatesView = () => {
    const [viewMode, setViewMode] = useState('table');
    const [selectedCandidates, setSelectedCandidates] = useState([]);
    const [sortBy, setSortBy] = useState('date');
    const [sortOrder, setSortOrder] = useState('desc');
    const [statusFilter, setStatusFilter] = useState('all');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

    const filteredCandidates = candidates.filter(c => {
      const matchesSearch = (c.name || c.filename || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' ? true : statusFilter === 'completed' ? c.status === 'completed' : c.status === 'pending';
      return matchesSearch && matchesStatus;
    });

    const sortedCandidates = [...filteredCandidates].sort((a, b) => {
      let aVal, bVal;
      switch(sortBy) {
        case 'score': aVal = a.score || 0; bVal = b.score || 0; break;
        case 'name': aVal = (a.name || a.filename || '').toLowerCase(); bVal = (b.name || b.filename || '').toLowerCase(); break;
        case 'experience': aVal = a.experience_years || 0; bVal = b.experience_years || 0; break;
        default: aVal = new Date(a.created_at || 0); bVal = new Date(b.created_at || 0);
      }
      if (sortOrder === 'asc') return aVal > bVal ? 1 : -1;
      return aVal < bVal ? 1 : -1;
    });

    const totalPages = Math.ceil(sortedCandidates.length / itemsPerPage);
    const paginatedCandidates = sortedCandidates.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    const statsCandidates = {
      total: candidates.length,
      completed: candidates.filter(c => c.status === 'completed').length,
      pending: candidates.filter(c => c.status === 'pending').length,
      avgScore: candidates.length > 0 ? Math.round(candidates.reduce((a,b) => a + (b.score || 0), 0) / candidates.length) : 0
    };

    const toggleSelect = (id) => setSelectedCandidates(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
    const selectAll = () => {
      if (selectedCandidates.length === paginatedCandidates.length) setSelectedCandidates([]);
      else setSelectedCandidates(paginatedCandidates.map(c => c.id));
    };

    const deleteSelected = async () => {
      if (confirm(`Supprimer ${selectedCandidates.length} candidat(s) ?`)) {
        for (const id of selectedCandidates) await deleteCandidate(id);
        setSelectedCandidates([]);
      }
    };

    const exportToCSV = () => {
      const headers = ['Nom', 'Email', 'Score', 'Compétences', 'Expérience', 'Statut', 'Date'];
      const rows = sortedCandidates.map(c => [
        c.name || c.filename, c.email || '', c.score || 0, (c.skills || []).join(', '),
        c.experience_years || 0, c.status === 'completed' ? 'Traité' : 'En attente',
        new Date(c.created_at || Date.now()).toLocaleDateString()
      ]);
      const csvContent = [headers, ...rows].map(row => row.join(';')).join('\n');
      const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `candidats_${new Date().toISOString().slice(0,10)}.csv`;
      link.click();
      URL.revokeObjectURL(link.href);
    };

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-blue-400">{statsCandidates.total}</div><div className="text-sm text-gray-400">Total candidats</div></div>
          <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-green-400">{statsCandidates.completed}</div><div className="text-sm text-gray-400">Traités</div></div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-yellow-400">{statsCandidates.pending}</div><div className="text-sm text-gray-400">En attente</div></div>
          <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-purple-400">{statsCandidates.avgScore}%</div><div className="text-sm text-gray-400">Score moyen</div></div>
        </div>

        <div className="flex flex-wrap justify-between items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="flex bg-gray-700 rounded-lg p-1">
              <button onClick={() => setViewMode('table')} className={`px-3 py-1.5 rounded-md text-sm ${viewMode === 'table' ? 'bg-blue-500 text-white' : 'text-gray-400'}`}>📋 Tableau</button>
              <button onClick={() => setViewMode('cards')} className={`px-3 py-1.5 rounded-md text-sm ${viewMode === 'cards' ? 'bg-blue-500 text-white' : 'text-gray-400'}`}>🃏 Cartes</button>
            </div>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-2 py-1.5 bg-gray-700 rounded-lg text-sm">
              <option value="all">Tous les statuts</option>
              <option value="completed">Traités</option>
              <option value="pending">En attente</option>
            </select>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="px-2 py-1.5 bg-gray-700 rounded-lg text-sm">
              <option value="date">Trier par date</option>
              <option value="score">Trier par score</option>
              <option value="name">Trier par nom</option>
              <option value="experience">Trier par expérience</option>
            </select>
            <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')} className="px-2 py-1.5 bg-gray-700 rounded-lg text-sm">{sortOrder === 'asc' ? '↑' : '↓'}</button>
          </div>
          <div className="flex items-center gap-2">
            {selectedCandidates.length > 0 && <button onClick={deleteSelected} className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg text-sm flex items-center gap-1"><Trash2 size={14} /> Supprimer ({selectedCandidates.length})</button>}
            <button onClick={exportToCSV} className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg text-sm flex items-center gap-1"><Download size={14} /> Export CSV</button>
          </div>
        </div>

        {viewMode === 'table' && (
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-700/50">
                  <tr><th className="p-3 w-10"><input type="checkbox" checked={selectedCandidates.length === paginatedCandidates.length && paginatedCandidates.length > 0} onChange={selectAll} className="w-4 h-4 rounded" /></th>
                    <th className="p-3 text-left">Candidat</th><th className="p-3 text-left">Score</th><th className="p-3 text-left">Compétences</th>
                    <th className="p-3 text-left">Expérience</th><th className="p-3 text-left">Date</th><th className="p-3 text-left">Statut</th><th className="p-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {paginatedCandidates.map(c => (
                    <tr key={c.id} className="hover:bg-gray-700/30">
                      <td className="p-3"><input type="checkbox" checked={selectedCandidates.includes(c.id)} onChange={() => toggleSelect(c.id)} className="w-4 h-4 rounded" /></td>
                      <td className="p-3"><div className="flex items-center gap-2"><div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-xs font-bold">{c.name?.charAt(0) || '?'}</div><div><div className="font-medium">{c.name || c.filename}</div><div className="text-xs text-gray-400">{c.email || '-'}</div></div></div></td>
                      <td className="p-3"><div className={`font-bold ${c.score >= 75 ? 'text-green-400' : c.score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{c.score || 0}%</div></td>
                      <td className="p-3"><div className="flex flex-wrap gap-1">{(c.skills || []).slice(0, 3).map(s => <span key={s} className="text-xs px-1.5 py-0.5 bg-gray-600 rounded-full">{s}</span>)}</div></td>
                      <td className="p-3">{c.experience_years || 0} ans</td>
                      <td className="p-3 text-sm">{new Date(c.created_at || Date.now()).toLocaleDateString()}</td>
                      <td className="p-3"><span className={`text-xs px-2 py-1 rounded-full ${c.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>{c.status === 'completed' ? '✓ Traité' : '⏳ En attente'}</span></td>
                      <td className="p-3"><div className="flex items-center gap-1">
                        <button onClick={() => { setSelectedCandidate(c); setActiveTab('chat'); }} className="p-1 text-blue-400 hover:bg-blue-500/20 rounded" title="Chat">💬</button>
                        <button onClick={() => loadInterviewQuestions(c)} className="p-1 text-purple-400 hover:bg-purple-500/20 rounded" title="Questions">❓</button>
                        <button onClick={(e) => exportCandidatePDF(c, e)} className="p-1 text-green-400 hover:bg-green-500/20 rounded" title="PDF">📄</button>
                        <button onClick={(e) => deleteCandidate(c.id, e)} className="p-1 text-red-400 hover:bg-red-500/20 rounded" title="Supprimer">🗑️</button>
                      </div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {totalPages > 1 && (
              <div className="p-4 border-t border-gray-700 flex justify-between items-center">
                <button onClick={() => setCurrentPage(p => Math.max(1, p-1))} disabled={currentPage === 1} className="px-3 py-1 bg-gray-700 rounded-lg disabled:opacity-50">◀ Précédent</button>
                <span className="text-sm">Page {currentPage} sur {totalPages}</span>
                <button onClick={() => setCurrentPage(p => Math.min(totalPages, p+1))} disabled={currentPage === totalPages} className="px-3 py-1 bg-gray-700 rounded-lg disabled:opacity-50">Suivant ▶</button>
              </div>
            )}
            {paginatedCandidates.length === 0 && <div className="text-center py-12 text-gray-500"><Users size={48} className="mx-auto mb-3 opacity-50" /><p>Aucun candidat trouvé</p></div>}
          </div>
        )}

        {viewMode === 'cards' && (
          <div className="grid grid-cols-3 gap-4">
            {paginatedCandidates.map(c => (
              <div key={c.id} className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-blue-500/50 transition">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2"><div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center font-bold">{c.name?.charAt(0) || '?'}</div><div><div className="font-medium">{c.name || c.filename}</div><div className="text-xs text-gray-400">{c.email || '-'}</div></div></div>
                  <div className={`text-xl font-bold ${c.score >= 75 ? 'text-green-400' : c.score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{c.score || 0}%</div>
                </div>
                <div className="mb-2"><div className="text-xs text-gray-400 mb-1">Compétences</div><div className="flex flex-wrap gap-1">{(c.skills || []).slice(0, 4).map(s => <span key={s} className="text-xs px-1.5 py-0.5 bg-gray-700 rounded-full">{s}</span>)}</div></div>
                <div className="flex justify-between text-sm mb-2"><span className="text-gray-400">Expérience:</span><span>{c.experience_years || 0} ans</span></div>
                <div className="flex justify-between text-sm mb-3"><span className="text-gray-400">Date:</span><span>{new Date(c.created_at || Date.now()).toLocaleDateString()}</span></div>
                <div className="flex justify-around pt-2 border-t border-gray-700">
                  <button onClick={() => { setSelectedCandidate(c); setActiveTab('chat'); }} className="p-2 text-blue-400 hover:bg-blue-500/20 rounded">💬</button>
                  <button onClick={() => loadInterviewQuestions(c)} className="p-2 text-purple-400 hover:bg-purple-500/20 rounded">❓</button>
                  <button onClick={(e) => exportCandidatePDF(c, e)} className="p-2 text-green-400 hover:bg-green-500/20 rounded">📄</button>
                  <button onClick={(e) => deleteCandidate(c.id, e)} className="p-2 text-red-400 hover:bg-red-500/20 rounded">🗑️</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // ==================== VUE ENTRETIENS ====================
  const InterviewsView = () => {
    const [interviews, setInterviews] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [showDetailModal, setShowDetailModal] = useState(false);
    const [showEmailModal, setShowEmailModal] = useState(false);
    const [editingInterview, setEditingInterview] = useState(null);
    const [selectedInterview, setSelectedInterview] = useState(null);
    const [selectedCandidate, setSelectedCandidate] = useState(null);
    const [emailSubject, setEmailSubject] = useState('');
    const [emailBody, setEmailBody] = useState('');
    const [filterDate, setFilterDate] = useState(new Date().toISOString().split('T')[0]);
    const [viewMode, setViewMode] = useState('list');
    
    const [formData, setFormData] = useState({
      candidate_id: '', candidate_name: '', date: new Date().toISOString().split('T')[0],
      time: '10:00', duration: 30, type: 'video', meeting_link: '', notes: ''
    });

    const fetchInterviews = async () => {
      try {
        const response = await authFetch('http://localhost:8000/api/interviews');
        if (response.ok) {
          const data = await response.json();
          setInterviews(data);
        }
      } catch (error) {
        console.error("Erreur chargement entretiens:", error);
      }
    };

    useEffect(() => {
      fetchInterviews();
    }, []);

    const createInterview = async () => {
      try {
        const response = await authFetch('http://localhost:8000/api/interviews', {
          method: 'POST', body: JSON.stringify(formData)
        });
        if (response.ok) {
          await fetchInterviews();
          setShowModal(false);
          resetForm();
        }
      } catch (error) {
        console.error("Erreur création entretien:", error);
      }
    };

    const updateInterview = async () => {
      if (!editingInterview) return;
      try {
        const response = await authFetch(`http://localhost:8000/api/interviews/${editingInterview.id}`, {
          method: 'PUT', body: JSON.stringify(formData)
        });
        if (response.ok) {
          await fetchInterviews();
          setShowModal(false);
          setEditingInterview(null);
          resetForm();
        }
      } catch (error) {
        console.error("Erreur modification entretien:", error);
      }
    };

    const deleteInterview = async (id) => {
      if (confirm('Supprimer cet entretien ?')) {
        try {
          await authFetch(`http://localhost:8000/api/interviews/${id}`, { method: 'DELETE' });
          await fetchInterviews();
          if (selectedInterview?.id === id) setShowDetailModal(false);
        } catch (error) {
          console.error("Erreur suppression:", error);
        }
      }
    };

    const updateStatus = async (id, status) => {
      try {
        const interview = interviews.find(i => i.id === id);
        const response = await authFetch(`http://localhost:8000/api/interviews/${id}`, {
          method: 'PUT', body: JSON.stringify({ ...interview, status })
        });
        if (response.ok) await fetchInterviews();
      } catch (error) {
        console.error("Erreur mise à jour:", error);
      }
    };

    const sendEmail = async () => {
      if (!selectedCandidate) return;
      try {
        await authFetch('http://localhost:8000/api/send-email', {
          method: 'POST', body: JSON.stringify({
            candidate_id: selectedCandidate.id, subject: emailSubject, body: emailBody
          })
        });
        alert('Email envoyé avec succès !');
        setShowEmailModal(false);
        setEmailSubject('');
        setEmailBody('');
      } catch (error) {
        console.error("Erreur envoi email:", error);
        alert('Erreur lors de l\'envoi');
      }
    };

    const resetForm = () => {
      setFormData({
        candidate_id: '', candidate_name: '', date: new Date().toISOString().split('T')[0],
        time: '10:00', duration: 30, type: 'video', meeting_link: '', notes: ''
      });
      setEditingInterview(null);
    };

    const openCreateModal = () => {
      resetForm();
      setShowModal(true);
    };

    const openEditModal = (interview) => {
      setEditingInterview(interview);
      setFormData({
        candidate_id: interview.candidate_id,
        candidate_name: interview.candidate_name,
        date: interview.date,
        time: interview.time,
        duration: interview.duration,
        type: interview.type,
        meeting_link: interview.meeting_link || '',
        notes: interview.notes || ''
      });
      setShowModal(true);
    };

    const openDetailModal = (interview) => {
      setSelectedInterview(interview);
      setShowDetailModal(true);
    };

    const openEmailModal = (candidate) => {
      setSelectedCandidate(candidate);
      setEmailSubject(`Entretien - ${candidate.name || 'Candidat'}`);
      setEmailBody(`Bonjour,\n\nJe vous confirme notre entretien le [DATE] à [HEURE].\n\nLien de visio: [LIEN]\n\nCordialement,\nL'équipe recrutement`);
      setShowEmailModal(true);
    };

    const filteredInterviews = interviews.filter(i => i.date === filterDate);
    const dates = [...new Set(interviews.map(i => i.date))].sort();
    const statsInterviews = {
      total: interviews.length,
      scheduled: interviews.filter(i => i.status === 'scheduled').length,
      completed: interviews.filter(i => i.status === 'completed').length,
      cancelled: interviews.filter(i => i.status === 'cancelled').length
    };

    const getTypeIcon = (type) => {
      switch(type) {
        case 'video': return '📹';
        case 'phone': return '📞';
        case 'onsite': return '🏢';
        default: return '📅';
      }
    };

    const getTypeLabel = (type) => {
      switch(type) {
        case 'video': return 'Visioconférence';
        case 'phone': return 'Téléphone';
        case 'onsite': return 'Sur site';
        default: return 'Entretien';
      }
    };

    const getStatusBadge = (status) => {
      switch(status) {
        case 'scheduled': return <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full text-xs flex items-center gap-1"><Clock size={10} /> Planifié</span>;
        case 'completed': return <span className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full text-xs flex items-center gap-1"><CheckCircle size={10} /> Réalisé</span>;
        case 'cancelled': return <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full text-xs flex items-center gap-1"><XCircle size={10} /> Annulé</span>;
        default: return <span className="px-2 py-0.5 bg-gray-500/20 text-gray-400 rounded-full text-xs">{status}</span>;
      }
    };

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 rounded-xl p-4 cursor-pointer hover:scale-105 transition" onClick={() => setFilterDate('')}>
            <div className="text-2xl font-bold text-blue-400">{statsInterviews.total}</div>
            <div className="text-sm text-gray-400">Total entretiens</div>
          </div>
          <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 rounded-xl p-4 cursor-pointer hover:scale-105 transition" onClick={() => setFilterDate('')}>
            <div className="text-2xl font-bold text-green-400">{statsInterviews.scheduled}</div>
            <div className="text-sm text-gray-400">Planifiés</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 rounded-xl p-4 cursor-pointer hover:scale-105 transition" onClick={() => setFilterDate('')}>
            <div className="text-2xl font-bold text-purple-400">{statsInterviews.completed}</div>
            <div className="text-sm text-gray-400">Réalisés</div>
          </div>
          <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 rounded-xl p-4 cursor-pointer hover:scale-105 transition" onClick={() => setFilterDate('')}>
            <div className="text-2xl font-bold text-red-400">{statsInterviews.cancelled}</div>
            <div className="text-sm text-gray-400">Annulés</div>
          </div>
        </div>

        <div className="flex justify-between items-center flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <button onClick={openCreateModal} className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center gap-2 hover:shadow-lg transition">
              <Plus size={16} /> Nouvel entretien
            </button>
            <div className="flex bg-gray-700 rounded-lg p-1">
              <button onClick={() => setViewMode('list')} className={`px-3 py-1.5 rounded-md text-sm ${viewMode === 'list' ? 'bg-blue-500 text-white' : 'text-gray-400'}`}>📋 Liste</button>
              <button onClick={() => setViewMode('calendar')} className={`px-3 py-1.5 rounded-md text-sm ${viewMode === 'calendar' ? 'bg-blue-500 text-white' : 'text-gray-400'}`}>📅 Calendrier</button>
            </div>
            <select value={filterDate} onChange={(e) => setFilterDate(e.target.value)} className="px-3 py-2 bg-gray-700 rounded-lg text-sm">
              <option value={new Date().toISOString().split('T')[0]}>Aujourd'hui</option>
              {dates.map(d => <option key={d} value={d}>{new Date(d).toLocaleDateString()}</option>)}
            </select>
          </div>
          <div className="text-sm text-gray-400">
            {filteredInterviews.length} entretien(s) le {new Date(filterDate).toLocaleDateString()}
          </div>
        </div>

        {viewMode === 'list' && (
          <div className="space-y-3">
            {filteredInterviews.map(interview => (
              <div key={interview.id} className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-blue-500/50 transition cursor-pointer group" onClick={() => openDetailModal(interview)}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-xl">
                      {getTypeIcon(interview.type)}
                    </div>
                    <div>
                      <div className="font-semibold text-lg group-hover:text-blue-400 transition">{interview.candidate_name}</div>
                      <div className="flex items-center gap-3 text-sm text-gray-400 mt-1 flex-wrap">
                        <span className="flex items-center gap-1"><Clock size={14} /> {interview.time} ({interview.duration} min)</span>
                        <span className="px-2 py-0.5 bg-gray-700 rounded-full text-xs">{getTypeLabel(interview.type)}</span>
                        {interview.meeting_link && <a href={interview.meeting_link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline text-xs flex items-center gap-1" onClick={(e) => e.stopPropagation()}>🔗 Lien de visio</a>}
                      </div>
                      {interview.notes && <div className="text-xs text-gray-500 mt-1 line-clamp-1">{interview.notes}</div>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(interview.status)}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                      <button onClick={(e) => { e.stopPropagation(); openEditModal(interview); }} className="p-2 text-yellow-400 hover:bg-yellow-500/20 rounded-lg" title="Modifier">✏️</button>
                      <button onClick={(e) => { e.stopPropagation(); openEmailModal({ id: interview.candidate_id, name: interview.candidate_name }); }} className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg" title="Envoyer email">✉️</button>
                      <button onClick={(e) => { e.stopPropagation(); deleteInterview(interview.id); }} className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg" title="Supprimer">🗑️</button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {filteredInterviews.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Calendar size={48} className="mx-auto mb-3 opacity-50" />
                <p>Aucun entretien prévu ce jour</p>
                <button onClick={openCreateModal} className="mt-3 text-blue-400 hover:underline">+ Planifier un entretien</button>
              </div>
            )}
          </div>
        )}

        {viewMode === 'calendar' && (
          <div className="grid grid-cols-7 gap-2">
            {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(day => (
              <div key={day} className="text-center text-sm font-medium text-gray-400 py-2">{day}</div>
            ))}
            {Array(35).fill(0).map((_, i) => {
              const day = i + 1;
              const dayInterviews = interviews.filter(i => new Date(i.date).getDate() === day);
              return (
                <div key={i} className="bg-gray-800 rounded-lg p-2 min-h-[100px] border border-gray-700 hover:border-blue-500/50 transition">
                  <div className="text-right text-sm text-gray-400">{day}</div>
                  <div className="space-y-1 mt-1">
                    {dayInterviews.slice(0, 2).map(interview => (
                      <div key={interview.id} onClick={() => openDetailModal(interview)} className="text-xs p-1 bg-blue-500/20 rounded cursor-pointer hover:bg-blue-500/30 truncate">
                        {interview.time} - {interview.candidate_name}
                      </div>
                    ))}
                    {dayInterviews.length > 2 && <div className="text-xs text-gray-500 text-center">+{dayInterviews.length - 2}</div>}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Modal Création/Modification */}
        {showModal && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowModal(false)}>
            <div className="bg-gray-800 rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="sticky top-0 bg-gray-800 p-4 border-b border-gray-700 flex justify-between">
                <h3 className="text-lg font-semibold">{editingInterview ? 'Modifier' : 'Nouvel'} entretien</h3>
                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">✕</button>
              </div>
              <div className="p-4 space-y-4">
                <select value={formData.candidate_id} onChange={(e) => { const candidate = candidates.find(c => c.id === e.target.value); setFormData({ ...formData, candidate_id: e.target.value, candidate_name: candidate?.name || '' }); }} className="w-full px-3 py-2 bg-gray-700 rounded-lg" required>
                  <option value="">Sélectionner un candidat</option>
                  {candidates.map(c => <option key={c.id} value={c.id}>{c.name || c.filename} {c.email ? `(${c.email})` : ''}</option>)}
                </select>
                <div className="grid grid-cols-2 gap-3">
                  <input type="date" value={formData.date} onChange={(e) => setFormData({ ...formData, date: e.target.value })} className="px-3 py-2 bg-gray-700 rounded-lg" />
                  <input type="time" value={formData.time} onChange={(e) => setFormData({ ...formData, time: e.target.value })} className="px-3 py-2 bg-gray-700 rounded-lg" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <select value={formData.duration} onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) })} className="px-3 py-2 bg-gray-700 rounded-lg">
                    <option value="15">15 min</option><option value="30">30 min</option><option value="45">45 min</option><option value="60">60 min</option>
                  </select>
                  <select value={formData.type} onChange={(e) => setFormData({ ...formData, type: e.target.value })} className="px-3 py-2 bg-gray-700 rounded-lg">
                    <option value="video">📹 Visioconférence</option><option value="phone">📞 Téléphone</option><option value="onsite">🏢 Sur site</option>
                  </select>
                </div>
                <input type="text" value={formData.meeting_link} onChange={(e) => setFormData({ ...formData, meeting_link: e.target.value })} placeholder="Lien de visioconférence (Zoom, Teams, Meet...)" className="w-full px-3 py-2 bg-gray-700 rounded-lg" />
                <textarea value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} placeholder="Notes (optionnel)" rows="3" className="w-full px-3 py-2 bg-gray-700 rounded-lg" />
                <button onClick={editingInterview ? updateInterview : createInterview} disabled={!formData.candidate_id || !formData.date || !formData.time} className="w-full py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg font-medium hover:opacity-90 transition disabled:opacity-50">
                  {editingInterview ? '💾 Enregistrer les modifications' : '📅 Créer l\'entretien'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal Détail entretien */}
        {showDetailModal && selectedInterview && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowDetailModal(false)}>
            <div className="bg-gray-800 rounded-xl max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
              <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                <h3 className="text-lg font-semibold flex items-center gap-2"><Calendar size={20} className="text-blue-400" /> Détail de l'entretien</h3>
                <button onClick={() => setShowDetailModal(false)} className="text-gray-400 hover:text-white text-xl">✕</button>
              </div>
              <div className="p-4 space-y-4">
                <div className="flex items-center gap-3 p-3 bg-gray-700/30 rounded-lg">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-xl">{getTypeIcon(selectedInterview.type)}</div>
                  <div><div className="font-semibold text-lg">{selectedInterview.candidate_name}</div><div className="text-sm text-gray-400">ID: {selectedInterview.candidate_id}</div></div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Date</div><div className="font-medium">{new Date(selectedInterview.date).toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div></div>
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Horaire</div><div className="font-medium">{selectedInterview.time} ({selectedInterview.duration} minutes)</div></div>
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Type</div><div className="font-medium flex items-center gap-1">{getTypeIcon(selectedInterview.type)} {getTypeLabel(selectedInterview.type)}</div></div>
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Statut</div><div>{getStatusBadge(selectedInterview.status)}</div></div>
                </div>
                {selectedInterview.meeting_link && (
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Lien de visioconférence</div><a href={selectedInterview.meeting_link} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline break-all">{selectedInterview.meeting_link}</a></div>
                )}
                {selectedInterview.notes && (
                  <div className="p-3 bg-gray-700/30 rounded-lg"><div className="text-xs text-gray-400 mb-1">Notes</div><div className="text-sm whitespace-pre-wrap">{selectedInterview.notes}</div></div>
                )}
                <div className="flex gap-3 pt-2">
                  <select value={selectedInterview.status} onChange={(e) => { updateStatus(selectedInterview.id, e.target.value); setShowDetailModal(false); }} className="flex-1 px-3 py-2 bg-gray-700 rounded-lg text-sm">
                    <option value="scheduled">📅 Marquer comme planifié</option><option value="completed">✅ Marquer comme réalisé</option><option value="cancelled">❌ Marquer comme annulé</option>
                  </select>
                  <button onClick={() => { openEditModal(selectedInterview); setShowDetailModal(false); }} className="px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 transition">✏️ Modifier</button>
                  <button onClick={() => { deleteInterview(selectedInterview.id); setShowDetailModal(false); }} className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition">🗑️ Supprimer</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal Email */}
        {showEmailModal && selectedCandidate && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowEmailModal(false)}>
            <div className="bg-gray-800 rounded-xl max-w-md w-full" onClick={(e) => e.stopPropagation()}>
              <div className="p-4 border-b border-gray-700 flex justify-between"><h3 className="text-lg font-semibold">✉️ Envoyer un email à {selectedCandidate.name}</h3><button onClick={() => setShowEmailModal(false)} className="text-gray-400">✕</button></div>
              <div className="p-4 space-y-4">
                <input type="text" value={emailSubject} onChange={(e) => setEmailSubject(e.target.value)} placeholder="Sujet" className="w-full px-3 py-2 bg-gray-700 rounded-lg" />
                <textarea value={emailBody} onChange={(e) => setEmailBody(e.target.value)} placeholder="Votre message..." rows="8" className="w-full px-3 py-2 bg-gray-700 rounded-lg" />
                <div className="flex gap-3"><button onClick={() => setShowEmailModal(false)} className="flex-1 py-2 bg-gray-700 rounded-lg">Annuler</button><button onClick={sendEmail} className="flex-1 py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center gap-2"><Send size={16} /> Envoyer</button></div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const JobsView = () => (
    <div className="space-y-6">
      {offerMessage && (
        <div className={`rounded-lg p-3 text-center ${offerMessage.includes('✅') ? 'bg-green-500/20 text-green-400 border border-green-500' : 'bg-red-500/20 text-red-400 border border-red-500'}`}>
          {offerMessage}
        </div>
      )}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700 bg-gradient-to-r from-blue-900/20 to-transparent">
          <h3 className="font-semibold text-lg flex items-center gap-2"><Briefcase size={20} className="text-blue-400" />Définir l'offre d'emploi</h3>
          <p className="text-sm text-gray-400">Les CV seront comparés à cette offre pour le scoring automatique</p>
        </div>
        <div className="p-4 space-y-4">
          <input type="text" value={jobOffer.title} onChange={(e) => setJobOffer({...jobOffer, title: e.target.value})} className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg" placeholder="Ex: Lead Dev Full Stack" />
          <div className="flex gap-2 mb-3">
            <input type="text" value={newSkill} onChange={(e) => setNewSkill(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && addSkill()} className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg" placeholder="Ajouter une compétence" />
            <button onClick={addSkill} className="px-4 py-2 bg-blue-500 rounded-lg hover:bg-blue-600 flex items-center gap-1"><Plus size={16} /> Ajouter</button>
          </div>
          <div className="flex flex-wrap gap-2">{jobOffer.required_skills.map((skill, idx) => (<span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-700 rounded-lg text-sm">{skill}<button onClick={() => removeSkill(skill)} className="text-red-400">×</button></span>))}</div>
          <input type="number" value={jobOffer.experience_years} onChange={(e) => setJobOffer({...jobOffer, experience_years: parseInt(e.target.value) || 0})} className="w-32 px-3 py-2 bg-gray-700 rounded-lg" min="0" />
          <button onClick={saveJobOffer} disabled={savingOffer} className="w-full py-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg font-medium">{savingOffer ? "Sauvegarde..." : "💾 Sauvegarder l'offre"}</button>
        </div>
      </div>
    </div>
  );

  // Vue Analytics
  const AnalyticsView = () => {
    const hasRealData = candidates.length > 0;
    const displayStats = hasRealData ? stats : mockStats;
    const getTopSkills = () => {
      if (hasRealData) {
        const skillCount = {};
        candidates.forEach(c => { (c.skills || []).forEach(skill => { skillCount[skill] = (skillCount[skill] || 0) + 1; }); });
        return Object.entries(skillCount).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([skill, count]) => ({ skill, count }));
      }
      return mockSkills;
    };
    const getExpDistribution = () => {
      if (hasRealData) {
        const ranges = { '0-2 ans': 0, '3-5 ans': 0, '6-8 ans': 0, '9-10 ans': 0, '10+ ans': 0 };
        candidates.forEach(c => { const exp = c.experience_years || 0; if (exp <= 2) ranges['0-2 ans']++; else if (exp <= 5) ranges['3-5 ans']++; else if (exp <= 8) ranges['6-8 ans']++; else if (exp <= 10) ranges['9-10 ans']++; else ranges['10+ ans']++; });
        return Object.entries(ranges).map(([range, count]) => ({ range, count }));
      }
      return mockExpDistribution;
    };
    const topSkills = getTopSkills();
    const maxSkillCount = Math.max(...topSkills.map(s => s.count), 1);
    return (
      <div className="space-y-6">
        {!hasRealData && <div className="bg-blue-500/20 border border-blue-500/30 rounded-xl p-3 text-center"><p className="text-blue-400 text-sm">Mode démo - Uploadez des CV pour voir vos données réelles !</p></div>}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-blue-400">{displayStats.total}</div><div className="text-sm text-gray-400">CV analysés</div></div>
          <div className="bg-gradient-to-br from-green-500/10 to-green-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-green-400">{displayStats.preselected}</div><div className="text-sm text-gray-400">Présélectionnés</div></div>
          <div className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-yellow-400">{displayStats.interview}</div><div className="text-sm text-gray-400">À interviewer</div></div>
          <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 rounded-xl p-4"><div className="text-2xl font-bold text-purple-400">{displayStats.avgScore}%</div><div className="text-sm text-gray-400">Score moyen</div></div>
        </div>
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <h3 className="font-semibold mb-4 text-center">Distribution des scores</h3>
            <div className="flex justify-around items-center py-4">
              <div className="text-center"><div className="w-20 h-20 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-2xl mx-auto">{displayStats.preselected}</div><div className="text-xs mt-2 text-green-400">Présélectionnés</div></div>
              <div className="text-center"><div className="w-20 h-20 rounded-full bg-yellow-500 flex items-center justify-center text-white font-bold text-2xl mx-auto">{displayStats.interview}</div><div className="text-xs mt-2 text-yellow-400">À interviewer</div></div>
              <div className="text-center"><div className="w-20 h-20 rounded-full bg-red-500 flex items-center justify-center text-white font-bold text-2xl mx-auto">{displayStats.rejected}</div><div className="text-xs mt-2 text-red-400">Refusés</div></div>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <h3 className="font-semibold mb-4 text-center">Top compétences</h3>
            <div className="space-y-3">{topSkills.map((skill) => (<div key={skill.skill}><div className="flex justify-between text-sm"><span className="capitalize">{skill.skill}</span><span className="text-gray-400">{skill.count}</span></div><div className="h-2 bg-gray-700 rounded-full overflow-hidden"><div className="h-full bg-blue-500 rounded-full" style={{ width: `${(skill.count / maxSkillCount) * 100}%` }} /></div></div>))}</div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <h3 className="font-semibold mb-4 text-center">Distribution expérience</h3>
            <div className="space-y-3">{getExpDistribution().map((item) => (<div key={item.range}><div className="flex justify-between text-sm"><span>{item.range}</span><span className="text-gray-400">{item.count}</span></div><div className="h-2 bg-gray-700 rounded-full overflow-hidden"><div className="h-full bg-green-500 rounded-full" style={{ width: `${(item.count / displayStats.total) * 100}%` }} /></div></div>))}</div>
          </div>
          <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
            <h3 className="font-semibold mb-4 text-center">Scores récents</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {(hasRealData ? candidates : [{ name: "Sofia Andrade", score: 92 }, { name: "Marc Bouchard", score: 85 }, { name: "Layla Karim", score: 78 }]).slice(0, 5).map((c, idx) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-700/30 rounded-lg"><span className="text-sm">{c.name}</span><span className={`text-sm font-bold ${c.score >= 75 ? 'text-green-400' : c.score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{c.score}%</span></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
    <button onClick={onClick} className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg transition text-sm ${active ? 'bg-gray-700 text-blue-400' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}>
      <Icon size={18} /><span>{label}</span>
    </button>
  );

  const bgColor = darkMode ? 'bg-gray-900' : 'bg-gray-100';
  const textColor = darkMode ? 'text-gray-100' : 'text-gray-900';
  const sidebarBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  if (!isAuthenticated) return <Login onLogin={handleLogin} />;

  return (
    <div className={`flex h-screen ${bgColor} ${textColor}`}>
      <aside className={`w-64 ${sidebarBg} border-r ${borderColor} p-4 flex flex-col`}>
        <div className="flex justify-between items-center mb-6"><h1 className="text-xl font-bold text-blue-400">HireFlow</h1>
          <button onClick={() => setDarkMode(!darkMode)} className="p-1.5 rounded-lg bg-gray-700/50 hover:bg-gray-600">{darkMode ? <Sun size={16} className="text-yellow-400" /> : <Moon size={16} className="text-blue-400" />}</button>
        </div>
        {currentUser && (<div className="mb-4 p-2 bg-gray-700/30 rounded-lg"><div className="text-sm font-medium">{currentUser.name}</div><div className="text-xs text-gray-400">{currentUser.email}</div></div>)}
        <h2 className="text-xs uppercase tracking-wider text-gray-500 mb-3">Principal</h2>
        <nav className="space-y-1 mb-6">
          <SidebarItem icon={LayoutDashboard} label="Pipeline" active={activeTab === 'pipeline'} onClick={() => setActiveTab('pipeline')} />
          <SidebarItem icon={Upload} label="Upload CV" active={activeTab === 'upload'} onClick={() => setActiveTab('upload')} />
          <SidebarItem icon={Users} label="Candidats" active={activeTab === 'candidates'} onClick={() => setActiveTab('candidates')} />
          <SidebarItem icon={Calendar} label="Entretiens" active={activeTab === 'interviews'} onClick={() => setActiveTab('interviews')} />
        </nav>
        <h2 className="text-xs uppercase tracking-wider text-gray-500 mb-3">Agents IA</h2>
        <nav className="space-y-1 mb-6">
          <SidebarItem icon={Activity} label="Statut agents" active={activeTab === 'agents'} onClick={() => setActiveTab('agents')} />
          <SidebarItem icon={BarChart3} label="Analytics" active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} />
        </nav>
        <h2 className="text-xs uppercase tracking-wider text-gray-500 mb-3">Offres</h2>
        <nav className="space-y-1 mb-6">
          <SidebarItem icon={Briefcase} label="Postes ouverts" active={activeTab === 'jobs'} onClick={() => setActiveTab('jobs')} />
          <SidebarItem icon={Settings} label="Paramètres" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        </nav>
        <div className="mt-auto pt-4 border-t border-gray-700 space-y-2">
          <div className="flex items-center gap-2 text-xs text-gray-500"><div className={`w-2 h-2 rounded-full ${backendStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} /><span>Agents actifs: 5/5</span></div>
          <button onClick={handleLogout} className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-red-400 hover:bg-red-500/20"><LogOut size={18} /><span>Déconnexion</span></button>
        </div>
      </aside>

      <main className="flex-1 overflow-auto"><div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <div><h2 className="text-xl font-bold">
            {activeTab === 'pipeline' && 'Pipeline — ' + jobOffer.title}
            {activeTab === 'upload' && 'Upload de CV'}
            {activeTab === 'candidates' && 'Gestion des candidats'}
            {activeTab === 'interviews' && 'Agenda des entretiens'}
            {activeTab === 'agents' && 'Statut des agents IA'}
            {activeTab === 'analytics' && 'Analytiques avancées'}
            {activeTab === 'jobs' && 'Gestion des offres'}
            {activeTab === 'settings' && 'Paramètres'}
          </h2></div>
          <div className="flex items-center gap-3">
            <div className="relative"><Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" /><input type="text" placeholder="Rechercher" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-9 pr-3 py-1.5 bg-gray-800 border border-gray-700 rounded-lg text-sm w-48" /></div>
            {candidates.length > 0 && <button onClick={deleteAllCandidates} className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg"><Trash2 size={16} /> Tout supprimer</button>}
          </div>
        </div>

        {activeTab === 'pipeline' && (
          <div className="space-y-6">
            <div className="grid grid-cols-5 gap-4">{agents.map((agent, idx) => (<div key={idx} className="bg-gray-800 rounded-lg p-2 text-center border-l-4 border-blue-500"><agent.icon size={16} className="mx-auto text-blue-400 mb-1" /><div className="font-medium text-xs">{agent.name}</div><span className="text-xs text-green-400">{agent.status}</span></div>))}</div>
            <div className="grid grid-cols-3 gap-5">{Object.entries(columns).map(([key, col]) => (<div key={key} className="bg-gray-800/50 rounded-lg"><div className="p-3 border-b border-gray-700 flex justify-between"><h3 className={`font-medium ${key === 'preselected' ? 'text-blue-400' : key === 'interview' ? 'text-yellow-400' : 'text-gray-400'}`}>{key === 'preselected' && '📋'} {key === 'interview' && '🎯'} {key === 'rejected' && '❌'} {col.title}</h3><span className="text-sm text-gray-400">{col.count}</span></div><div className="p-3 space-y-3 max-h-[500px] overflow-y-auto">{col.candidates.map(c => (<div key={c.id} className="bg-gray-700 rounded-lg p-3"><div className="flex justify-between"><div className="flex gap-2 cursor-pointer" onClick={() => { setSelectedCandidate(c); setActiveTab('chat'); }}><div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-xs font-bold">{c.name?.charAt(0)}{c.name?.charAt(1) || c.name?.charAt(0)}</div><div><div className="font-medium text-sm">{c.name || 'Candidat'}</div><div className="text-xs text-gray-400">{c.experience_years ? `${c.experience_years} ans` : 'Expérience inconnue'}</div><div className="flex gap-1 mt-1">{(c.skills || []).slice(0, 2).map(s => <span key={s} className="text-xs px-1.5 py-0.5 bg-gray-600 rounded-full">{s}</span>)}</div></div></div><div className="text-right"><div className={`text-lg font-bold ${c.score >= 75 ? 'text-green-400' : c.score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>{c.score || 0}%</div><div className="text-xs text-gray-500">compatibilité</div><div className="flex gap-1 mt-1"><button onClick={(e) => { e.stopPropagation(); loadInterviewQuestions(c); }} className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">❓</button><button onClick={(e) => exportCandidatePDF(c, e)} className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded">📄</button><button onClick={(e) => deleteCandidate(c.id, e)} className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded">🗑️</button></div></div></div></div>))}</div></div>))}</div>
          </div>
        )}

        {activeTab === 'upload' && (
          <div className="bg-gray-800 rounded-lg p-8 text-center border-2 border-dashed border-gray-600">
            <Upload size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold mb-2">Déposez vos CV ici</h3>
            <p className="text-gray-400 text-sm mb-4">Support PDF, DOCX, TXT</p>
            <input type="file" multiple onChange={(e) => setFiles([...e.target.files])} className="hidden" id="file-input" accept=".pdf,.docx,.txt" />
            <label htmlFor="file-input" className="px-4 py-2 bg-blue-500 rounded-lg cursor-pointer hover:bg-blue-600 inline-block">Sélectionner des fichiers</label>
            {files.length > 0 && (<div className="mt-4"><button onClick={async () => { setUploading(true); const formData = new FormData(); files.forEach(f => formData.append('files', f)); try { const token = localStorage.getItem('token'); await fetch('http://localhost:8000/api/upload-batch', { method: 'POST', body: formData, headers: { 'Authorization': `Bearer ${token}` } }); await fetch('http://localhost:8000/api/process-all', { method: 'POST', headers: { 'Authorization': `Bearer ${token}` } }); await fetchCandidates(); alert(`${files.length} CV traités !`); } catch (error) { console.error(error); } finally { setUploading(false); setFiles([]); } }} className="px-4 py-2 bg-green-500 rounded-lg">{uploading ? 'Traitement...' : `Uploader ${files.length} fichier(s)`}</button></div>)}
          </div>
        )}

        {activeTab === 'candidates' && <CandidatesView />}
        {activeTab === 'interviews' && <InterviewsView />}
        {activeTab === 'jobs' && <JobsView />}
        {activeTab === 'analytics' && <AnalyticsView />}

        {activeTab === 'agents' && (
          <div className="grid grid-cols-2 gap-6">{agents.map((agent, idx) => (<div key={idx} className="bg-gray-800 rounded-lg p-4"><div className="flex items-center gap-3 mb-3"><agent.icon size={24} className="text-blue-400" /><div><div className="font-semibold">{agent.name}</div><div className="text-xs text-green-400">{agent.status}</div></div></div><p className="text-sm text-gray-400">{agent.desc}</p><div className="mt-3 h-1 bg-gray-700 rounded-full"><div className="h-full w-full bg-green-500 rounded-full" /></div></div>))}</div>
        )}

        {activeTab === 'chat' && (
          <div className="grid grid-cols-2 gap-6 h-[calc(100vh-150px)]">
            <div className="bg-gray-800 rounded-lg p-4 overflow-y-auto"><h3 className="font-semibold mb-3">📄 Sélectionnez un candidat</h3><div className="space-y-2">{candidates.map(c => (<div key={c.id} onClick={() => setSelectedCandidate(c)} className={`p-3 rounded-lg cursor-pointer ${selectedCandidate?.id === c.id ? 'bg-blue-500/20 border border-blue-500' : 'bg-gray-700 hover:bg-gray-600'}`}><div className="font-medium">{c.name || 'Candidat'}</div><div className="text-xs text-gray-400">Score: {c.score || 0}%</div></div>))}</div></div>
            <div className="bg-gray-800 rounded-lg flex flex-col"><div className="p-4 border-b border-gray-700"><h3 className="font-semibold">💬 Chat — {selectedCandidate?.name || 'Sélectionnez un candidat'}</h3></div><div className="flex-1 p-4 overflow-y-auto">{chatResponse && <div className="bg-gray-700 rounded-lg p-3"><div className="text-xs text-blue-400 mb-1">Agent RAG</div><div className="text-sm">{chatResponse}</div></div>}{!chatResponse && selectedCandidate && <div className="text-center text-gray-500 py-8">Posez une question</div>}</div><div className="p-4 border-t border-gray-700"><div className="flex gap-2"><input type="text" value={chatMessage} onChange={(e) => setChatMessage(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleChat()} placeholder="Votre question..." className="flex-1 px-3 py-2 bg-gray-700 rounded-lg" /><button onClick={handleChat} className="px-4 py-2 bg-blue-500 rounded-lg"><Send size={16} /></button></div></div></div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="bg-gray-800 rounded-xl p-6 max-w-2xl"><h3 className="font-semibold text-lg mb-4">⚙️ Paramètres</h3>
            <div className="space-y-4"><div className="flex justify-between items-center p-3 bg-gray-700/30 rounded-lg"><div><div className="font-medium">Thème</div><div className="text-sm text-gray-400">Mode sombre / clair</div></div><button onClick={() => setDarkMode(!darkMode)} className="px-3 py-1.5 bg-gray-700 rounded-lg">{darkMode ? 'Mode clair' : 'Mode sombre'}</button></div>
            <div className="flex justify-between items-center p-3 bg-gray-700/30 rounded-lg"><div><div className="font-medium">Compte</div><div className="text-sm text-gray-400">{currentUser?.email}</div></div><button onClick={handleLogout} className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg">Déconnexion</button></div>
            <div className="flex justify-between items-center p-3 bg-gray-700/30 rounded-lg"><div><div className="font-medium">Version</div><div className="text-sm text-gray-400">HireFlow v2.0</div></div><Sparkles className="w-5 h-5 text-purple-400" /></div>
            {candidates.length > 0 && <button onClick={deleteAllCandidates} className="w-full py-2 bg-red-500/20 text-red-400 rounded-lg">🗑️ Supprimer toutes les données</button>}</div>
          </div>
        )}
      </div></main>

      {showQuestionsModal && selectedCandidate && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={() => setShowQuestionsModal(false)}>
          <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-gray-800 p-4 border-b border-gray-700 flex justify-between"><h3 className="text-lg font-semibold">Questions pour {selectedCandidate.name}</h3><button onClick={() => setShowQuestionsModal(false)} className="text-gray-400">✕</button></div>
            <div className="p-4 space-y-4">{loadingQuestions ? <div className="text-center py-8">Chargement...</div> : interviewQuestions?.questions?.map((q, idx) => (<div key={idx} className="bg-gray-700 rounded-lg p-3"><div className="font-medium">{idx+1}. {q.question}</div><div className="text-xs text-gray-400 mt-1">{q.pourquoi}</div></div>))}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;