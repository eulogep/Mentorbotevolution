import { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import { ArrowRight, CheckCircle2, Headphones, Loader2, RotateCcw, Sparkles, Square, Volume2 } from 'lucide-react';
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
  listening_detail: 'Repérage d’information',
  listening_inference: 'Inférence prudente',
  listening_main_idea: 'Idée principale',
};

const SharedListeningDiagnostic = ({ endpoint, moduleId, onRemediationCreated }) => {
  const { token } = useAuth();
  const audioRef = useRef(null);
  const [subjects, setSubjects] = useState([]);
  const [subjectId, setSubjectId] = useState('');
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [attempt, setAttempt] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [stimuli, setStimuli] = useState([]);
  const [items, setItems] = useState([]);
  const [stimulusIndex, setStimulusIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [playback, setPlayback] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioState, setAudioState] = useState('Prêt à écouter.');
  const [stimulusStartedAt, setStimulusStartedAt] = useState(null);
  const [diagnosticStartedAt, setDiagnosticStartedAt] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);
  const [review, setReview] = useState(null);
  const [creatingRemediation, setCreatingRemediation] = useState(false);
  const [remediation, setRemediation] = useState(null);
  const [error, setError] = useState(null);

  const authConfig = useMemo(() => (token ? { headers: { Authorization: `Bearer ${token}` } } : {}), [token]);
  const languageSubjects = useMemo(() => subjects.filter((subject) => subject.domain === 'language'), [subjects]);
  const unavailableAssets = useMemo(
    () => (metadata?.stimuli || []).filter((stimulus) => stimulus.audio_status !== 'available'),
    [metadata],
  );
  const listeningReady = Boolean(metadata?.stimuli?.length) && unavailableAssets.length === 0;
  const currentStimulus = stimuli[stimulusIndex];
  const currentQuestions = useMemo(
    () => items.filter((item) => item.stimulus_id === currentStimulus?.id),
    [items, currentStimulus?.id],
  );
  const currentAnswersComplete = currentQuestions.length > 0 && currentQuestions.every((item) => answers[item.id]?.selected_index !== undefined);
  const remediationTargets = useMemo(() => results?.analysis?.available_remediation_targets || [], [results]);

  useEffect(() => {
    let ignore = false;
    if (!token) {
      setSubjects([]);
      setMetadata(null);
      setLoading(false);
      return () => { ignore = true; };
    }

    const loadInitialData = async () => {
      try {
        setLoading(true);
        const [subjectResponse, catalogResponse] = await Promise.all([
          axios.get('/api/mastery/get-subjects', authConfig),
          axios.get(endpoint, authConfig),
        ]);
        if (ignore) return;
        const nextSubjects = subjectResponse.data?.status === 'success' ? subjectResponse.data.subjects || [] : [];
        const nextLanguageSubjects = nextSubjects.filter((subject) => subject.domain === 'language');
        setSubjects(nextSubjects);
        setSubjectId((current) => current || (nextLanguageSubjects[0] ? String(nextLanguageSubjects[0].id) : ''));
        setMetadata(catalogResponse.data || null);
      } catch (requestError) {
        if (!ignore) setError(requestError.response?.data?.message || requestError.message || 'Impossible de préparer le module Listening avancé.');
      } finally {
        if (!ignore) setLoading(false);
      }
    };
    loadInitialData();
    return () => { ignore = true; };
  }, [authConfig, endpoint, token]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return undefined;
    const handleEnded = () => {
      setIsPlaying(false);
      setAudioState(`Écoute terminée. Répondez maintenant aux ${currentQuestions.length} questions associées.`);
    };
    const handleError = () => {
      setIsPlaying(false);
      setError('Le fichier audio attendu est indisponible. Cet exercice ne peut pas être poursuivi.');
      setAudioState('Le fichier audio est indisponible.');
    };
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    return () => {
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [currentStimulus?.id, currentQuestions.length]);

  const resetSession = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setAttempt(null);
    setDiagnostic(null);
    setStimuli([]);
    setItems([]);
    setStimulusIndex(0);
    setAnswers({});
    setPlayback(null);
    setIsPlaying(false);
    setAudioState('Prêt à écouter.');
    setStimulusStartedAt(null);
    setDiagnosticStartedAt(null);
    setResults(null);
    setReview(null);
    setRemediation(null);
    setError(null);
  };

  const startDiagnostic = async () => {
    if (!subjectId) {
      setError('Créez ou choisissez d’abord un parcours du domaine Langues.');
      return;
    }
    if (!listeningReady) {
      setError('Le diagnostic reste indisponible tant que les quatre actifs audio originaux ne sont pas publiés et vérifiés.');
      return;
    }
    try {
      setStarting(true);
      setError(null);
      const response = await axios.post(
        `${endpoint}/start`,
        { subject_id: Number(subjectId) },
        authConfig,
      );
      const payload = response.data;
      setAttempt(payload.attempt);
      setDiagnostic(payload.diagnostic);
      setStimuli(payload.stimuli || []);
      setItems(payload.items || []);
      setStimulusIndex(0);
      setAnswers({});
      setPlayback(null);
      setIsPlaying(false);
      setAudioState('Prêt à écouter. L’extrait ne pourra être lu qu’une seule fois.');
      const now = Date.now();
      setStimulusStartedAt(now);
      setDiagnosticStartedAt(now);
    } catch (requestError) {
      setError(requestError.response?.data?.message || requestError.message || 'Impossible de démarrer le diagnostic Listening avancé.');
    } finally {
      setStarting(false);
    }
  };

  const playCurrentStimulus = async () => {
    if (!attempt || !currentStimulus || playback || isPlaying) return;
    const audio = audioRef.current;
    if (!audio) return;
    try {
      setError(null);
      setAudioState('Autorisation de l’écoute unique en cours.');
      const playbackResponse = await axios.post(
        `/api/diagnostic/attempts/${attempt.id}/stimuli/${currentStimulus.id}/playback`,
        {},
        authConfig,
      );
      const nextPlayback = playbackResponse.data.playback;
      audio.src = nextPlayback.audio_url;
      setPlayback(nextPlayback);
      setAudioState('Lecture de l’extrait audio en cours.');
      await audio.play();
      setIsPlaying(true);
    } catch (requestError) {
      audio.pause();
      audio.currentTime = 0;
      setIsPlaying(false);
      setAudioState('La lecture n’a pas pu démarrer. L’écoute unique peut déjà être réservée.');
      setError(requestError.response?.data?.message || requestError.message || 'La lecture audio n’a pas pu être validée.');
    }
  };

  const stopCurrentStimulus = () => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    setIsPlaying(false);
    setAudioState('Lecture arrêtée. L’écoute unique reste considérée comme utilisée.');
  };

  const selectAnswer = (itemId, selectedIndex) => {
    if (!playback) return;
    setAnswers((current) => ({
      ...current,
      [itemId]: {
        ...current[itemId],
        selected_index: selectedIndex,
        response_time_seconds: stimulusStartedAt ? Math.max(0, (Date.now() - stimulusStartedAt) / 1000) : null,
      },
    }));
  };

  const selectConfidence = (itemId, confidence) => {
    if (!playback) return;
    setAnswers((current) => ({
      ...current,
      [itemId]: { ...current[itemId], confidence },
    }));
  };

  const loadReview = async (attemptId) => {
    const reviewResponse = await axios.get(`/api/diagnostic/attempts/${attemptId}/listening-review`, authConfig);
    setReview(reviewResponse.data);
  };

  const advanceStimulus = async () => {
    if (!playback || !currentAnswersComplete) return;
    if (stimulusIndex < stimuli.length - 1) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setStimulusIndex((current) => current + 1);
      setPlayback(null);
      setIsPlaying(false);
      setAudioState('Prêt à écouter. L’extrait ne pourra être lu qu’une seule fois.');
      setStimulusStartedAt(Date.now());
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const durationSeconds = diagnosticStartedAt ? Math.max(0, (Date.now() - diagnosticStartedAt) / 1000) : null;
      const responsePayload = items.map((item) => ({ item_id: item.id, ...answers[item.id] }));
      const submitResponse = await axios.post(
        `/api/diagnostic/attempts/${attempt.id}/submit`,
        { responses: responsePayload, duration_seconds: durationSeconds },
        authConfig,
      );
      setResults(submitResponse.data);
      await loadReview(attempt.id);
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

  if (loading) return <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Préparation du module Listening avancé…</div>;

  if (results) {
    const attemptResult = results.attempt;
    return (
      <div className="space-y-5">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
        <Card className="border-indigo-200 bg-indigo-50/60 shadow-sm">
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><CheckCircle2 className="h-5 w-5 text-indigo-700" />Résultats descriptifs d’écoute</CardTitle><CardDescription>{results.disclaimer}</CardDescription></CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Items corrects</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.correct_count} / {attemptResult.total_items}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Exactitude observée</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.accuracy === null ? '—' : `${Math.round(attemptResult.accuracy * 100)} %`}</p></div>
            <div className="rounded-xl bg-white p-4 shadow-sm"><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Temps observé</p><p className="mt-1 text-2xl font-bold text-slate-950">{attemptResult.duration_seconds ? `${Math.round(attemptResult.duration_seconds / 60)} min` : '—'}</p></div>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-sm">
          <CardHeader><CardTitle className="text-base">Réécoute guidée et transcription</CardTitle><CardDescription>Les scripts, les locuteurs et les corrections deviennent disponibles après la soumission, afin de soutenir l’auto-explication sans aider la première réponse.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            {(review?.review_stimuli || []).map((stimulus, index) => {
              return <div key={stimulus.stimulus_id} className="rounded-xl border border-slate-200 bg-slate-50 p-4"><div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><p className="font-semibold text-slate-900">Extrait {index + 1}</p>{stimulus.audio_url && <audio controls className="max-w-full" src={stimulus.audio_url}>Votre navigateur ne peut pas lire cet audio.</audio>}</div><div className="mt-3 space-y-2 text-sm leading-6 text-slate-800">{stimulus.speaker_transcript.map((line, lineIndex) => <p key={`${stimulus.stimulus_id}-${lineIndex}`}><span className="font-semibold">{line.speaker} :</span> {line.text}</p>)}</div><div className="mt-4 space-y-3">{stimulus.items.map((item) => <div key={item.item_id} className="rounded-lg border border-slate-200 bg-white p-3"><div className="flex items-center justify-between gap-3"><p className="text-sm font-semibold text-slate-900">Question</p><Badge variant={item.is_correct ? 'default' : 'outline'}>{item.is_correct ? 'Réponse correcte' : 'À revoir'}</Badge></div><p className="mt-2 text-sm text-slate-700"><span className="font-semibold">Correction :</span> {item.choices[item.correct_index]}</p><p className="mt-1 text-sm text-slate-600">{item.explanation}</p></div>)}</div></div>;
            })}
          </CardContent>
        </Card>

        {remediationTargets.length > 0 && <Card className="border-amber-200 bg-amber-50/50 shadow-sm"><CardHeader><CardTitle className="text-base">Cartes FSRS optionnelles</CardTitle><CardDescription>Seules les formulations atomiques et réutilisables disponibles dans vos erreurs peuvent être ajoutées aux révisions espacées.</CardDescription></CardHeader><CardContent>{!remediation ? <Button onClick={createRemediation} disabled={creatingRemediation} className="w-full bg-indigo-700 hover:bg-indigo-800">{creatingRemediation ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Création des cartes…</> : <><Sparkles className="mr-2 h-4 w-4" />Créer les cartes de remédiation FSRS</>}</Button> : <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900"><p className="font-semibold">{remediation.created_count} carte(s) créée(s).</p><p className="mt-1">Elles rejoignent les révisions FSRS du domaine Langues.</p></div>}</CardContent></Card>}
        <Button variant="outline" onClick={resetSession}><RotateCcw className="mr-2 h-4 w-4" />Faire un nouveau diagnostic</Button>
      </div>
    );
  }

  if (!attempt) {
    return (
      <div className="space-y-5">
        {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
        <Card className="border-slate-200 shadow-sm">
          <CardHeader><CardTitle className="flex items-center gap-2 text-lg"><Headphones className="h-5 w-5 text-indigo-700" />{metadata?.diagnostic?.title || 'Listening professionnel'}</CardTitle><CardDescription>{metadata?.diagnostic?.description || 'Extraits audio originaux avec une écoute autorisée par stimulus et une correction différée.'} Cette activité n’est pas un test TOEIC officiel.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            {languageSubjects.length ? <><div><label htmlFor={`shared-listening-subject-${moduleId}`} className="block text-sm font-semibold text-slate-800">Parcours de langue associé</label><select id={`shared-listening-subject-${moduleId}`} value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600">{languageSubjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>)}</select></div>{listeningReady ? <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-950"><p className="font-semibold">Module prêt</p><p className="mt-1">Les {metadata?.stimuli?.length || 0} stimuli audio sont disponibles ; leur transcription restera masquée jusqu’à la soumission.</p></div> : <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"><p className="font-semibold">Publication audio en cours</p><p className="mt-1">{unavailableAssets.length || metadata?.stimuli?.length || 0} stimulus(s) audio sont indisponibles. Le diagnostic reste fermé jusqu’à vérification complète.</p></div>}<Button onClick={startDiagnostic} disabled={starting || !listeningReady} className="w-full bg-indigo-700 hover:bg-indigo-800">{starting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Préparation…</> : <><ArrowRight className="mr-2 h-4 w-4" />Démarrer le diagnostic d’écoute</>}</Button></> : <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-700">Créez d’abord un parcours du domaine Langues pour rattacher vos résultats et vos remédiations à un objectif explicite.</div>}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-start"><div><CardTitle className="text-lg">Diagnostic d’écoute</CardTitle><CardDescription>{diagnostic?.title} · Extrait {stimulusIndex + 1} sur {stimuli.length} · {currentQuestions.length} question{currentQuestions.length > 1 ? 's' : ''}</CardDescription></div><Badge variant="outline">{currentStimulus?.task_type === 'listening_conversation' ? 'Conversation' : 'Présentation'}</Badge></div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-600 transition-[width] duration-200" style={{ width: `${((stimulusIndex + 1) / stimuli.length) * 100}%` }} /></div>
        </CardHeader>
        <CardContent className="space-y-5">
          <audio ref={audioRef} preload="none" aria-hidden="true" />
          <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-4"><p className="font-semibold text-indigo-950">Écoute unique par extrait</p><p className="mt-1 text-sm text-indigo-900">Écoutez l’extrait, puis choisissez A, B ou C pour chacune des {currentQuestions.length} questions. Les formulations et la transcription restent masquées jusqu’à la revue.</p><div className="mt-3 flex flex-wrap gap-2"><Button className="bg-indigo-700 hover:bg-indigo-800" onClick={playCurrentStimulus} disabled={Boolean(playback) || isPlaying} aria-describedby="shared-listening-audio-status"><Volume2 className="mr-2 h-4 w-4" />{playback ? 'Écoute utilisée' : 'Écouter l’extrait'}</Button>{isPlaying && <Button variant="outline" onClick={stopCurrentStimulus}><Square className="mr-2 h-4 w-4" />Arrêter l’écoute</Button>}</div><p id="shared-listening-audio-status" className="mt-3 text-sm text-indigo-900" aria-live="polite">{audioState}</p></div>
          <div className="space-y-4">{currentQuestions.map((item, questionIndex) => <div key={item.id} className="rounded-xl border border-slate-200 bg-white p-4"><div className="flex items-center justify-between gap-3"><p className="font-semibold text-slate-900">Question {questionIndex + 1}</p><Badge variant="outline">{targetLabels[item.target] || item.target}</Badge></div><p className="mt-2 text-sm text-slate-600">Choisissez la réponse la plus adaptée après votre écoute.</p><div className="mt-3 grid gap-2 sm:grid-cols-3">{(item.choice_labels || []).map((label, index) => <button type="button" key={label} onClick={() => selectAnswer(item.id, index)} disabled={!playback} className={`rounded-xl border p-4 text-left text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-50 ${answers[item.id]?.selected_index === index ? 'border-indigo-600 bg-indigo-50 text-indigo-950 ring-1 ring-indigo-600' : 'border-slate-200 bg-white text-slate-800 hover:border-indigo-300 hover:bg-slate-50'}`}><span className="text-indigo-700">Réponse {label}</span></button>)}</div><div className="mt-4"><p className="mb-2 text-sm font-semibold text-slate-800">Confiance <span className="font-normal text-slate-500">(facultatif)</span></p><div className="grid grid-cols-2 gap-2 sm:grid-cols-4">{confidenceLabels.map((option) => <button type="button" key={option.value} onClick={() => selectConfidence(item.id, option.value)} disabled={!playback} className={`rounded-lg border px-3 py-2 text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-50 ${answers[item.id]?.confidence === option.value ? 'border-indigo-600 bg-indigo-50 text-indigo-950' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'}`}>{option.label}</button>)}</div></div></div>)}</div>
          <div className="flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-center sm:justify-between"><p className="text-xs text-slate-500">La lecture et le temps sont des données de contrôle descriptives, pas des indicateurs de niveau.</p><Button onClick={advanceStimulus} disabled={!playback || !currentAnswersComplete || submitting} className="bg-indigo-700 hover:bg-indigo-800">{submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Analyse…</> : <>{stimulusIndex === stimuli.length - 1 ? 'Voir mes résultats' : 'Extrait suivant'}<ArrowRight className="ml-2 h-4 w-4" /></>}</Button></div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SharedListeningDiagnostic;
