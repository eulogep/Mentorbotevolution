import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Brain, CheckCircle, HelpCircle, Loader2, Sparkles, AlertCircle } from 'lucide-react';

const qualityButtons = [
  { val: 0, label: "0 — Oublié", color: "bg-red-100 text-red-800 border-red-200 hover:bg-red-200" },
  { val: 1, label: "1 — Très difficile", color: "bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200" },
  { val: 2, label: "2 — Difficile", color: "bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200" },
  { val: 3, label: "3 — Moyen", color: "bg-yellow-100 text-yellow-800 border-yellow-200 hover:bg-yellow-200" },
  { val: 4, label: "4 — Bien", color: "bg-green-100 text-green-800 border-green-200 hover:bg-green-200" },
  { val: 5, label: "5 — Parfait", color: "bg-emerald-100 text-emerald-800 border-emerald-200 hover:bg-emerald-200" }
];

const FlashcardReviewSession = () => {
  const [loading, setLoading] = useState(true);
  const [cards, setCards] = useState([]);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sessionFinished, setSessionFinished] = useState(false);
  const [error, setError] = useState(null);

  const fetchCards = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get('/api/spaced-repetition/review-cards');
      if (res.data && res.data.status === 'success') {
        setCards(res.data.cards || []);
      } else {
        throw new Error(res.data?.message || "Erreur lors du chargement des cartes.");
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Erreur réseau.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  const handleStartSession = () => {
    if (cards.length === 0) return;
    setSessionStarted(true);
    setCurrentIndex(0);
    setShowAnswer(false);
    setSessionFinished(false);
  };

  const handleScoreCard = async (quality) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    const currentCard = cards[currentIndex];

    try {
      const res = await axios.post(`/api/spaced-repetition/review-cards/${currentCard.id}/answer`, {
        quality: quality
      });

      if (res.data && res.data.status === 'success') {
        // Passer à la carte suivante ou terminer la session
        if (currentIndex < cards.length - 1) {
          setShowAnswer(false);
          setCurrentIndex(prev => prev + 1);
        } else {
          setSessionFinished(true);
          setSessionStarted(false);
        }
      } else {
        throw new Error(res.data?.message || "Erreur lors de l'enregistrement du score.");
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Erreur de connexion.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setSessionStarted(false);
    setSessionFinished(false);
    setCurrentIndex(0);
    setShowAnswer(false);
    fetchCards();
  };

  if (loading) {
    return (
      <Card className="border-0 shadow-lg p-8 text-center flex flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 text-purple-600 animate-spin" />
        <span className="text-sm font-semibold text-gray-600">Chargement de votre session de révision...</span>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-0 shadow-lg p-8 text-center flex flex-col items-center justify-center gap-3 border-red-100 bg-red-50/50">
        <AlertCircle className="h-8 w-8 text-red-600" />
        <span className="text-sm font-semibold text-red-800">Erreur : {error}</span>
        <Button variant="outline" onClick={fetchCards} className="mt-2">Recharger</Button>
      </Card>
    );
  }

  if (!sessionStarted && !sessionFinished) {
    return (
      <Card className="border-0 shadow-2xl bg-gradient-to-br from-white/90 to-purple-50/50 backdrop-blur-xl rounded-2xl overflow-hidden p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-600 text-white rounded-xl shadow-md">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Réviser mes flashcards</h3>
            <p className="text-xs text-gray-500 font-medium">
              Reprends les cartes sauvegardées depuis tes documents analysés.
            </p>
          </div>
        </div>

        <CardContent className="p-0 text-center space-y-6 py-6">
          <div className="max-w-md mx-auto space-y-3">
            <p className="text-sm text-gray-600 font-medium">
              Vous avez <span className="font-bold text-purple-700">{cards.length}</span> carte{cards.length > 1 ? 's' : ''} disponible{cards.length > 1 ? 's' : ''} pour cette session.
            </p>
            {cards.length === 0 ? (
              <div className="p-4 bg-yellow-50 border border-yellow-100 rounded-xl text-xs text-yellow-800 font-medium">
                Aucune flashcard sauvegardée disponible. Importez des documents d'abord !
              </div>
            ) : (
              <Button 
                onClick={handleStartSession}
                className="w-full bg-purple-700 hover:bg-purple-800 text-white py-3 font-semibold rounded-xl shadow-lg shadow-purple-100 transition-all duration-200 flex items-center justify-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                Commencer la révision
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (sessionFinished) {
    return (
      <Card className="border-0 shadow-2xl bg-gradient-to-br from-white/90 to-purple-50/50 backdrop-blur-xl rounded-2xl overflow-hidden p-6 text-center space-y-6">
        <div className="flex flex-col items-center gap-3 py-6">
          <div className="p-4 bg-green-100 text-green-700 rounded-full shadow-inner mb-2">
            <CheckCircle className="h-10 w-10" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900">Session terminée !</h3>
          <p className="text-sm font-semibold text-gray-600">
            Félicitations, vous avez révisé <span className="font-bold text-purple-700">{cards.length}</span> carte{cards.length > 1 ? 's' : ''} avec succès.
          </p>
          <div className="text-[10px] text-gray-400 font-medium bg-white/70 px-4 py-1.5 border border-purple-100/20 rounded-full shadow-sm">
            Algorithme de répétition espacée (SM-2 local)
          </div>
        </div>

        <Button 
          onClick={handleReset}
          className="w-full max-w-xs bg-purple-700 hover:bg-purple-800 text-white font-semibold py-2.5 rounded-xl shadow-lg transition-all duration-200"
        >
          Nouvelle Session / Rafraîchir
        </Button>
      </Card>
    );
  }

  const currentCard = cards[currentIndex];
  const progressValue = ((currentIndex + 1) / cards.length) * 100;

  return (
    <Card className="border-0 shadow-2xl bg-gradient-to-br from-white/90 to-purple-50/50 backdrop-blur-xl rounded-2xl overflow-hidden p-6 space-y-6">
      {/* Session Progress */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs font-bold text-purple-900">
          <span>RÉVISION EN COURS</span>
          <span>{currentIndex + 1} / {cards.length}</span>
        </div>
        <Progress value={progressValue} className="h-2 w-full bg-purple-100" />
      </div>

      {/* Card Content Display */}
      <div className="bg-white border border-purple-100/50 rounded-2xl p-6 min-h-[160px] flex flex-col justify-between shadow-sm relative overflow-hidden">
        <div className="absolute top-4 right-4">
          <Badge className="bg-purple-50 text-purple-700 border border-purple-100 text-[10px] font-bold rounded-full uppercase">
            {currentCard.difficulty || "medium"}
          </Badge>
        </div>

        <div className="space-y-4 pr-12">
          <div>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Concept : {currentCard.concept_name}</span>
            <p className="text-lg font-extrabold text-gray-900 leading-snug">
              {currentCard.front_content || currentCard.question}
            </p>
          </div>

          {showAnswer && (
            <div className="pt-4 border-t border-purple-50 text-left">
              <span className="text-[10px] font-bold text-purple-400 uppercase tracking-widest block mb-1">Réponse</span>
              <p className="text-sm font-semibold text-gray-700 leading-relaxed bg-purple-50/30 p-3 border border-purple-100/20 rounded-xl">
                {currentCard.back_content || currentCard.answer}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Control Buttons */}
      <div className="space-y-4">
        {!showAnswer ? (
          <Button 
            onClick={() => setShowAnswer(true)}
            className="w-full bg-purple-700 hover:bg-purple-800 text-white py-3 font-semibold rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            <HelpCircle className="h-4 w-4" />
            Révéler la réponse
          </Button>
        ) : (
          <div className="space-y-3">
            <p className="text-center text-xs font-bold text-purple-950 uppercase tracking-wider">
              Comment évaluez-vous votre réponse ?
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {qualityButtons.map(btn => (
                <button
                  key={btn.val}
                  disabled={isSubmitting}
                  onClick={() => handleScoreCard(btn.val)}
                  className={`border py-2 px-3 rounded-xl text-xs font-bold transition-all duration-200 text-center ${btn.color} ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default FlashcardReviewSession;
