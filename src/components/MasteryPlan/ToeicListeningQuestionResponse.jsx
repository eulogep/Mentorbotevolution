import { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import { ArrowRight, CheckCircle2, Headphones, Loader2, RotateCcw, Sparkles, Volume2 } from 'lucide-react';
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
  listening_function: 'Fonction communicative',
  listening_detail: 'Repérage d’information',
  listening_cause: 'Comprendre une cause',
};

const ToeicListeningQuestionResponse = ({ onRemediationCreated }) => {
  const { token } = useAuth();
  const audioRef = useRef(null);
  const [subjects, setSubjects] = useState([]);
  const [subjectId, setSubjectId] = useState('');
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [attempt, setAttempt] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [items, setItems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [playCount, setPlayCount] = useState(0);
  const [audioState, setAudioState] = useState('Prêt à écouter.');
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
  const unavailableAssets = useMemo(
    () => (metadata?.items || []).filter((item) => item.audio_status !== 'available'),
    [metadata],
  );
  const listeningReady = Boolean(metadata?.items?.length) && unavailableAssets.length === 0;
  const remediationTargets = useMemo(() => results?.analysis?.remediation_targets || [], [results]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        const [subjectResponse, listeningResponse] = await Promise.all([
          axios.get('/api/mastery/get-subjects', authConfig),
          axios.get('/api/diagnostic/toeic-listening-question-response', authConfig),
        ]);
        const nextSubjects = subjectResponse.data?.status === 'success' ? subjectResponse.data.subjects || [] : [];
        const nextLanguageSubjects = nextSubjects.filter((subject) => subject.domain === 'language');
        setSubjects(nextSubjects);
        setSubjectId((current) => current || (nextLanguageSubjects[0] ? String(nextLanguageSubjects[0].id) : ''));
        setMetadata(listeningResponse.data || null);
      } catch (requestError) {
        setError(requestError.response?.data?.message || requestError.message || 'Impossible de préparer le module Listening.');
      } finally {
        setLoading(false);
      }
    };
    if (token) loadInitialData();
  }, [authConfig, token]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return undefined;
    const handleEnded = () => setAudioState('Écoute terminée. Vous pouvez maintenant choisir votre réponse.');
    const handleError = () => {
      setAudioState('Le fichier audio est indisponible. Cet exercice ne peut pas être poursuivi.');
      setError('Le fichier audio attendu est indisponible. Rechargez la page ou revenez lorsque la publication des actifs est terminée.');
    };
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    return () => {
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [currentItem?.id]);

  const resetSession = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setAttempt(null);
    setDiagnostic(null);
    setItems([]);
    setCurrentIndex(0);
    setAnswers([]);
    setSelectedIndex(null);
    setConfidence(null);
    setPlayCount(0);
    setAudioState('Prêt à écouter.');
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
    if (!listeningReady) {
      setError('Le diagnostic Listening reste indisponible tant que les quatre actifs audio originaux ne sont pas publiés et vérifiés.');
      return;
    }
    try {
      setStarting(true);
      setError(null);
      const response = await axios.post(
        '/api/diagnostic/toeic-listening-question-response/start',
        { subject_id: Number(subjectId) },
        authConfig,
      );
      setAttempt(response.data.attempt);
      setDiagnostic(response.data.diagnostic);
      setItems(response.data.items || []);
      setCurrentIndex(0);
      setAnswers([]);
      setSelectedIndex(null);
      setConfidence(null);
      setPlayCount(0);
      setAudioState('Prêt à écouter. L’extrait pourra être lu une seule fois.');
      const now = Date.now();
      setItemStartedAt(now);
      setDiagnosticStartedAt(now);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'Impossible de démarrer le diagnostic Listening.');
    } finally {
      setStarting(false);
    }
  };

  const playCurrentAudio = async () => {
    if (!currentItem || playCount >= currentItem.max_plays) return;
    const audio = audioRef.current;
    if (!audio) return;
    try {
      setError(null);
      setAudioState('Lecture de l’extrait audio en cours.');
      await audio.play();
      setPlayCount(1);
    } catch (playError) {
      setAudioState('La lecture audio n’a pas pu démarrer.');
      setError(playError.message || 'La lecture audio n’a pas pu démarrer.');
    }
  };

  const continueToNextItem = async () => {
    if (selectedIndex === null || !currentItem || playCount < 1) return;
    const responseTime = itemStartedAt ? Math.max(0, (Date.now() - itemStartedAt) / 1000) : null;
    const nextAnswers = [...answers, {
      item_id: currentItem.id,
      selected_index: selectedIndex,
      response_time_seconds: responseTime,
      confidence,
      play_count: playCount,
    }];

    if (currentIndex < items.length - 1) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setAnswers(nextAnswers);
      setCurrentIndex((current) => current + 1);
      setSelectedIndex(null);
      setConfidence(null);
      setPlayCount(0);
      setAudioState('Prêt à écouter. L’extrait pourra être lu une seule fois.');
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
      setError(requestError.response?.data?.message || requestError.message || 'Impossible d’enregistrer les réponses Listening.');
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

  if (loading) return <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Préparation du module Listening…</div>;

  if (results) {
    const attemptResult = results.attempt;
    return (
      <div className="space-y-5">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
        <Card className="border-indigo-200 bg-indigo-50/60 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg"><CheckCircle2 className="h-5 w-5 text-indigo-700" />Résultats descriptifs d’écoute</CardTitle>
            <CardDescription>{results.disclaimer}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Items corrects</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.correct_count} / {attemptResult.total_items}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Exactitude observée</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.accuracy === null ? '—' : `${Math.round(attemptResult.accuracy * 100)} %`}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Temps observé</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.duration_seconds ? `${Math.round(attemptResult.duration_seconds / 60)} min` : '—'}</p></div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader><CardTitle className="text-base">Réécoute guidée et transcription</CardTitle><CardDescription>Les scripts et corrections deviennent disponibles après la soumission, pour soutenir la révision sans aider la première réponse.</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            {(results.review_items || []).map((item, index) => <div key={item.item_id} className="rounded-xl border border-slate-200 bg-slate-50 p-4"><div className="flex items-center justify-between gap-3"><p className="font-semibold text-slate-900">Extrait {index + 1}</p><Badge variant={item.is_correct ? 'default' : 'outline'}>{item.is_correct ? 'Réponse correcte' : 'À revoir'}</Badge></div><p className="mt-3 whitespace-pre-line text-sm leading-6 text-slate-800">{item.transcript}</p><p className="mt-3 text-sm text-slate-700"><span className="font-semibold">Correction :</span> {item.choices[item.correct_index]}</p><p className="mt-1 text-sm text-slate-600">{item.explanation}</p></div>)}
          </CardContent>
        </Card>

        {remediationTargets.length > 0 && <Card className="border-amber-200 bg-amber-50/50 shadow-sm"><CardHeader><CardTitle className="text-base">Cartes FSRS optionnelles</CardTitle><CardDescription>Seules des formulations atomiques et réutilisables peuvent être ajoutées aux révisions espacées.</CardDescription></CardHeader><CardContent>{!remediation ? <Button onClick={createRemediation} disabled={creatingRemediation} className="w-full bg-indigo-700 hover:bg-indigo-800">{creatingRemediation ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Création des cartes…</> : <><Sparkles className="mr-2 h-4 w-4" />Créer les cartes de remédiation FSRS</>}</Button> : <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900"><p className="font-semibold">{remediation.created_count} carte(s) créée(s).</p><p className="mt-1">Elles rejoignent les révisions FSRS du domaine Langues.</p></div>}</CardContent></Card>}
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
            <CardTitle className="flex items-center gap-2 text-lg"><Headphones className="h-5 w-5 text-indigo-700" />Listening — questions et réponses</CardTitle>
            <CardDescription>Quatre exercices audio originaux d’anglais professionnel. Une seule écoute est autorisée par item avant la correction différée. Cette activité n’est pas un test TOEIC officiel.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {languageSubjects.length ? <><div><label htmlFor="listening-subject" className="block text-sm font-semibold text-slate-800">Parcours de langue associé</label><select id="listening-subject" value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600">{languageSubjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}</select></div>{listeningReady ? <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-950"><p className="font-semibold">Module prêt</p><p className="mt-1">Les quatre actifs audio sont présents et leur transcription restera masquée jusqu’à la soumission.</p></div> : <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"><p className="font-semibold">Publication audio en cours</p><p className="mt-1">{unavailableAssets.length || 4} actif(s) audio sont encore indisponibles. Le diagnostic complet restera volontairement fermé jusqu’à la vérification des quatre fichiers originaux.</p></div>}<Button onClick={startDiagnostic} disabled={starting || !listeningReady} className="w-full bg-indigo-700 hover:bg-indigo-800">{starting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Préparation…</> : <><ArrowRight className="mr-2 h-4 w-4" />Démarrer le diagnostic d’écoute</>}</Button></> : <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-700">Créez d’abord un parcours du domaine Langues pour rattacher vos résultats et vos remédiations à un objectif explicite.</div>}
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
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start"><div><CardTitle className="text-lg">Diagnostic écoute</CardTitle><CardDescription>{diagnostic?.title} · Item {currentIndex + 1} sur {items.length}</CardDescription></div><Badge variant="outline">{targetLabels[currentItem?.target] || currentItem?.target}</Badge></div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-600 transition-[width] duration-200" style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }} /></div>
        </CardHeader>
        <CardContent className="space-y-5">
          <audio ref={audioRef} src={currentItem?.audio_url} preload="auto" aria-hidden="true" />
          <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-4"><p className="font-semibold text-indigo-950">Écoute unique</p><p className="mt-1 text-sm text-indigo-900">Écoutez l’extrait, puis choisissez la réponse A, B ou C. Les choix textuels et la transcription restent masqués jusqu’à la correction.</p><Button className="mt-3 bg-indigo-700 hover:bg-indigo-800" onClick={playCurrentAudio} disabled={playCount >= (currentItem?.max_plays || 1)} aria-describedby="listening-audio-status"><Volume2 className="mr-2 h-4 w-4" />{playCount ? 'Écoute utilisée' : 'Écouter l’extrait'}</Button><p id="listening-audio-status" className="mt-3 text-sm text-indigo-900" aria-live="polite">{audioState}</p></div>
          <div className="grid gap-2 sm:grid-cols-3">{(currentItem?.choice_labels || []).map((label, index) => <button type="button" key={label} onClick={() => setSelectedIndex(index)} disabled={playCount < 1} className={`rounded-xl border p-4 text-left text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-50 ${selectedIndex === index ? 'border-indigo-600 bg-indigo-50 text-indigo-950 ring-1 ring-indigo-600' : 'border-slate-200 bg-white text-slate-800 hover:border-indigo-300 hover:bg-slate-50'}`}><span className="text-indigo-700">Réponse {label}</span></button>)}</div>
          <div><p className="mb-2 text-sm font-semibold text-slate-800">Confiance dans votre réponse <span className="font-normal text-slate-500">(facultatif)</span></p><div className="grid grid-cols-2 gap-2 sm:grid-cols-4">{confidenceLabels.map((item) => <button type="button" key={item.value} onClick={() => setConfidence(item.value)} disabled={playCount < 1} className={`rounded-lg border px-3 py-2 text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-50 ${confidence === item.value ? 'border-indigo-600 bg-indigo-50 text-indigo-950' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>{item.label}</button>)}</div></div>
          <div className="flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between"><p className="text-xs text-slate-500">Le nombre d’écoutes et le temps sont des données de contrôle descriptives, pas des indicateurs de niveau.</p><Button onClick={continueToNextItem} disabled={selectedIndex === null || playCount < 1 || submitting} className="bg-indigo-700 hover:bg-indigo-800">{submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyse…</> : <>{isLastItem ? 'Voir mes résultats' : 'Question suivante'}<ArrowRight className="ml-2 h-4 w-4" /></>}</Button></div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ToeicListeningQuestionResponse;
