/**
 * ValidationChecklist Component
 * 
 * Ajout: POST /api/analysis/update-progress à la validation
 */
import React, { useState } from 'react';
import axios from 'axios';
import { CheckCircle2, Circle, Star, Trophy, Brain, Target, MessageSquare, Users, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { Alert, AlertDescription } from '../ui/alert';

const ValidationChecklist = ({ concept = { id: 'concept_ui', name: 'Concept' }, onValidationComplete }) => {
  const [validationSteps, setValidationSteps] = useState([
    { id: 'understanding', title: 'Compréhension Théorique', description: 'Je peux expliquer ce concept dans mes propres mots', completed: false, required: true, icon: Brain, explanation: '' },
    { id: 'application', title: 'Application Pratique', description: 'Je peux utiliser ce concept dans des exercices', completed: false, required: true, icon: Target, score: 0 },
    { id: 'memorization', title: 'Mémorisation Long Terme', description: "Je me souviens de ce concept après 24h", completed: false, required: true, icon: Star, confidence: [7] },
    { id: 'transfer', title: 'Transfert de Connaissances', description: "Je peux appliquer ce concept à de nouveaux contextes", completed: false, required: false, icon: MessageSquare, examples: '' },
    { id: 'mastery', title: 'Maîtrise Complète', description: "Je peux enseigner ce concept à quelqu'un d'autre", completed: false, required: false, icon: Users, teaching: '' }
  ]);

  const [overallConfidence, setOverallConfidence] = useState([7]);
  const [showCelebration, setShowCelebration] = useState(false);
  const [saving, setSaving] = useState(false);
  const [serverMsg, setServerMsg] = useState(null);
  const [error, setError] = useState(null);

  const toggleStep = (stepId) => {
    setValidationSteps(prev => prev.map(step => step.id === stepId ? { ...step, completed: !step.completed } : step));
  };

  const updateStepData = (stepId, field, value) => {
    setValidationSteps(prev => prev.map(step => step.id === stepId ? { ...step, [field]: value } : step));
  };

  const getCompletionRate = () => {
    const requiredSteps = validationSteps.filter(step => step.required);
    const completedRequired = requiredSteps.filter(step => step.completed);
    return (completedRequired.length / requiredSteps.length) * 100;
  };

  const getOverallProgress = () => {
    const completed = validationSteps.filter(step => step.completed);
    return (completed.length / validationSteps.length) * 100;
  };

  const canValidate = () => {
    const requiredSteps = validationSteps.filter(step => step.required);
    return requiredSteps.every(step => step.completed);
  };

  const computePayload = () => {
    const application = validationSteps.find(s => s.id === 'application');
    const memorization = validationSteps.find(s => s.id === 'memorization');
    const mastery_level = getOverallProgress() / 100; // 0..1
    const retention_rate = (memorization?.confidence?.[0] || 7) / 10; // 0..1
    // temps approximatif selon l'activité
    const time_spent = Math.round(5 + (application?.score || 0) / 5 + (overallConfidence[0]));

    return {
      concept_id: concept?.id || concept?.name || 'concept_ui',
      mastery_level,
      retention_rate,
      time_spent,
    };
  };

  const validateConcept = async () => {
    if (!canValidate()) return;

    const validationData = {
      conceptId: concept?.id || concept?.name || 'concept_ui',
      completionRate: getCompletionRate(),
      overallProgress: getOverallProgress(),
      confidence: overallConfidence[0],
      steps: validationSteps,
      timestamp: new Date().toISOString()
    };

    setShowCelebration(true);
    setTimeout(() => setShowCelebration(false), 3000);
    onValidationComplete?.(validationData);

    // Envoi backend
    try {
      setSaving(true); setError(null); setServerMsg(null);
      const payload = computePayload();
      const res = await axios.post('/api/analysis/update-progress', payload);
      const data = res.data;
      if (data.status !== 'success') throw new Error(data.message || 'Mise à jour échouée');
      setServerMsg(`Prochaine révision: ${new Date(data.updated_concept.next_review).toLocaleString()}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const getStepIcon = (step) => {
    const IconComponent = step.icon; return <IconComponent className="h-5 w-5" />;
  };

  const renderStepContent = (step) => {
    switch (step.id) {
      case 'understanding':
        return (
          <div className="mt-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Expliquez ce concept avec vos propres mots (Technique Feynman):</label>
            <Textarea placeholder="Décrivez le concept comme si vous l'expliquiez à un enfant de 10 ans..." value={step.explanation || ''} onChange={(e) => updateStepData(step.id, 'explanation', e.target.value)} className="min-h-[100px]" />
          </div>
        );
      case 'application':
        return (
          <div className="mt-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Score aux exercices pratiques:</label>
            <div className="px-4">
              <Slider value={[step.score || 0]} onValueChange={(value) => updateStepData(step.id, 'score', value[0])} max={100} min={0} step={5} className="w-full" />
              <div className="flex justify-between text-sm text-gray-500 mt-1"><span>0%</span><span className="font-medium text-blue-600">{step.score || 0}%</span><span>100%</span></div>
            </div>
            {step.score >= 80 && (<Badge className="mt-2 bg-green-100 text-green-800">Excellent! Objectif atteint (≥80%)</Badge>)}
          </div>
        );
      case 'memorization':
        return (
          <div className="mt-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Niveau de confiance dans votre mémorisation:</label>
            <div className="px-4">
              <Slider value={step.confidence || [7]} onValueChange={(value) => updateStepData(step.id, 'confidence', value)} max={10} min={1} step={1} className="w-full" />
              <div className="flex justify-between text-sm text-gray-500 mt-1"><span>Faible</span><span className="font-medium text-blue-600">{step.confidence?.[0] || 7}/10</span><span>Excellent</span></div>
            </div>
          </div>
        );
      case 'transfer':
        return (
          <div className="mt-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Donnez des exemples d'application dans d'autres contextes:</label>
            <Textarea placeholder="Comment pourriez-vous utiliser ce concept dans d'autres situations?" value={step.examples || ''} onChange={(e) => updateStepData(step.id, 'examples', e.target.value)} />
          </div>
        );
      case 'mastery':
        return (
          <div className="mt-3">
            <label className="text-sm font-medium text-gray-700 mb-2 block">Comment enseigneriez-vous ce concept?</label>
            <Textarea placeholder="Décrivez votre approche pédagogique pour enseigner ce concept..." value={step.teaching || ''} onChange={(e) => updateStepData(step.id, 'teaching', e.target.value)} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {showCelebration && (
        <Alert className="border-green-200 bg-green-50">
          <Trophy className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">🎉 Félicitations! Vous avez validé la maîtrise de ce concept!</AlertDescription>
        </Alert>
      )}

      {serverMsg && (
        <Alert className="border-blue-200 bg-blue-50">
          <AlertDescription className="text-blue-800">{serverMsg}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-700">Erreur: {error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><CheckCircle2 className="h-5 w-5" />Validation de Maîtrise: {concept?.name || 'Concept'}</CardTitle>
          <CardDescription>Validez votre compréhension étape par étape pour confirmer la maîtrise complète</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2"><span className="text-sm font-medium">Progression globale</span><span className="text-sm text-gray-500">{Math.round(getOverallProgress())}%</span></div>
            <Progress value={getOverallProgress()} className="w-full" />
          </div>

          <div className="space-y-4">
            {validationSteps.map((step) => (
              <Card key={step.id} className={`transition-all ${step.completed ? 'bg-green-50 border-green-200' : 'hover:bg-gray-50'}`}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <button onClick={() => toggleStep(step.id)} className="mt-1 flex-shrink-0">
                      {step.completed ? (<CheckCircle2 className="h-6 w-6 text-green-500" />) : (<Circle className="h-6 w-6 text-gray-400 hover:text-gray-600" />)}
                    </button>
                    <div className="flex-grow">
                      <div className="flex items-center gap-2 mb-1">{getStepIcon(step)}<h3 className={`font-medium ${step.completed ? 'text-green-800' : 'text-gray-900'}`}>{step.title}{step.required && (<Badge variant="outline" className="ml-2 text-xs">Requis</Badge>)}</h3></div>
                      <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                      {renderStepContent(step)}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <label className="text-sm font-medium text-blue-900 mb-3 block">Niveau de confiance global dans votre maîtrise:</label>
            <div className="px-4">
              <Slider value={overallConfidence} onValueChange={setOverallConfidence} max={10} min={1} step={1} className="w-full" />
              <div className="flex justify-between text-sm text-blue-700 mt-1"><span>Pas confiant</span><span className="font-medium">{overallConfidence[0]}/10</span><span>Très confiant</span></div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm font-medium">Étapes requises: {Math.round(getCompletionRate())}%</p>
                <p className="text-xs text-gray-500">Toutes les étapes requises doivent être complétées</p>
              </div>
              <Badge className={canValidate() ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}>{canValidate() ? 'Prêt à valider' : 'En cours'}</Badge>
            </div>
            <Button onClick={validateConcept} disabled={!canValidate() || saving} className="w-full" size="lg">
              {saving ? (<><Loader2 className="h-4 w-4 mr-2 animate-spin" />Sauvegarde...</>) : (<><Trophy className="h-4 w-4 mr-2" />Valider la Maîtrise du Concept</>)}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ValidationChecklist;