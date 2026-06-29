import React, { useState } from 'react';
import { BookOpen, Brain, Sparkles, HelpCircle, Calendar, ShieldCheck, ChevronDown, ChevronUp, FolderPlus, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

const LearningPipelineDisplay = ({ pipeline, filename, onSaveFlashcards }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null); // 'success', 'error', or null
  const [saveMessage, setSaveMessage] = useState('');

  if (!pipeline) return null;

  const {
    document_summary = "Aucun résumé disponible.",
    concepts = [],
    flashcards = [],
    revision_plan = [],
    is_simulated = false,
    pipeline_version = "0.1"
  } = pipeline;

  const handleSaveClick = async () => {
    if (!onSaveFlashcards || isSaving) return;
    setIsSaving(true);
    setSaveStatus(null);
    setSaveMessage('');
    try {
      const res = await onSaveFlashcards(flashcards);
      if (res && res.status === 'success') {
        setSaveStatus('success');
        if (res.skipped_count > 0) {
          setSaveMessage(`${res.saved_count} flashcards sauvegardées, ${res.skipped_count} ignorée(s) car déjà présente(s) ou invalide(s).`);
        } else {
          setSaveMessage(`${res.saved_count} flashcards sauvegardées avec succès !`);
        }
      } else {
        setSaveStatus('error');
        setSaveMessage(res?.message || "Une erreur est survenue lors de la sauvegarde.");
      }
    } catch (err) {
      setSaveStatus('error');
      setSaveMessage(err.message || "Une erreur réseau est survenue.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className="border-0 shadow-2xl bg-gradient-to-br from-white/90 to-purple-50/50 backdrop-blur-xl rounded-2xl overflow-hidden mt-6 transition-all duration-300 hover:shadow-purple-100">
      <CardHeader className="border-b border-purple-100/50 bg-white/40 pb-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-purple-600 text-white rounded-xl shadow-md shadow-purple-200">
              <Brain className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold bg-gradient-to-r from-purple-900 to-indigo-950 bg-clip-text text-transparent">
                Pipeline d'Apprentissage
              </CardTitle>
              <CardDescription className="text-xs font-medium text-purple-600/80">
                Document : {filename || "Inconnu"} (v{pipeline_version})
              </CardDescription>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {is_simulated && (
              <Badge variant="secondary" className="bg-purple-100/80 text-purple-800 border-purple-200/50 py-1 px-3 flex items-center gap-1.5 rounded-full font-semibold text-xs shadow-sm">
                <ShieldCheck className="h-3.5 w-3.5" />
                Mode heuristique local — aucune IA externe utilisée
              </Badge>
            )}

            {flashcards.length > 0 && onSaveFlashcards && (
              <Button
                size="sm"
                onClick={handleSaveClick}
                disabled={isSaving}
                className="bg-purple-700 hover:bg-purple-800 text-white font-bold py-1 px-3 rounded-full flex items-center gap-1.5 shadow transition-all duration-200"
              >
                {isSaving ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <FolderPlus className="h-3.5 w-3.5" />
                )}
                Sauvegarder les flashcards
              </Button>
            )}

            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1.5 hover:bg-purple-50 rounded-lg text-purple-700 transition-colors"
            >
              {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="p-6 space-y-6">
          {/* Status Alert */}
          {saveStatus && (
            <div className={`p-4 rounded-xl flex items-start gap-3 border ${
              saveStatus === 'success' 
                ? 'bg-green-50 border-green-200 text-green-800' 
                : 'bg-red-50 border-red-200 text-red-800'
            }`}>
              {saveStatus === 'success' ? (
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              )}
              <div>
                <p className="text-sm font-bold">
                  {saveStatus === 'success' ? 'Sauvegarde réussie' : 'Erreur de sauvegarde'}
                </p>
                <p className="text-xs font-medium mt-0.5">{saveMessage}</p>
              </div>
            </div>
          )}

          {/* Résumé du Document */}
          <div className="space-y-2 p-4 bg-white/60 border border-purple-50 rounded-xl shadow-sm">
            <h3 className="text-sm font-semibold text-purple-950 flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-purple-600" />
              Résumé du Document
            </h3>
            <p className="text-sm text-gray-700 leading-relaxed font-medium">
              {document_summary}
            </p>
          </div>

          {/* Concepts Détectés */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-purple-950 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-600" />
              Concepts Détectés ({concepts.length})
            </h3>
            {concepts.length === 0 ? (
              <p className="text-sm text-gray-500 italic pl-6">Aucun concept extrait.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {concepts.map((concept, idx) => (
                  <div key={idx} className="p-4 bg-white border border-purple-100/50 rounded-xl hover:border-purple-200 transition-all duration-200 shadow-sm flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-sm text-gray-900">{concept.title}</span>
                        <Badge className="bg-indigo-50 text-indigo-700 border border-indigo-100 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          Confiance : {Math.round((concept.confidence || 0.7) * 100)}%
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {concept.description}
                      </p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-gray-50 flex items-center justify-between text-[10px] text-gray-400">
                      <span>Source: {concept.source || "heuristic"}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Flashcards Générées */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-purple-950 flex items-center gap-2">
              <HelpCircle className="h-4 w-4 text-purple-600" />
              Flashcards Générées ({flashcards.length})
            </h3>
            {flashcards.length === 0 ? (
              <p className="text-sm text-gray-500 italic pl-6">Aucune flashcard générée.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {flashcards.map((card, idx) => (
                  <div key={idx} className="bg-gradient-to-br from-white to-purple-50/20 border border-purple-100/50 rounded-xl overflow-hidden shadow-sm flex flex-col">
                    <div className="p-3.5 bg-purple-50/50 border-b border-purple-100/30 flex items-center justify-between">
                      <span className="text-xs font-bold text-purple-900">Concept: {card.concept_name}</span>
                      <Badge className="bg-purple-100/70 text-purple-900 hover:bg-purple-100 text-[9px] font-bold uppercase rounded-full">
                        {card.difficulty || "medium"}
                      </Badge>
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Question</p>
                        <p className="text-sm font-bold text-gray-900 mb-3">{card.question}</p>
                        
                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Réponse</p>
                        <p className="text-xs text-gray-700 leading-relaxed font-medium bg-white/80 p-2.5 border border-purple-100/10 rounded-lg">
                          {card.answer}
                        </p>
                      </div>
                      <div className="text-[10px] text-gray-400 self-end">
                        Source: {card.source || "heuristic"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Plan de Révision */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-purple-950 flex items-center gap-2">
              <Calendar className="h-4 w-4 text-purple-600" />
              Plan de Révision Espacée
            </h3>
            {revision_plan.length === 0 ? (
              <p className="text-sm text-gray-500 italic pl-6">Aucun plan de révision généré.</p>
            ) : (
              <div className="space-y-4">
                {revision_plan.map((plan, idx) => (
                  <div key={idx} className="p-4 bg-white border border-purple-100/30 rounded-xl shadow-sm space-y-3">
                    <h4 className="text-sm font-bold text-indigo-950 border-l-2 border-purple-600 pl-2">
                      {plan.concept_name}
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
                      {(plan.schedule || []).map((step, sIdx) => (
                        <div key={sIdx} className="p-3 bg-purple-50/30 border border-purple-100/20 rounded-lg text-center flex flex-col justify-between gap-1">
                          <span className="text-[10px] font-bold text-purple-700">Étape {step.review_step}</span>
                          <span className="text-xs font-bold text-gray-800">dans {step.interval_days} jour{step.interval_days > 1 ? 's' : ''}</span>
                          <span className="text-[9px] text-gray-400">Cible: {Math.round((step.target_confidence || 0.7) * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default LearningPipelineDisplay;
