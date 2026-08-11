import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { ArrowRight, CheckCircle2, ClipboardCheck, Clock3, Loader2, RotateCcw, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

const confidenceLabels = [
  { value: 1, label: 'Très incertain' },
  { value: 2, label: 'Plutôt incertain' },
  { value: 3, label: 'Plutôt sûr' },
  { value: 4, label: 'Très sûr' },
];

const targetLabels = {
  grammar: 'Grammaire en contexte',
  lexis: 'Vocabulaire professionnel',
  cohesion: 'Cohésion du texte',
  detail: 'Repérage d’information',
  inference: 'Inférence simple',
};

const ToeicReadingDiagnostic = ({ onRemediationCreated }) => {
  const { token } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [subjectId, setSubjectId] = useState('');
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [starting, setStarting] = useState(false);
  const [attempt, setAttempt] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [items, setItems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [itemStartedAt, setItemStartedAt] = useState(null);
  const [diagnosticStartedAt, setDiagnosticStartedAt] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [creatingRemediation, setCreatingRemediation] = useState(false);
  const [remediation, setRemediation] = useState(null);
  const [error, setError] = useState(null);

  const authConfig = useMemo(() => (token ? { headers: { Authorization: `Bearer ${token}` } } : {}), [token]);
  const languageSubjects = useMemo(() => subjects.filter((subject) => subject.domain === 'language'), [subjects]);
  const currentItem = items[currentIndex];
  const currentTarget = currentItem ? targetLabels[currentItem.target] || currentItem.target : '';
  const remediationTargets = useMemo(
    () => (results?.analysis?.recommendations || []).filter((item) => item.code === 'create_remediation').map((item) => item.target),
    [results],
  );

  useEffect(() => {
    const loadSubjects = async () => {
      try {
        setLoadingSubjects(true);
        const response = await axios.get('/api/mastery/get-subjects', authConfig);
        const nextSubjects = response.data?.status === 'success' ? response.data.subjects || [] : [];
        const nextLanguageSubjects = nextSubjects.filter((subject) => subject.domain === 'language');
        setSubjects(nextSubjects);
        setSubjectId((current) => current || (nextLanguageSubjects[0] ? String(nextLanguageSubjects[0].id) : ''));
      } catch (requestError) {
        setError(requestError.message || 'Impossible de charger les parcours de langue.');
      } finally {
        setLoadingSubjects(false);
      }
    };
    if (token) loadSubjects();
  }, [authConfig, token]);

  const resetSession = () => {
    setAttempt(null);
    setDiagnostic(null);
    setItems([]);
    setCurrentIndex(0);
    setAnswers([]);
    setSelectedIndex(null);
    setConfidence(null);
    setItemStartedAt(null);
    setDiagnosticStartedAt(null);
    setResults(null);
    setRemediation(null);
    setError(null);
  };

  const startDiagnostic = async () => {
    if (!subjectId) {
      setError('Créez ou choisissez d’abord un parcours du domaine Langues.');
      return;
    }
    try {
      setStarting(true);
      setError(null);
      const response = await axios.post('/api/diagnostic/toeic-reading/start', { subject_id: Number(subjectId) }, authConfig);
      setAttempt(response.data.attempt);
      setDiagnostic(response.data.diagnostic);
      setItems(response.data.items || []);
      setCurrentIndex(0);
      setAnswers([]);
      setSelectedIndex(null);
      setConfidence(null);
      const now = Date.now();
      setItemStartedAt(now);
      setDiagnosticStartedAt(now);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'Impossible de démarrer le diagnostic.');
    } finally {
      setStarting(false);
    }
  };

  const continueToNextItem = async () => {
    if (selectedIndex === null || !currentItem) return;
    const responseTime = itemStartedAt ? Math.max(0, (Date.now() - itemStartedAt) / 1000) : null;
    const nextAnswers = [...answers, {
      item_id: currentItem.id,
      selected_index: selectedIndex,
      response_time_seconds: responseTime,
      confidence,
    }];

    if (currentIndex < items.length - 1) {
      setAnswers(nextAnswers);
      setCurrentIndex((current) => current + 1);
      setSelectedIndex(null);
      setConfidence(null);
      setItemStartedAt(Date.now());
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const durationSeconds = diagnosticStartedAt ? Math.max(0, (Date.now() - diagnosticStartedAt) / 1000) : null;
      const response = await axios.post(
        `/api/diagnostic/attempts/${attempt.id}/submit`,
        { responses: nextAnswers, duration_seconds: durationSeconds },
        authConfig,
      );
      setAnswers(nextAnswers);
      setResults(response.data);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'Impossible d’enregistrer les réponses.');
    } finally {
      setSubmitting(false);
    }
  };

  const createRemediation = async () => {
    if (!attempt || !remediationTargets.length) return;
    try {
      setCreatingRemediation(true);
      setError(null);
      const response = await axios.post(
        `/api/diagnostic/attempts/${attempt.id}/create-remediation`,
        { targets: remediationTargets },
        authConfig,
      );
      setRemediation(response.data);
      onRemediationCreated?.();
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'Impossible de créer les cartes de remédiation.');
    } finally {
      setCreatingRemediation(false);
    }
  };

  if (loadingSubjects) return <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Chargement du diagnostic…</div>;

  if (results) {
    const attemptResult = results.attempt;
    const accuracyPercent = attemptResult.accuracy === null ? '—' : `${Math.round(attemptResult.accuracy * 100)} %`;
    return (
      <div className="space-y-5">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
        <Card className="border-indigo-200 bg-indigo-50/60 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg"><CheckCircle2 className="h-5 w-5 text-indigo-700" />Résultats descriptifs</CardTitle>
            <CardDescription>{results.disclaimer}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Items corrects</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.correct_count} / {attemptResult.total_items}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Exactitude observée</p><p className="mt-1 text-2xl font-bold text-slate-950">{accuracyPercent}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Temps observé</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.duration_seconds ? `${Math.round(attemptResult.duration_seconds / 60)} min` : '—'}</p></div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader><CardTitle className="text-base">Détail par cible</CardTitle><CardDescription>Ces chiffres décrivent ce lot d’items ; ils ne certifient pas votre niveau.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {results.analysis.breakdown.map((item) => <div key={item.target} className="flex flex-col justify-between gap-2 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center"><div><p className="font-semibold text-slate-900">{targetLabels[item.target] || item.target}</p><p className="mt-1 text-sm text-slate-600">{item.correct} correct(s) sur {item.items} · {item.incorrect} erreur(s)</p></div><Badge variant="outline">{item.accuracy === null ? '—' : `${Math.round(item.accuracy * 100)} %`}</Badge></div>)}
          </CardContent>
        </Card>

        <Card className="border-amber-200 bg-amber-50/50 shadow-sm">
          <CardHeader><CardTitle className="text-base">Prochaines actions</CardTitle><CardDescription>Les recommandations s’appuient uniquement sur les réponses observées et la taille de l’échantillon.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {results.analysis.recommendations.map((recommendation) => <div key={recommendation.target} className="rounded-xl border border-amber-200 bg-white p-4"><p className="font-semibold text-slate-900">{targetLabels[recommendation.target] || recommendation.target}</p><p className="mt-1 text-sm text-slate-700">{recommendation.message}</p></div>)}
            {remediationTargets.length > 0 && !remediation && <Button onClick={createRemediation} disabled={creatingRemediation} className="w-full bg-indigo-700 hover:bg-indigo-800">{creatingRemediation ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Création des cartes…</> : <><Sparkles className="mr-2 h-4 w-4" />Créer les cartes de remédiation FSRS</>}</Button>}
            {remediation && <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900"><p className="font-semibold">{remediation.created_count} carte(s) de remédiation créée(s).</p><p className="mt-1">Elles sont immédiatement disponibles dans les révisions du domaine Langues. {remediation.skipped_count ? `${remediation.skipped_count} carte(s) identique(s) existaient déjà.` : ''}</p></div>}
          </CardContent>
        </Card>
        <Button variant="outline" onClick={resetSession}><RotateCcw className="mr-2 h-4 w-4" />Faire un nouveau diagnostic</Button>
      </div>
    );
  }

  if (!attempt) {
    return (
      <div className="space-y-5">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg"><ClipboardCheck className="h-5 w-5 text-indigo-700" />Diagnostic lecture — anglais professionnel</CardTitle>
            <CardDescription>19 items originaux sur la grammaire, le vocabulaire, la cohésion et la compréhension de documents professionnels. Cette activité formative ne fournit pas de score TOEIC estimé.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {languageSubjects.length ? <><div><label htmlFor="diagnostic-subject" className="block text-sm font-semibold text-slate-800">Parcours de langue associé</label><select id="diagnostic-subject" value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600">{languageSubjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}</select></div><div className="rounded-xl border border-indigo-100 bg-indigo-50 p-4 text-sm text-indigo-950"><p className="font-semibold">Avant de commencer</p><p className="mt-1">Répondez sans aide. Après le diagnostic, l’application indiquera les cibles à pratiquer ; vous déciderez ensuite si des cartes FSRS doivent être créées.</p></div><Button onClick={startDiagnostic} disabled={starting} className="w-full bg-indigo-700 hover:bg-indigo-800">{starting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Préparation…</> : <><ArrowRight className="mr-2 h-4 w-4" />Démarrer le diagnostic</>}</Button></> : <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-700">Créez d’abord un parcours du domaine Langues pour rattacher vos résultats et vos remédiations à un objectif explicite.</div>}
          </CardContent>
        </Card>
      </div>
    );
  }

  const isLastItem = currentIndex === items.length - 1;
  return (
    <div className="space-y-5">
      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start"><div><CardTitle className="text-lg">Diagnostic lecture</CardTitle><CardDescription>{diagnostic?.title} · Item {currentIndex + 1} sur {items.length}</CardDescription></div><Badge variant="outline">{currentTarget}</Badge></div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-600 transition-[width] duration-200" style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }} /></div>
        </CardHeader>
        <CardContent className="space-y-5">
          {currentItem?.passage && <div className="whitespace-pre-line rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-800">{currentItem.passage}</div>}
          <div><p className="text-base font-semibold leading-7 text-slate-950">{currentItem?.prompt}</p><p className="mt-1 text-xs text-slate-500">Contexte : {currentItem?.scenario}</p></div>
          <div className="grid gap-2">{currentItem?.choices.map((choice, index) => <button type="button" key={choice} onClick={() => setSelectedIndex(index)} className={`rounded-xl border p-4 text-left text-sm transition ${selectedIndex === index ? 'border-indigo-600 bg-indigo-50 text-indigo-950 ring-1 ring-indigo-600' : 'border-slate-200 bg-white text-slate-800 hover:border-indigo-300 hover:bg-slate-50'}`}><span className="mr-2 font-semibold text-indigo-700">{String.fromCharCode(65 + index)}.</span>{choice}</button>)}</div>
          <div><p className="mb-2 text-sm font-semibold text-slate-800">Confiance dans votre réponse <span className="font-normal text-slate-500">(facultatif)</span></p><div className="grid grid-cols-2 gap-2 sm:grid-cols-4">{confidenceLabels.map((item) => <button type="button" key={item.value} onClick={() => setConfidence(item.value)} className={`rounded-lg border px-3 py-2 text-xs font-medium transition ${confidence === item.value ? 'border-indigo-600 bg-indigo-50 text-indigo-950' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>{item.label}</button>)}</div></div>
          <div className="flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between"><p className="flex items-center gap-2 text-xs text-slate-500"><Clock3 className="h-4 w-4" />Le temps est enregistré comme donnée descriptive, pas comme seuil universel.</p><Button onClick={continueToNextItem} disabled={selectedIndex === null || submitting} className="bg-indigo-700 hover:bg-indigo-800">{submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyse…</> : <>{isLastItem ? 'Voir mes résultats' : 'Question suivante'}<ArrowRight className="ml-2 h-4 w-4" /></>}</Button></div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ToeicReadingDiagnostic;
