import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';
import { Loader2 } from 'lucide-react';

const SpacedAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setLoading(true); setError(null);
      const res = await axios.get('/api/spaced-repetition/performance-analytics?period_days=30');
      const j = res.data;
      if (j.status !== 'success') throw new Error(j.message || 'Analyse échouée');
      setData(j.analytics);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="flex items-center gap-2 text-gray-600"><Loader2 className="h-4 w-4 animate-spin" />Chargement analytics...</div>;
  if (error) return <div className="text-red-600 text-sm">Erreur: {error}</div>;
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card className="border-0 shadow-xl">
        <CardHeader><CardTitle>Aperçu 30 jours</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between text-sm"><span>Total révisions</span><span className="font-semibold">{data.total_reviews}</span></div>
          <div>
            <div className="flex justify-between text-sm"><span>Taux de réussite moyen</span><span className="font-semibold">{Math.round(data.average_success_rate * 100)}%</span></div>
            <Progress value={data.average_success_rate * 100} className="h-2" />
          </div>
          <div>
            <div className="flex justify-between text-sm"><span>Taux de rétention</span><span className="font-semibold">{Math.round(data.retention_rate * 100)}%</span></div>
            <Progress value={data.retention_rate * 100} className="h-2" />
          </div>
          <div className="flex justify-between text-sm"><span>Temps moyen de réponse</span><span className="font-semibold">{data.average_response_time.toFixed(1)}s</span></div>
          <div className="flex justify-between text-sm"><span>Score de régularité</span><span className="font-semibold">{Math.round(data.consistency_score * 100)}%</span></div>
        </CardContent>
      </Card>

      <Card className="border-0 shadow-xl">
        <CardHeader><CardTitle>Répartition Difficulté</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-3 gap-3 text-sm">
          {['easy', 'medium', 'hard'].map(k => (
            <div key={k} className="p-3 rounded-lg bg-gray-50">
              <div className="font-medium capitalize">{k}</div>
              <div className="text-gray-600">Succès: {Math.round(data.difficulty_breakdown[k].success_rate * 100)}%</div>
              <div className="text-gray-600">Temps moy.: {data.difficulty_breakdown[k].avg_time.toFixed(1)}s</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default SpacedAnalytics;