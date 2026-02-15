import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Loader2, RotateCcw, ChevronRight } from 'lucide-react';

const qualities = [0, 1, 2, 3, 4, 5];

const SpacedReview = () => {
  const [loading, setLoading] = useState(true);
  const [cards, setCards] = useState([]);
  const [index, setIndex] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  const loadDue = async () => {
    try {
      setLoading(true); setError(null);
      const res = await axios.get('/api/spaced-repetition/get-due-cards?limit=10');
      const data = res.data;
      if (data.status !== 'success') throw new Error(data.message || 'Récupération échouée');
      setCards(data.due_cards || []); setIndex(0); setFeedback(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDue(); }, []);

  const current = cards[index];

  const review = async (q) => {
    if (!current) return;
    try {
      setSubmitting(true); setFeedback(null);
      const res = await axios.post('/api/spaced-repetition/review-card', {
        card_id: current.id,
        quality_response: q,
        current_interval: current.interval || 1,
        current_easiness: current.easiness_factor || 2.5,
        review_count: current.review_count || 0,
        success_rate: current.success_rate || 0.0,
        average_response_time: current.average_response_time || 0.0,
        response_time: 5
      });
      const data = res.data;
      if (data.status !== 'success') throw new Error(data.message || 'Révision échouée');
      setFeedback(data.feedback);
      // passer à la carte suivante après une courte pause
      setTimeout(() => setIndex(prev => Math.min(prev + 1, cards.length - 1)), 800);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Répétition Espacée</h3>
        <Button size="sm" variant="outline" onClick={loadDue}><RotateCcw className="h-4 w-4 mr-1" />Rafraîchir</Button>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-gray-600"><Loader2 className="h-4 w-4 animate-spin" />Chargement...</div>
      ) : error ? (
        <div className="text-red-600 text-sm">Erreur: {error}</div>
      ) : cards.length === 0 ? (
        <Card><CardContent className="p-6 text-center">Aucune carte due pour le moment 🎉</CardContent></Card>
      ) : (
        <Card className="border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>{current.concept_name}</span>
              <Badge variant="outline" className="text-xs">{index + 1}/{cards.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-700">{current.content}</div>
            <div className="grid grid-cols-6 gap-2">
              {qualities.map(q => (
                <Button key={q} disabled={submitting} onClick={() => review(q)} className={`${q >= 4 ? 'bg-green-600 hover:bg-green-700' : q === 3 ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-red-500 hover:bg-red-600'} text-white`}>{q}</Button>
              ))}
            </div>
            {feedback && (
              <div className="p-3 bg-blue-50 rounded-lg text-sm">
                <div className="font-medium">{feedback.message}</div>
                {feedback.encouragement && <div className="text-blue-700">{feedback.encouragement}</div>}
                {feedback.tips && feedback.tips.length > 0 && (
                  <ul className="list-disc pl-5 text-blue-700 mt-1">
                    {feedback.tips.map((t, i) => (<li key={i}>{t}</li>))}
                  </ul>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
      {cards.length > 0 && index < cards.length - 1 && (
        <div className="text-right text-sm text-gray-500 flex items-center justify-end"><ChevronRight className="h-4 w-4 mr-1" />Carte suivante...</div>
      )}
    </div>
  );
};

export default SpacedReview;