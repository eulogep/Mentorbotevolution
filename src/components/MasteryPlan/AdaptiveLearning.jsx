import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { BarChart3, BrainCircuit, Clock3, Loader2, Play, Save, SlidersHorizontal } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

const displayNames = {
  language: 'Anglais et TOEIC',
  computing: 'Informatique',
  productivity: 'Bureautique',
  data: 'Données et visualisation',
  infrastructure: 'Réseau et systèmes',
  security: 'Cybersécurité',
  general: 'Parcours libre',
};

const AdaptiveLearning = ({ onStartDomainSession }) => {
  const { token } = useAuth();
  const [domains, setDomains] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingDomain, setSavingDomain] = useState(null);
  const [error, setError] = useState(null);

  const loadAdaptiveData = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const authConfig = { headers: { Authorization: `Bearer ${token}` } };
      const [overviewResponse, profilesResponse] = await Promise.all([
        axios.get('/api/spaced-repetition/adaptive-overview', authConfig),
        axios.get('/api/spaced-repetition/adaptive-profiles', authConfig),
      ]);
      if (overviewResponse.data.status !== 'success' || profilesResponse.data.status !== 'success') {
        throw new Error('Les données adaptatives ne sont pas disponibles.');
      }
      setDomains(overviewResponse.data.domains || []);
      setProfiles(profilesResponse.data.profiles || []);
    } catch (requestError) {
      setError(requestError.message || 'Impossible de charger le module adaptatif.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadAdaptiveData(); }, [loadAdaptiveData]);

  const profileByDomain = useMemo(
    () => Object.fromEntries(profiles.map((profile) => [profile.domain, profile])),
    [profiles],
  );
  const visibleDomains = domains.filter((domain) => domain.cards_total > 0 || ['language', 'computing'].includes(domain.domain));

  const updateRetention = async (domain, value) => {
    try {
      setSavingDomain(domain);
      setError(null);
      const authConfig = { headers: { Authorization: `Bearer ${token}` } };
      const response = await axios.put(
        `/api/spaced-repetition/adaptive-profiles/${domain}`,
        { desired_retention: Number(value) },
        authConfig,
      );
      if (response.data.status !== 'success') throw new Error(response.data.message || 'Enregistrement impossible');
      await loadAdaptiveData();
    } catch (requestError) {
      setError(requestError.message || 'Impossible d’enregistrer ce réglage.');
    } finally {
      setSavingDomain(null);
    }
  };

  if (loading) return <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Calcul des priorités de révision…</div>;

  return (
    <div className="space-y-5">
      <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 via-white to-teal-50 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg"><BrainCircuit className="h-5 w-5 text-indigo-700" />Apprentissage adaptatif</CardTitle>
          <CardDescription>Chaque carte est planifiée par FSRS à partir de vos rappels. La rétention cible est un choix explicite : l’augmenter peut accroître la charge de révision.</CardDescription>
        </CardHeader>
      </Card>

      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}

      <div className="grid gap-4 lg:grid-cols-2">
        {visibleDomains.map((domain) => {
          const profile = profileByDomain[domain.domain];
          const retention = profile?.desired_retention ?? domain.desired_retention;
          const isSaving = savingDomain === domain.domain;
          return (
            <Card key={domain.domain} className="border-slate-200 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3"><div><CardTitle className="text-base">{displayNames[domain.domain] || domain.label}</CardTitle><CardDescription className="mt-1">{domain.cards_total} carte{domain.cards_total > 1 ? 's' : ''} suivie{domain.cards_total > 1 ? 's' : ''}</CardDescription></div><Badge variant="outline" className="border-indigo-200 bg-indigo-50 text-indigo-800">{domain.cards_due} due{domain.cards_due > 1 ? 's' : ''}</Badge></div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3 text-sm"><div className="rounded-lg bg-slate-50 p-3"><p className="flex items-center gap-1 text-xs text-slate-500"><Clock3 className="h-3.5 w-3.5" />Revues sur 30 jours</p><p className="mt-1 text-lg font-semibold text-slate-900">{domain.reviews_last_30_days}</p></div><div className="rounded-lg bg-slate-50 p-3"><p className="flex items-center gap-1 text-xs text-slate-500"><BarChart3 className="h-3.5 w-3.5" />Rappel observé</p><p className="mt-1 text-lg font-semibold text-slate-900">{domain.recall_rate === null ? '—' : `${Math.round(domain.recall_rate * 100)} %`}</p></div></div>
                <div className="rounded-lg border border-slate-200 p-3"><p className="text-xs font-medium text-slate-700">Rétention cible</p><div className="mt-2 flex items-center gap-2"><select aria-label={`Rétention cible ${displayNames[domain.domain] || domain.label}`} value={retention} onChange={(event) => updateRetention(domain.domain, event.target.value)} disabled={isSaving} className="w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"><option value="0.80">80 % — charge réduite</option><option value="0.85">85 %</option><option value="0.90">90 % — équilibre</option><option value="0.93">93 %</option><option value="0.95">95 % — charge élevée</option><option value="0.97">97 % — charge très élevée</option></select><Save className="h-4 w-4 shrink-0 text-slate-500" /></div><p className="mt-2 text-xs text-slate-500">Appliquée à la prochaine revue de ce domaine. Source : {domain.retention_source === 'domain_profile' ? 'préférence du domaine' : 'préférence globale'}.</p></div>
                <p className="text-sm leading-5 text-slate-600">{domain.recommendation.message}</p>
                <Button type="button" className="w-full bg-indigo-700 hover:bg-indigo-800" disabled={domain.cards_due === 0} onClick={() => onStartDomainSession?.(domain.domain)}><Play className="mr-2 h-4 w-4" />Réviser {displayNames[domain.domain] || domain.label}</Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card className="border-slate-200 shadow-sm"><CardContent className="flex gap-3 p-5"><SlidersHorizontal className="mt-0.5 h-5 w-5 shrink-0 text-indigo-700" /><p className="text-sm leading-6 text-slate-600">Le module organise le rappel de vocabulaire, définitions, commandes et concepts. Pour maîtriser l’anglais ou l’informatique, complétez ces cartes par de l’écoute, des projets, des exercices pratiques et des explications justifiées.</p></CardContent></Card>
    </div>
  );
};

export default AdaptiveLearning;
