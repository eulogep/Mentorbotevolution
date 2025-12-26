import React, { useState } from 'react';
import { Target, Brain, Calendar, BookOpen, Zap, CheckCircle2, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';

const PlanGenerator = ({ analyzedDocuments, onPlanGenerated }) => {
  const [targetScore, setTargetScore] = useState([14]);
  const [timeframe, setTimeframe] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [studyTime, setStudyTime] = useState([2]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(null);

  const learningMethods = {
    visual: {
      name: 'Visuel',
      description: 'Cartes mentales, schémas, graphiques',
      icon: '👁️',
      techniques: ['Dual Coding', 'Méthode des Lieux', 'Cartes Conceptuelles']
    },
    auditory: {
      name: 'Auditif',
      description: 'Écoute, répétition orale, discussions',
      icon: '👂',
      techniques: ['Technique Feynman', 'Répétition Orale', 'Podcasts Éducatifs']
    },
    kinesthetic: {
      name: 'Kinesthésique',
      description: 'Manipulation, expérimentation, mouvement',
      icon: '✋',
      techniques: ['Apprentissage Actif', 'Simulations', 'Exercices Pratiques']
    },
    mixed: {
      name: 'Mixte',
      description: 'Combinaison de tous les styles',
      icon: '🧠',
      techniques: ['Approche Multimodale', 'Rotation des Méthodes', 'Adaptation Contextuelle']
    }
  };

  const generatePlan = async () => {
    setIsGenerating(true);
    
    // Simulation de génération de plan (remplacer par vraie API)
    await new Promise(resolve => setTimeout(resolve, 3000));

    const concepts = analyzedDocuments?.flatMap(doc => doc.concepts) || [
      'Grammaire avancée',
      'Vocabulaire business',
      'Compréhension orale',
      'Expression écrite'
    ];

    const plan = {
      id: Date.now(),
      targetScore: targetScore[0],
      timeframe,
      learningStyle,
      dailyStudyTime: studyTime[0],
      concepts: concepts.map((concept, index) => ({
        id: index + 1,
        name: concept,
        difficulty: Math.floor(Math.random() * 3) + 1, // 1-3
        estimatedTime: Math.floor(Math.random() * 10) + 5, // 5-15 heures
        progress: 0,
        methods: learningMethods[learningStyle]?.techniques || ['Répétition Espacée'],
        resources: {
          flashcards: Math.floor(Math.random() * 20) + 10,
          quizzes: Math.floor(Math.random() * 5) + 3,
          exercises: Math.floor(Math.random() * 8) + 5
        },
        schedule: generateSchedule(index, timeframe)
      })),
      milestones: generateMilestones(timeframe, targetScore[0]),
      totalEstimatedTime: concepts.length * 8, // Estimation
      successProbability: calculateSuccessProbability(targetScore[0], studyTime[0], timeframe)
    };

    setGeneratedPlan(plan);
    setIsGenerating(false);
    onPlanGenerated?.(plan);
  };

  const generateSchedule = (conceptIndex, timeframe) => {
    const weeks = parseInt(timeframe) || 12;
    const startWeek = Math.floor((conceptIndex / 4) * weeks) + 1;
    const endWeek = Math.min(startWeek + 3, weeks);
    
    return {
      startWeek,
      endWeek,
      sessionsPerWeek: 3,
      reviewSessions: [endWeek + 1, endWeek + 3, endWeek + 7]
    };
  };

  const generateMilestones = (timeframe, target) => {
    const weeks = parseInt(timeframe) || 12;
    const milestones = [];
    
    for (let i = 1; i <= 4; i++) {
      const week = Math.floor((weeks / 4) * i);
      const score = Math.floor((target / 4) * i) + 10;
      milestones.push({
        week,
        targetScore: score,
        description: `Évaluation intermédiaire ${i}`,
        concepts: Math.floor((generatedPlan?.concepts.length || 4) / 4 * i)
      });
    }
    
    return milestones;
  };

  const calculateSuccessProbability = (target, dailyTime, timeframe) => {
    const baseProb = 0.7;
    const timeBonus = Math.min(dailyTime * 0.1, 0.2);
    const targetPenalty = Math.max((target - 12) * 0.05, 0);
    const timeframePenalty = Math.max((16 - parseInt(timeframe)) * 0.02, 0);
    
    return Math.min(Math.max(baseProb + timeBonus - targetPenalty - timeframePenalty, 0.3), 0.95);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 1: return 'bg-green-100 text-green-800';
      case 2: return 'bg-yellow-100 text-yellow-800';
      case 3: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyLabel = (difficulty) => {
    switch (difficulty) {
      case 1: return 'Facile';
      case 2: return 'Moyen';
      case 3: return 'Difficile';
      default: return 'Inconnu';
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Générateur de Plan de Maîtrise
          </CardTitle>
          <CardDescription>
            Définissez vos objectifs pour générer un plan d'apprentissage personnalisé et adaptatif
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Objectif de note */}
          <div className="space-y-2">
            <Label className="text-base font-medium">Objectif de note</Label>
            <div className="px-4">
              <Slider
                value={targetScore}
                onValueChange={setTargetScore}
                max={20}
                min={10}
                step={0.5}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-500 mt-1">
                <span>10/20</span>
                <span className="font-medium text-blue-600">
                  {targetScore[0]}/20
                </span>
                <span>20/20</span>
              </div>
            </div>
          </div>

          {/* Délai */}
          <div className="space-y-2">
            <Label htmlFor="timeframe">Délai souhaité</Label>
            <Select value={timeframe} onValueChange={setTimeframe}>
              <SelectTrigger>
                <SelectValue placeholder="Sélectionnez une durée" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="4">4 semaines (intensif)</SelectItem>
                <SelectItem value="8">8 semaines (accéléré)</SelectItem>
                <SelectItem value="12">12 semaines (standard)</SelectItem>
                <SelectItem value="16">16 semaines (confortable)</SelectItem>
                <SelectItem value="24">24 semaines (progressif)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Style d'apprentissage */}
          <div className="space-y-2">
            <Label>Style d'apprentissage préféré</Label>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(learningMethods).map(([key, method]) => (
                <Card
                  key={key}
                  className={`cursor-pointer transition-all ${
                    learningStyle === key 
                      ? 'ring-2 ring-blue-500 bg-blue-50' 
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => setLearningStyle(key)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg">{method.icon}</span>
                      <span className="font-medium">{method.name}</span>
                    </div>
                    <p className="text-xs text-gray-600">{method.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Temps d'étude quotidien */}
          <div className="space-y-2">
            <Label className="text-base font-medium">Temps d'étude quotidien</Label>
            <div className="px-4">
              <Slider
                value={studyTime}
                onValueChange={setStudyTime}
                max={6}
                min={0.5}
                step={0.5}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-500 mt-1">
                <span>30min</span>
                <span className="font-medium text-blue-600">
                  {studyTime[0]}h/jour
                </span>
                <span>6h</span>
              </div>
            </div>
          </div>

          <Button 
            onClick={generatePlan} 
            disabled={!timeframe || !learningStyle || isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Brain className="h-4 w-4 mr-2 animate-pulse" />
                Génération du plan en cours...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Générer le Plan de Maîtrise
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Plan généré */}
      {generatedPlan && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              Plan de Maîtrise Généré
            </CardTitle>
            <CardDescription>
              Votre parcours personnalisé pour atteindre {generatedPlan.targetScore}/20
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Résumé du plan */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {generatedPlan.concepts.length}
                </div>
                <div className="text-sm text-blue-800">Concepts à maîtriser</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {generatedPlan.totalEstimatedTime}h
                </div>
                <div className="text-sm text-green-800">Temps estimé total</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {Math.round(generatedPlan.successProbability * 100)}%
                </div>
                <div className="text-sm text-purple-800">Probabilité de succès</div>
              </div>
            </div>

            {/* Concepts à maîtriser */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Concepts à Maîtriser</h3>
              <div className="space-y-3">
                {generatedPlan.concepts.map((concept) => (
                  <div key={concept.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{concept.name}</h4>
                      <Badge className={getDifficultyColor(concept.difficulty)}>
                        {getDifficultyLabel(concept.difficulty)}
                      </Badge>
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
                        <Badge key={index} variant="outline" className="text-xs">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Jalons */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Jalons de Progression</h3>
              <div className="space-y-2">
                {generatedPlan.milestones.map((milestone, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-bold">{milestone.week}</span>
                    </div>
                    <div className="flex-grow">
                      <div className="font-medium">{milestone.description}</div>
                      <div className="text-sm text-gray-600">
                        Objectif: {milestone.targetScore}/20 • {milestone.concepts} concepts maîtrisés
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                  </div>
                ))}
              </div>
            </div>

            <Button className="w-full" size="lg">
              <Calendar className="h-4 w-4 mr-2" />
              Commencer le Plan de Maîtrise
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PlanGenerator;

