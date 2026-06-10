import React, { useState, useEffect } from 'react';

function KanbanBoard() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/candidates');
      const data = await response.json();
      setCandidates(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getColumn = (score) => {
    if (score >= 75) return 'preselected';
    if (score >= 50) return 'interview';
    return 'rejected';
  };

  const columns = {
    preselected: { title: 'Présélectionnées', color: 'blue', candidates: [] },
    interview: { title: 'À interviewer', color: 'yellow', candidates: [] },
    rejected: { title: 'Refusés', color: 'gray', candidates: [] }
  };

  candidates.forEach(c => {
    const col = getColumn(c.score || 0);
    columns[col].candidates.push(c);
  });

  if (loading) return <div className="p-6">Chargement...</div>;

  return (
    <div className="p-6">
      <div className="grid grid-cols-3 gap-6">
        {Object.entries(columns).map(([key, col]) => (
          <div key={key} className="bg-gray-800 rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold">{col.title}</h3>
              <span className={`text-sm px-2 py-1 rounded bg-${col.color}-900/30 text-${col.color}-400`}>
                {col.candidates.length}
              </span>
            </div>
            <div className="space-y-3">
              {col.candidates.map(c => (
                <div key={c.id} className="bg-gray-700/50 rounded-lg p-3 hover:bg-gray-700 transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{c.name || c.filename}</div>
                      <div className="text-sm text-gray-400">{c.skills?.slice(0, 2).join(', ') || '—'}</div>
                    </div>
                    <div className={`text-lg font-bold ${
                      c.score >= 75 ? 'text-green-400' : c.score >= 50 ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {c.score || '—'}%
                    </div>
                  </div>
                </div>
              ))}
              {col.candidates.length === 0 && (
                <div className="text-center text-gray-500 py-4 text-sm">Aucun candidat</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default KanbanBoard;