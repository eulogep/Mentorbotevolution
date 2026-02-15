/**
 * PlanGenerator Component
 * Connexion backend: /api/analysis/generate-plan (JSON)
 */
import React, { useState } from 'react';
import axios from 'axios';
import { Target, Brain, Calendar, CheckCircle2, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';

const PlanGenerator = ({ analyzedDocuments = [], onPlanGenerated }) => {
  const [targetScore, setTargetScore] = useState([14]);
  const [timeframe, setTimeframe] = useState(''); // en semaines
  const [learningStyle, setLearningStyle] = useState('');
  const [studyTime, setStudyTime] = useState([2]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [error, setError] = useState(null);

  const learningMethods = {
    visual: { name: 'Visuel', icon: '👁️', techniques: ['Dual Coding', 'Méthode des Lieux', 'Cartes Conceptuelles'] },
    auditory: { name: 'Auditif', icon: '👂', techniques: ['Technique Feynman', 'Répétition Orale', 'Podcasts Éducatifs'] },
    kinesthetic: { name: 'Kinesthésique', icon: '✋', techniques: ['Apprentissage Actif', 'Simulations', 'Exercices Pratiques'] },
    mixed: { name: 'Mixte', icon: '🧠', techniques: ['Approche Multimodale', 'Rotation des Méthodes', 'Adaptation Contextuelle'] }
  };

  const convertWeeksToMonths = (weeks) => Math.max(1, Math.round(parseInt(weeks || '12', 10) / 4));

  const buildConceptsPayload = () => {
    if (analyzedDocuments.length > 0) {
      // extraire une liste unique des concepts avec difficulté/importance par défaut
      const setNames = new Set();
      const concepts = [];
      analyzedDocuments.forEach(doc => {
        (doc.concepts || []).forEach(name => {
          if (!setNames.has(name)) {
            setNames.add(name);
            concepts.push({ name, difficulty: 'medium', importance: 0.7 });
          }
        });
      });
      return concepts;
    }
    // fallback par défaut
    return [
      { name: 'Grammaire avancée', difficulty: 'medium', importance: 0.7 },
      { name: 'Vocabulaire business', difficulty: 'medium', importance: 0.8 },
      { name: 'Compréhension orale', difficulty: 'high', importance: 0.9 },
    ];
  };

  const generatePlan = async () => {
    if (!timeframe || !learningStyle) return;
    setIsGenerating(true);
    setError(null);

    try {
      const payload = {
        target_score: Math.round((targetScore[0] / 20) * 100),
        timeframe_months: convertWeeksToMonths(timeframe),
        daily_study_hours: studyTime[0],
        learning_style: learningStyle,
        chronotype: 'intermediate',
        concepts: buildConceptsPayload()
      };

      const res = await axios.post('/api/analysis/generate-plan', payload);

      const data = res.data;
      if (data.status !== 'success') throw new Error(data.message || 'Erreur génération');

      const plan = data.plan;
      const conceptsPlan = (plan.concepts_plan || []).map((c, idx) => ({
        id: idx + 1,
        name: c.name,
        difficulty: c.difficulty === 'high' ? 3 : c.difficulty === 'medium' ? 2 : 1,
        estimatedTime: c.estimated_hours || 6,
        progress: 0,
        methods: c.methods || learningMethods[learningStyle]?.techniques || ['Répétition Espacée'],
        resources: {
          flashcards: Math.max(10, Math.round((c.exercises_count || 20) * 0.4)),
          quizzes: Math.max(3, Math.round((c.exercises_count || 20) * 0.2)),
          exercises: Math.max(5, Math.round((c.exercises_count || 20) * 0.4))
        },
        schedule: { startWeek: 1, endWeek: 4, sessionsPerWeek: 3, reviewSessions: [5, 7, 11] }
      }));

      const uiPlan = {
        id: plan.id,
        targetScore: targetScore[0],
        timeframe,
        learningStyle,
        dailyStudyTime: studyTime[0],
        concepts: conceptsPlan,
        milestones: (plan.milestones || []).map((m, i) => ({
          week: (m.month || i + 1) * 4,
          targetScore: Math.round((payload.target_score / 4) * (i + 1)),
          description: m.key_objectives?.[0] || `Évaluation intermédiaire ${(i + 1)}`,
          concepts: m.target_concepts || 3
        })),
        totalEstimatedTime: plan.total_estimated_hours || conceptsPlan.length * 8,
        successProbability: plan.success_probability || 0.8
      };

      setGeneratedPlan(uiPlan);
      onPlanGenerated?.(uiPlan);
    } catch (e) {
      console.error(e);
      setError(e.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) { case 1: return 'bg-green-100 text-green-800'; case 2: return 'bg-yellow-100 text-yellow-800'; case 3: return 'bg-red-100 text-red-800'; default: return 'bg-gray-100 text-gray-800'; }
  };
  const getDifficultyLabel = (difficulty) => (difficulty === 1 ? 'Facile' : difficulty === 2 ? 'Moyen' : difficulty === 3 ? 'Difficile' : 'Inconnu');

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Target className="h-5 w-5" />Générateur de Plan de Maîtrise</CardTitle>
          <CardDescription>Définissez vos objectifs pour générer un plan d'apprentissage personnalisé et adaptatif</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Objectif */}
          <div className="space-y-2">
            <Label className="text-base font-medium">Objectif de note</Label>
            <div className="px-4">
              <Slider value={targetScore} onValueChange={setTargetScore} max={20} min={10} step={0.5} className="w-full" />
              <div className="flex justify-between text-sm text-gray-500 mt-1"><span>10/20</span><span className="font-medium text-blue-600">{targetScore[0]}/20</span><span>20/20</span></div>
            </div>
          </div>
          {/* Délai */}
          <div className="space-y-2">
            <Label htmlFor="timeframe">Délai souhaité</Label>
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger><SelectValue placeholder="Sélectionnez une durée" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="4">4 semaines (intensif)</SelectItem>
                <SelectItem value="8">8 semaines (accéléré)</SelectItem>
                <SelectItem value="12">12 semaines (standard)</SelectItem>
                <SelectItem value="16">16 semaines (confortable)</SelectItem>
                <SelectItem value="24">24 semaines (progressif)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {/* Style */}
          <div className="space-y-2">
            <Label>Style d'apprentissage préféré</Label>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(learningMethods).map(([key, method]) => (
                <Card key={key} className={`cursor-pointer transition-all ${learningStyle === key ? 'ring-2 ring-blue-500 bg-blue-50' : 'hover:bg-gray-50'}`} onClick={() => setLearningStyle(key)}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2"><span className="text-lg">{method.icon}</span><span className="font-medium">{method.name}</span></div>
                    <p className="text-xs text-gray-600">{method.techniques.join(', ')}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          {/* Temps d'étude */}
          <div className="space-y-2">
            <Label className="text-base font-medium">Temps d'étude quotidien</Label>
            <div className="px-4">
              <Slider value={studyTime} onValueChange={setStudyTime} max={6} min={0.5} step={0.5} className="w-full" />
              <div className="flex justify-between text-sm text-gray-500 mt-1"><span>30min</span><span className="font-medium text-blue-600">{studyTime[0]}h/jour</span><span>6h</span></div>
            </div>
          </div>
          <Button onClick={generatePlan} disabled={!timeframe || !learningStyle || isGenerating} className="w-full">
            {isGenerating ? (<><Brain className="h-4 w-4 mr-2 animate-pulse" />Génération du plan en cours...</>) : (<><Target className="h-4 w-4 mr-2" />Générer le Plan de Maîtrise</>)}
          </Button>
          {error && <p className="text-sm text-red-600">Erreur: {error}</p>}
        </CardContent>
      </Card>

      {generatedPlan && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><CheckCircle2 className="h-5 w-5 text-green-500" />Plan de Maîtrise Généré</CardTitle>
            <CardDescription>Votre parcours personnalisé pour atteindre {generatedPlan.targetScore}/20</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg"><div className="text-2xl font-bold text-blue-600">{generatedPlan.concepts.length}</div><div className="text-sm text-blue-800">Concepts à maîtriser</div></div>
              <div className="text-center p-4 bg-green-50 rounded-lg"><div className="text-2xl font-bold text-green-600">{generatedPlan.totalEstimatedTime}h</div><div className="text-sm text-green-800">Temps estimé total</div></div>
              <div className="text-center p-4 bg-purple-50 rounded-lg"><div className="text-2xl font-bold text-purple-600">{Math.round(generatedPlan.successProbability * 100)}%</div><div className="text-sm text-purple-800">Probabilité de succès</div></div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3">Concepts à Maîtriser</h3>
              <div className="space-y-3">
                {generatedPlan.concepts.map((concept) => (
                  <div key={concept.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{concept.name}</h4>
                      <Badge className={getDifficultyColor(concept.difficulty)}>{getDifficultyLabel(concept.difficulty)}</Badge>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600 mb-3">
                      <div>⏱️ {concept.estimatedTime}h</div>
                      <div>📚 {concept.resources.flashcards} flashcards</div>
                      <div>❓ {concept.resources.quizzes} quiz</div>
                      <div>✏️ {concept.resources.exercises} exercices</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Méthodes:</span>
                      {concept.methods.map((method, index) => (
                        <Badge key={index} variant="outline" className="text-xs">{method}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-3">Jalons de Progression</h3>
              <div className="space-y-2">
                {generatedPlan.milestones.map((milestone, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center"><span className="text-blue-600 font-bold">{milestone.week}</span></div>
                    <div className="flex-grow">
                      <div className="font-medium">{milestone.description}</div>
                      <div className="text-sm text-gray-600">Objectif: {milestone.targetScore}/20 • {milestone.concepts} concepts maîtrisés</div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>
            <Button className="w-full" size="lg"><Calendar className="h-4 w-4 mr-2" />Commencer le Plan de Maîtrise</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PlanGenerator;