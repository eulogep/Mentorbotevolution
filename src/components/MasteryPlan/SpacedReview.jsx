import { useEffect, useState } from 'react';
import axios from 'axios';
import { Brain, ChevronRight, Clock3, Lightbulb, Loader2, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';

const ratings = [
  { id: 'again', label: 'À revoir', hint: 'Je n’ai pas retrouvé la réponse', className: 'bg-rose-600 hover:bg-rose-700' },
  { id: 'hard', label: 'Difficile', hint: 'Je l’ai retrouvée avec effort', className: 'bg-amber-600 hover:bg-amber-700' },
  { id: 'good', label: 'Bien', hint: 'Je l’ai retrouvée avec une hésitation', className: 'bg-sky-700 hover:bg-sky-800' },
  { id: 'easy', label: 'Facile', hint: 'Je l’ai retrouvée immédiatement', className: 'bg-emerald-700 hover:bg-emerald-800' },
];

const SpacedReview = () => {
  const [loading, setLoading] = useState(true);
  const [cards, setCards] = useState([]);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [revealed, setRevealed] = useState(false);
  const [startedAt, setStartedAt] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  const current = cards[index];
  const remaining = Math.max(0, cards.length - index);

  const resetCurrentAttempt = () => {
    setAnswer('');
    setRevealed(false);
    setFeedback(null);
    setStartedAt(Date.now());
  };

  const loadDue = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get('/api/spaced-repetition/get-due-cards?limit=10');
      const data = response.data;
      if (data.status !== 'success') throw new Error(data.message || 'Récupération échouée');
      setCards(data.due_cards || []);
      setIndex(0);
      setAnswer('');
      setRevealed(false);
      setFeedback(null);
      setStartedAt(Date.now());
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDue(); }, []);

  const review = async (rating) => {
    if (!current || !revealed || feedback) return;
    try {
      setSubmitting(true);
      setError(null);
      const responseTime = startedAt ? Math.max(1, (Date.now() - startedAt) / 1000) : 0;
      const response = await axios.post('/api/spaced-repetition/review-card', {
        card_id: current.id,
        rating,
        response_time: responseTime,
      });
      const data = response.data;
      if (data.status !== 'success') throw new Error(data.message || 'Révision échouée');
      setFeedback({
        ...data.feedback,
        nextReviewAt: data.next_review_at,
        retentionTarget: data.retention_target,
        memoryState: data.memory_state,
      });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSubmitting(false);
    }
  };

  const nextCard = () => {
    if (index + 1 >= cards.length) {
      setIndex(cards.length);
      setFeedback(null);
      return;
    }
    setIndex((previous) => previous + 1);
    resetCurrentAttempt();
  };

  if (loading) {
    return <div className="flex items-center gap-2 text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Préparation de votre session…</div>;
  }

  if (error && !current) {
    return <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800">Erreur : {error}</div>;
  }

  if (!current) {
    return (
      <Card className="border-0 bg-gradient-to-br from-emerald-50 to-teal-50 shadow-lg">
        <CardContent className="p-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-700 text-white"><Brain className="h-6 w-6" /></div>
          <h3 className="text-lg font-semibold text-slate-900">Session terminée</h3>
          <p className="mx-auto mt-2 max-w-md text-sm text-slate-600">Les prochaines échéances ont été mises à jour à partir de vos rappels. Revenez lorsque de nouvelles cartes seront dues.</p>
          <Button className="mt-5" variant="outline" onClick={loadDue}><RotateCcw className="mr-2 h-4 w-4" />Actualiser</Button>
        </CardContent>
      </Card>
    );
  }

  const question = current.front_content || current.concept_name;
  const correction = current.back_content || 'Aucune correction n’a encore été renseignée pour cette carte.';

  return (
    <div className="space-y-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h3 className="flex items-center gap-2 text-lg font-semibold text-slate-900"><Brain className="h-5 w-5 text-indigo-700" />Session de rappel actif</h3>
          <p className="mt-1 text-sm text-slate-600">Essayez de retrouver la réponse avant de consulter la correction.</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="border-indigo-200 bg-indigo-50 text-indigo-800">{remaining} carte{remaining > 1 ? 's' : ''} restante{remaining > 1 ? 's' : ''}</Badge>
          <Button size="sm" variant="outline" onClick={loadDue}><RotateCcw className="mr-1 h-4 w-4" />Actualiser</Button>
        </div>
      </div>

      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}

      <Card className="border-0 shadow-xl">
        <CardHeader className="border-b border-slate-100 bg-slate-50/70">
          <div className="flex items-start justify-between gap-3">
            <div>
              <CardTitle className="text-base text-slate-900">{current.concept_name}</CardTitle>
              <CardDescription className="mt-1">Étape {index + 1} sur {cards.length}</CardDescription>
            </div>
            {current.tags?.slice(0, 2).map((tag) => <Badge key={tag} variant="outline">{tag}</Badge>)}
          </div>
        </CardHeader>
        <CardContent className="space-y-5 p-5 sm:p-6">
          <section aria-labelledby="question-title" className="rounded-2xl border border-indigo-100 bg-indigo-50 p-5">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-indigo-700">Question</div>
            <p id="question-title" className="text-base font-medium leading-relaxed text-slate-900">{question}</p>
          </section>

          {!revealed ? (
            <section aria-labelledby="answer-title">
              <label id="answer-title" className="mb-2 block text-sm font-semibold text-slate-800">Votre réponse, avec vos propres mots</label>
              <Textarea
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                placeholder="Écrivez ce dont vous vous souvenez avant de révéler la correction…"
                className="min-h-[120px] border-slate-200 focus-visible:ring-indigo-600"
              />
              <p className="mt-2 text-xs text-slate-500">Cette réponse reste locale à la session : seule votre évaluation et son temps alimentent le calendrier.</p>
              <Button className="mt-4 bg-indigo-700 hover:bg-indigo-800" onClick={() => setRevealed(true)}>Révéler la correction</Button>
            </section>
          ) : (
            <>
              <section aria-labelledby="correction-title" className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-emerald-800">Correction</div>
                <p id="correction-title" className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800">{correction}</p>
              </section>

              {!feedback ? (
                <section aria-labelledby="rating-title">
                  <div className="mb-3 flex items-center gap-2"><Clock3 className="h-4 w-4 text-slate-500" /><h4 id="rating-title" className="font-semibold text-slate-900">À quel point avez-vous retrouvé la réponse ?</h4></div>
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {ratings.map((rating) => (
                      <Button key={rating.id} disabled={submitting} onClick={() => review(rating.id)} className={`h-auto min-h-16 justify-start whitespace-normal px-4 py-3 text-left text-white ${rating.className}`}>
                        <span><span className="block font-semibold">{rating.label}</span><span className="mt-0.5 block text-xs text-white/85">{rating.hint}</span></span>
                      </Button>
                    ))}
                  </div>
                </section>
              ) : (
                <section className="rounded-2xl border border-sky-200 bg-sky-50 p-5" aria-live="polite">
                  <div className="flex gap-3"><Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-sky-700" /><div>
                    <p className="font-semibold text-sky-950">{feedback.message}</p>
                    <p className="mt-1 text-sm text-sky-800">{feedback.tip}</p>
                    <p className="mt-3 text-sm font-medium text-sky-950">{feedback.next_action}</p>
                    <p className="mt-1 text-xs text-sky-700">Rétention cible : {Math.round(feedback.retentionTarget * 100)} %. Stabilité estimée : {feedback.memoryState?.stability_days || '—'} jours.</p>
                  </div></div>
                  <Button className="mt-4" onClick={nextCard}>Carte suivante<ChevronRight className="ml-1 h-4 w-4" /></Button>
                </section>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SpacedReview;
