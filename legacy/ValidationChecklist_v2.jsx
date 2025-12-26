import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  Circle, 
  Star, 
  Trophy, 
  Brain, 
  Target, 
  MessageSquare, 
  Users, 
  Clock,
  Lightbulb,
  BookOpen,
  Zap,
  Award,
  AlertCircle,
  Timer,
  Calendar
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { Alert, AlertDescription } from '../ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

const ValidationChecklist = ({ subjects }) => {
  const [selectedConcept, setSelectedConcept] = useState(null);
  const [validationSteps, setValidationSteps] = useState([]);
  const [spacedRepetitionSchedule, setSpacedRepetitionSchedule] = useState([]);
  const [showCelebration, setShowCelebration] = useState(false);
  const [activeValidation, setActiveValidation] = useState(null);

  useEffect(() => {
    if (selectedConcept) {
      initializeValidationSteps();
      generateSpacedRepetitionSchedule();
    }
  }, [selectedConcept]);

  const initializeValidationSteps = () => {
    const steps = [
      {
        id: 'theoretical',
        title: 'Compréhension Théorique',
        description: 'Expliquer le concept avec ses propres mots',
        level: 1,
        required: true,
        icon: Brain,
        color: 'blue',
        completed: false,
        confidence: [5],
        explanation: '',
        timeSpent: 0,
        attempts: 0,
        criteria: [
          'Définition claire et précise',
          'Identification des éléments clés',
          'Compréhension du contexte d\'utilisation'
        ]
      },
      {
        id: 'practical',
        title: 'Application Pratique',
        description: 'Résoudre des exercices utilisant ce concept',
        level: 2,
        required: true,
        icon: Target,
        color: 'green',
        completed: false,
        confidence: [5],
        exerciseScore: 0,
        exercisesCompleted: 0,
        timeSpent: 0,
        attempts: 0,
        criteria: [
          'Résolution correcte d\'exercices simples',
          'Application des règles appropriées',
          'Reconnaissance des patterns'
        ]
      },
      {
        id: 'memorization',
        title: 'Mémorisation Durable',
        description: 'Se souvenir du concept après 24h sans révision',
        level: 3,
        required: true,
        icon: Clock,
        color: 'purple',
        completed: false,
        confidence: [5],
        lastReview: null,
        retentionRate: 0,
        timeSpent: 0,
        attempts: 0,
        criteria: [
          'Rappel immédiat sans aide',
          'Rétention après 24h',
          'Stabilité de la mémorisation'
        ]
      },
      {
        id: 'transfer',
        title: 'Transfert de Connaissances',
        description: 'Appliquer le concept dans de nouveaux contextes',
        level: 4,
        required: false,
        icon: Zap,
        color: 'orange',
        completed: false,
        confidence: [5],
        transferExamples: '',
        creativityScore: 0,
        timeSpent: 0,
        attempts: 0,
        criteria: [
          'Application à des situations nouvelles',
          'Adaptation créative du concept',
          'Connexions avec d\'autres domaines'
        ]
      },
      {
        id: 'mastery',
        title: 'Maîtrise Complète',
        description: 'Enseigner le concept à quelqu\'un d\'autre',
        level: 5,
        required: false,
        icon: Users,
        color: 'red',
        completed: false,
        confidence: [5],
        teachingExplanation: '',
        pedagogicalQuality: 0,
        timeSpent: 0,
        attempts: 0,
        criteria: [
          'Explication claire et pédagogique',
          'Anticipation des difficultés',
          'Capacité à répondre aux questions'
        ]
      }
    ];
    setValidationSteps(steps);
  };

  const generateSpacedRepetitionSchedule = () => {
    const now = new Date();
    const schedule = [
      { interval: 1, date: new Date(now.getTime() + 24 * 60 * 60 * 1000), completed: false },
      { interval: 3, date: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000), completed: false },
      { interval: 7, date: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000), completed: false },
      { interval: 14, date: new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000), completed: false },
      { interval: 30, date: new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000), completed: false }
    ];
    setSpacedRepetitionSchedule(schedule);
  };

  const toggleStep = (stepId) => {
    setValidationSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { 
            ...step, 
            completed: !step.completed,
            attempts: step.attempts + 1,
            timeSpent: step.timeSpent + Math.floor(Math.random() * 10) + 5 // Simulation
          }
        : step
    ));
  };

  const updateStepData = (stepId, field, value) => {
    setValidationSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, [field]: value }
        : step
    ));
  };

  const getCompletionRate = () => {
    const requiredSteps = validationSteps.filter(step => step.required);
    const completedRequired = requiredSteps.filter(step => step.completed);
    return requiredSteps.length > 0 ? (completedRequired.length / requiredSteps.length) * 100 : 0;
  };

  const getMasteryLevel = () => {
    const completedSteps = validationSteps.filter(step => step.completed);
    return completedSteps.length;
  };

  const getOverallConfidence = () => {
    const completedSteps = validationSteps.filter(step => step.completed);
    if (completedSteps.length === 0) return 0;
    const avgConfidence = completedSteps.reduce((acc, step) => acc + step.confidence[0], 0) / completedSteps.length;
    return Math.round(avgConfidence * 10);
  };

  const startValidation = (concept) => {
    setSelectedConcept(concept);
    setActiveValidation(concept);
  };

  const completeValidation = () => {
    const masteryLevel = getMasteryLevel();
    const confidence = getOverallConfidence();
    
    if (masteryLevel >= 3 && confidence >= 70) {
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 3000);
    }
    
    // Ici on pourrait sauvegarder les résultats
    console.log('Validation terminée:', {
      concept: selectedConcept,
      masteryLevel,
      confidence,
      steps: validationSteps
    });
  };

  const renderConceptSelection = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            Validation de Maîtrise par Étapes
          </CardTitle>
          <CardDescription>
            Sélectionnez un concept à valider selon les 5 niveaux de compétence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subjects.map((subject) => (
              <Card key={subject.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">{subject.name}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {subject.concepts.map((concept, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 border rounded">
                      <div>
                        <span className="font-medium">{concept.name}</span>
                        <div className="text-xs text-gray-500">
                          Maîtrise: {Math.round(concept.mastery_level * 100)}% • 
                          Rétention: {Math.round(concept.retention_rate * 100)}%
                        </div>
                      </div>
                      <Button 
                        size="sm" 
                        onClick={() => startValidation(concept)}
                        variant={concept.mastery_level >= 0.8 ? "outline" : "default"}
                      >
                        {concept.mastery_level >= 0.8 ? 'Revalider' : 'Valider'}
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderValidationProcess = () => (
    <div className="space-y-6">
      {/* En-tête de validation */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-blue-500" />
                Validation: {selectedConcept?.name}
              </CardTitle>
              <CardDescription>
                Niveau de maîtrise: {getMasteryLevel()}/5 • Confiance: {getOverallConfidence()}%
              </CardDescription>
            </div>
            <Button onClick={() => setSelectedConcept(null)} variant="outline">
              Retour
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Progression de validation</span>
                <span>{Math.round(getCompletionRate())}%</span>
              </div>
              <Progress value={getCompletionRate()} className="h-3" />
            </div>
            
            {showCelebration && (
              <Alert className="border-green-200 bg-green-50">
                <Trophy className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  🎉 Félicitations ! Vous avez atteint un niveau de maîtrise élevé pour ce concept !
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Étapes de validation */}
      <div className="space-y-4">
        {validationSteps.map((step, index) => (
          <Card key={step.id} className={`border-l-4 border-l-${step.color}-500`}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full bg-${step.color}-100 flex items-center justify-center`}>
                    <step.icon className={`h-4 w-4 text-${step.color}-600`} />
                  </div>
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      Niveau {step.level}: {step.title}
                      {step.required && <Badge variant="secondary">Requis</Badge>}
                    </CardTitle>
                    <CardDescription>{step.description}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {step.completed ? (
                    <CheckCircle2 className="h-6 w-6 text-green-500" />
                  ) : (
                    <Circle className="h-6 w-6 text-gray-400" />
                  )}
                  <Button
                    variant={step.completed ? "outline" : "default"}
                    size="sm"
                    onClick={() => toggleStep(step.id)}
                  >
                    {step.completed ? 'Revalider' : 'Valider'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            {step.completed && (
              <CardContent className="space-y-4">
                <Tabs defaultValue="criteria" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="criteria">Critères</TabsTrigger>
                    <TabsTrigger value="details">Détails</TabsTrigger>
                    <TabsTrigger value="stats">Statistiques</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="criteria" className="space-y-2">
                    <h4 className="font-medium">Critères de validation:</h4>
                    <div className="space-y-1">
                      {step.criteria.map((criterion, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                          <span>{criterion}</span>
                        </div>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="details" className="space-y-3">
                    <div>
                      <label className="text-sm font-medium">Niveau de confiance:</label>
                      <Slider
                        value={step.confidence}
                        onValueChange={(value) => updateStepData(step.id, 'confidence', value)}
                        max={10}
                        step={1}
                        className="mt-2"
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        {step.confidence[0]}/10
                      </div>
                    </div>
                    
                    {step.id === 'theoretical' && (
                      <div>
                        <label className="text-sm font-medium">Explication dans vos mots:</label>
                        <Textarea
                          value={step.explanation}
                          onChange={(e) => updateStepData(step.id, 'explanation', e.target.value)}
                          placeholder="Expliquez ce concept comme si vous l'enseigniez à un ami..."
                          className="mt-2"
                        />
                      </div>
                    )}
                    
                    {step.id === 'transfer' && (
                      <div>
                        <label className="text-sm font-medium">Exemples de transfert:</label>
                        <Textarea
                          value={step.transferExamples}
                          onChange={(e) => updateStepData(step.id, 'transferExamples', e.target.value)}
                          placeholder="Donnez des exemples d'application dans d'autres contextes..."
                          className="mt-2"
                        />
                      </div>
                    )}
                    
                    {step.id === 'mastery' && (
                      <div>
                        <label className="text-sm font-medium">Explication pédagogique:</label>
                        <Textarea
                          value={step.teachingExplanation}
                          onChange={(e) => updateStepData(step.id, 'teachingExplanation', e.target.value)}
                          placeholder="Comment enseigneriez-vous ce concept à un débutant ?"
                          className="mt-2"
                        />
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="stats" className="space-y-2">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Tentatives:</span>
                        <span className="font-medium ml-2">{step.attempts}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Temps passé:</span>
                        <span className="font-medium ml-2">{step.timeSpent} min</span>
                      </div>
                      {step.id === 'practical' && (
                        <div>
                          <span className="text-gray-600">Score exercices:</span>
                          <span className="font-medium ml-2">{step.exerciseScore}%</span>
                        </div>
                      )}
                      {step.id === 'memorization' && (
                        <div>
                          <span className="text-gray-600">Taux de rétention:</span>
                          <span className="font-medium ml-2">{step.retentionRate}%</span>
                        </div>
                      )}
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Planning de répétition espacée */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-green-500" />
            Planning de Répétition Espacée
          </CardTitle>
          <CardDescription>
            Révisions programmées pour optimiser la rétention à long terme
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {spacedRepetitionSchedule.map((review, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 border rounded">
                <div className="flex items-center gap-3">
                  <Timer className="h-4 w-4 text-blue-500" />
                  <div>
                    <span className="font-medium">Révision {idx + 1}</span>
                    <div className="text-sm text-gray-600">
                      Dans {review.interval} jour{review.interval > 1 ? 's' : ''} • {review.date.toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <Badge variant={review.completed ? "default" : "outline"}>
                  {review.completed ? 'Terminée' : 'Programmée'}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions finales */}
      <div className="flex justify-center gap-4">
        <Button onClick={completeValidation} size="lg" className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          Terminer la validation
        </Button>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto">
      {selectedConcept ? renderValidationProcess() : renderConceptSelection()}
    </div>
  );
};

export default ValidationChecklist;

