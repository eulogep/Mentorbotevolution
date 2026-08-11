import { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, BarChart3, Clock3, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Progress } from '../ui/progress';

const ratingLabels = {
  again: 'À revoir',
  hard: 'Difficile',
  good: 'Bien',
  easy: 'Facile',
};

const SpacedAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [insights, setInsights] = useState([]);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('/api/spaced-repetition/performance-analytics?period_days=30');
      const payload = response.data;
      if (payload.status !== 'success') throw new Error(payload.message || 'Analyse échouée');
      setData(payload.analytics);
      setInsights(payload.insights || []);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <div className="flex items-center gap-2 text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Calcul à partir de vos révisions…</div>;
  if (error) return <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">Erreur : {error}</div>;
  if (!data) return null;

  const totalRatings = Object.values(data.ratings || {}).reduce((sum, value) => sum + value, 0);

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div><h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900"><BarChart3 className="h-5 w-5 text-indigo-700" />Vos données de pratique</h3><p className="mt-1 text-sm text-slate-600">Description des 30 derniers jours — aucune prédiction de score TOEIC.</p></div>
        <Button size="sm" variant="outline" onClick={load}><RefreshCw className="mr-2 h-4 w-4" />Actualiser</Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="border-slate-200 shadow-sm"><CardContent className="p-5"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Révisions enregistrées</p><p className="mt-2 text-3xl font-bold text-slate-950">{data.total_reviews}</p><p className="mt-2 text-xs text-slate-600">Sur {data.total_cards} carte{data.total_cards > 1 ? 's' : ''} créée{data.total_cards > 1 ? 's' : ''}.</p></CardContent></Card>
        <Card className="border-slate-200 shadow-sm"><CardContent className="p-5"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Rappels retrouvés</p><p className="mt-2 text-3xl font-bold text-slate-950">{Math.round(data.average_success_rate * 100)} %</p><Progress value={data.average_success_rate * 100} className="mt-3 h-2" /><p className="mt-2 text-xs text-slate-600">« Difficile », « Bien » et « Facile » comptent comme un rappel retrouvé.</p></CardContent></Card>
        <Card className="border-slate-200 shadow-sm"><CardContent className="p-5"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Temps de réponse</p><p className="mt-2 flex items-center gap-2 text-3xl font-bold text-slate-950"><Clock3 className="h-5 w-5 text-indigo-700" />{data.average_response_time.toFixed(1)} s</p><p className="mt-2 text-xs text-slate-600">Moyenne des temps mesurés en session.</p></CardContent></Card>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="border-slate-200 shadow-sm"><CardHeader><CardTitle className="text-base">Comment vos rappels ont été évalués</CardTitle><CardDescription>Les quatre réponses qui alimentent le calendrier de révision.</CardDescription></CardHeader><CardContent className="space-y-3">{Object.entries(ratingLabels).map(([rating, label]) => { const count = data.ratings?.[rating] || 0; const percentage = totalRatings ? (count / totalRatings) * 100 : 0; return <div key={rating}><div className="mb-1 flex justify-between text-sm"><span className="text-slate-700">{label}</span><span className="font-medium text-slate-900">{count}</span></div><Progress value={percentage} className="h-2" /></div>; })}</CardContent></Card>
        <Card className="border-slate-200 shadow-sm"><CardHeader><CardTitle className="text-base">Notions à consolider</CardTitle><CardDescription>Cartes avec au moins deux revues et moins de 60 % de rappels retrouvés.</CardDescription></CardHeader><CardContent>{data.fragile_cards?.length ? <div className="space-y-3">{data.fragile_cards.map((card) => <div key={card.id} className="flex items-start gap-3 rounded-xl bg-amber-50 p-3"><AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700" /><div><p className="text-sm font-medium text-slate-900">{card.concept_name}</p><p className="mt-1 text-xs text-slate-600">Rappels retrouvés : {Math.round(card.success_rate * 100)} % sur {card.review_count} revue{card.review_count > 1 ? 's' : ''}.</p></div></div>)}</div> : <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-600">Aucune carte fragile détectée pour le moment. Davantage de revues produiront un diagnostic plus utile.</p>}</CardContent></Card>
      </div>

      {insights.length > 0 && <Card className="border-indigo-100 bg-indigo-50 shadow-sm"><CardContent className="p-5"><h4 className="font-semibold text-indigo-950">Pistes de pratique</h4><ul className="mt-2 space-y-2 text-sm leading-6 text-indigo-900">{insights.map((insight) => <li key={insight}>• {insight}</li>)}</ul></CardContent></Card>}
    </div>
  );
};

export default SpacedAnalytics;
