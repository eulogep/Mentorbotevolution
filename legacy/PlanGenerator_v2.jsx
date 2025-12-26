import React, { useState, useEffect } from 'react';
import { 
  Target, 
  Brain, 
  Calendar, 
  BookOpen, 
  Zap, 
  CheckCircle2, 
  ArrowRight,
  Clock,
  TrendingUp,
  Lightbulb,
  Users,
  Activity,
  Star,
  AlertCircle,
  Settings
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';

const PlanGenerator = ({ subjects, analyzedDocuments }) => {
  const [targetScore, setTargetScore] = useState([800]);
  const [timeframe, setTimeframe] = useState('3');
  const [learningStyle, setLearningStyle] = useState('');
  const [studyTime, setStudyTime] = useState([2]);
  const [chronotype, setChronotype] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    generateUserProfile();
  }, [subjects]);

  const learningMethods = {
    visual: {
      name: 'Visuel',
      description: 'Cartes mentales, schémas, graphiques',
      icon: '👁️',
      techniques: ['Dual Coding', 'Méthode des Lieux', 'Cartes Conceptuelles', 'Visualisations'],
      effectiveness: 0.85,
      timeMultiplier: 1.0
    },
    auditory: {
      name: 'Auditif',
      description: 'Écoute, répétition orale, discussions',
      icon: '👂',
      techniques: ['Technique Feynman', 'Répétition Orale', 'Podcasts Éducatifs', 'Discussions'],
      effectiveness: 0.80,
      timeMultiplier: 1.1
    },
    kinesthetic: {
      name: 'Kinesthésique',
      description: 'Manipulation, expérimentation, mouvement',
      icon: '✋',
      techniques: ['Apprentissage Actif', 'Simulations', 'Exercices Pratiques', 'Jeux de rôle'],
      effectiveness: 0.75,
      timeMultiplier: 1.2
    },
    mixed: {
      name: 'Multimodal',
      description: 'Combinaison optimisée de tous les styles',
      icon: '🧠',
      techniques: ['Approche Multimodale', 'Rotation des Méthodes', 'Adaptation Contextuelle', 'Personnalisation IA'],
      effectiveness: 0.90,
      timeMultiplier: 0.9
    }
  };

  const chronotypes = {
    morning: {
      name: 'Matinal',
      description: 'Performance optimale le matin',
      peakHours: ['8h-10h', '14h-16h'],
      studySchedule: {
        deepWork: '8h30-10h30',
        review: '14h-15h30',
        avoid: 'après 18h'
      }
    },
    intermediate: {
      name: 'Intermédiaire',
      description: 'Performance équilibrée',
      peakHours: ['10h-12h', '15h-17h'],
      studySchedule: {
        deepWork: '10h30-12h30',
        review: '15h30-17h30',
        avoid: 'avant 9h et après 19h'
      }
    },
    evening: {
      name: 'Tardif',
      description: 'Performance optimale en soirée',
      peakHours: ['11h-13h', '17h-19h'],
      studySchedule: {
        deepWork: '11h30-13h30',
        review: '17h30-19h30',
        avoid: 'avant 10h'
      }
    }
  };

  const generateUserProfile = () => {
    if (!subjects || subjects.length === 0) return;

    // Analyse des performances pour déterminer le profil
    const totalConcepts = subjects.reduce((acc, s) => acc + s.concepts.length, 0);
    const completedConcepts = subjects.reduce((acc, s) => 
      acc + s.concepts.filter(c => c.status === 'completed').length, 0
    );
    const avgProgress = subjects.reduce((acc, s) => acc + s.progress, 0) / subjects.length;

    const profile = {
      currentLevel: avgProgress > 70 ? 'advanced' : avgProgress > 40 ? 'intermediate' : 'beginner',
      completionRate: completedConcepts / totalConcepts,
      strongAreas: subjects.filter(s => s.progress > 70).map(s => s.name),
      weakAreas: subjects.filter(s => s.progress < 40).map(s => s.name),
      learningVelocity: completedConcepts / (subjects.reduce((acc, s) => acc + s.total_time, 0) || 1),
      recommendedStyle: avgProgress > 60 ? 'mixed' : 'visual' // Simplification
    };

    setUserProfile(profile);
    setLearningStyle(profile.recommendedStyle);
  };

  const calculateOptimalPath = (concepts, targetScore, timeframe, style) => {
    // Algorithme de planification optimisée
    const sortedConcepts = concepts.sort((a, b) => {
      // Prioriser par importance et prérequis
      const aScore = (a.importance || 0.5) * (a.difficulty || 1) * (1 - (a.mastery_level || 0));
      const bScore = (b.importance || 0.5) * (b.difficulty || 1) * (1 - (b.mastery_level || 0));
      return bScore - aScore;
    });

    return sortedConcepts.map((concept, index) => {
      const method = learningMethods[style];
      const baseTime = (concept.difficulty || 1) * 10; // heures de base
      const adjustedTime = baseTime * method.timeMultiplier * (1 - (concept.mastery_level || 0));
      
      return {
        ...concept,
        estimatedTime: Math.round(adjustedTime),
        selectedMethods: method.techniques.slice(0, 2), // Top 2 méthodes
        priority: index + 1,
        weeklyGoal: Math.ceil(adjustedTime / (parseInt(timeframe) * 4)), // heures par semaine
        spacedRepetition: generateSpacedRepetitionSchedule(concept.name)
      };
    });
  };

  const generateSpacedRepetitionSchedule = (conceptName) => {
    const now = new Date();
    return [
      { day: 1, date: new Date(now.getTime() + 24 * 60 * 60 * 1000) },
      { day: 3, date: new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000) },
      { day: 7, date: new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000) },
      { day: 14, date: new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000) },
      { day: 30, date: new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000) }
    ];
  };

  const generatePlan = async () => {
    setIsGenerating(true);
    
    try {
      // Simulation de génération de plan avancée
      await new Promise(resolve => setTimeout(resolve, 4000));

      const allConcepts = subjects?.flatMap(subject => 
        subject.concepts.map(concept => ({
          ...concept,
          subject: subject.name,
          importance: Math.random() * 0.5 + 0.5, // 0.5-1.0
          difficulty: concept.mastery_level < 0.3 ? 3 : concept.mastery_level < 0.7 ? 2 : 1
        }))
      ) || [];

      const optimizedConcepts = calculateOptimalPath(allConcepts, targetScore[0], timeframe, learningStyle);
      const totalEstimatedTime = optimizedConcepts.reduce((acc, c) => acc + c.estimatedTime, 0);
      const dailyTimeNeeded = totalEstimatedTime / (parseInt(timeframe) * 30); // heures par jour

      const plan = {
        id: Date.now(),
        targetScore: targetScore[0],
        currentEstimatedScore: 650, // Simulation
        timeframe: parseInt(timeframe),
        learningStyle,
        chronotype,
        dailyStudyTime: studyTime[0],
        dailyTimeNeeded: Math.round(dailyTimeNeeded * 10) / 10,
        concepts: optimizedConcepts,
        totalEstimatedTime,
        successProbability: Math.min(0.95, 0.6 + (studyTime[0] / dailyTimeNeeded) * 0.3),
        milestones: generateMilestones(timeframe, targetScore[0]),
        weeklySchedule: generateWeeklySchedule(chronotype, studyTime[0]),
        adaptiveFeatures: {
          difficultyAdjustment: true,
          performanceTracking: true,
          methodOptimization: true,
          scheduleFlexibility: true
        }
      };

      setGeneratedPlan(plan);
    } catch (error) {
      console.error('Erreur lors de la génération du plan:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateMilestones = (timeframe, targetScore) => {
    const months = parseInt(timeframe);
    const currentScore = 650; // Simulation
    const scoreIncrease = (targetScore - currentScore) / months;

    return Array.from({ length: months }, (_, i) => ({
      month: i + 1,
      targetScore: Math.round(currentScore + (scoreIncrease * (i + 1))),
      description: `Objectif mois ${i + 1}`,
      keyMilestones: [
        `Maîtriser ${Math.ceil((i + 1) * 3)} nouveaux concepts`,
        `Atteindre ${Math.round(70 + (i + 1) * 5)}% de rétention`,
        `Compléter ${Math.ceil((i + 1) * 20)} exercices pratiques`
      ]
    }));
  };

  const generateWeeklySchedule = (chronotype, dailyTime) => {
    const chrono = chronotypes[chronotype] || chronotypes.intermediate;
    
    return {
      monday: { deepWork: chrono.studySchedule.deepWork, review: '30min révisions' },
      tuesday: { deepWork: chrono.studySchedule.deepWork, practice: '45min exercices' },
      wednesday: { review: chrono.studySchedule.review, consolidation: '30min synthèse' },
      thursday: { deepWork: chrono.studySchedule.deepWork, application: '45min application' },
      friday: { practice: '1h exercices', review: '30min révisions' },
      saturday: { flexible: '1h session libre', assessment: '30min auto-évaluation' },
      sunday: { rest: 'Repos ou révision légère (optionnel)' }
    };
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 3: return 'bg-red-100 text-red-800';
      case 2: return 'bg-yellow-100 text-yellow-800';
      case 1: return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderPlanConfiguration = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Générateur de Plan Adaptatif v2.0
          </CardTitle>
          <CardDescription>
            Configuration personnalisée basée sur l'IA et les neurosciences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {userProfile && (
            <Alert>
              <Lightbulb className="h-4 w-4" />
              <AlertDescription>
                Profil détecté: <strong>{userProfile.currentLevel}</strong> • 
                Taux de complétion: <strong>{Math.round(userProfile.completionRate * 100)}%</strong> • 
                Style recommandé: <strong>{learningMethods[userProfile.recommendedStyle]?.name}</strong>
              </AlertDescription>
            </Alert>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <Label>Objectif TOEIC</Label>
                <div className="mt-2">
                  <Slider
                    value={targetScore}
                    onValueChange={setTargetScore}
                    min={400}
                    max={990}
                    step={10}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-1">
                    <span>400</span>
                    <span className="font-medium">{targetScore[0]} points</span>
                    <span>990</span>
                  </div>
                </div>
              </div>

              <div>
                <Label>Délai (mois)</Label>
                <Select value={timeframe} onValueChange={setTimeframe}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner la durée" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 mois (intensif)</SelectItem>
                    <SelectItem value="2">2 mois (accéléré)</SelectItem>
                    <SelectItem value="3">3 mois (optimal)</SelectItem>
                    <SelectItem value="6">6 mois (confortable)</SelectItem>
                    <SelectItem value="12">12 mois (progressif)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Temps d'étude quotidien</Label>
                <div className="mt-2">
                  <Slider
                    value={studyTime}
                    onValueChange={setStudyTime}
                    min={0.5}
                    max={8}
                    step={0.5}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-500 mt-1">
                    <span>30min</span>
                    <span className="font-medium">{studyTime[0]}h/jour</span>
                    <span>8h</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <Label>Style d'apprentissage</Label>
                <Select value={learningStyle} onValueChange={setLearningStyle}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner votre style" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(learningMethods).map(([key, method]) => (
                      <SelectItem key={key} value={key}>
                        {method.icon} {method.name} - {method.description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Chronotype (rythme circadien)</Label>
                <Select value={chronotype} onValueChange={setChronotype}>
                  <SelectTrigger>
                    <SelectValue placeholder="Quand êtes-vous le plus efficace ?" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(chronotypes).map(([key, type]) => (
                      <SelectItem key={key} value={key}>
                        {type.name} - {type.description}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {chronotype && (
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-sm mb-2">Horaires optimaux:</h4>
                  <div className="text-xs space-y-1">
                    <div>Deep Work: {chronotypes[chronotype].studySchedule.deepWork}</div>
                    <div>Révisions: {chronotypes[chronotype].studySchedule.review}</div>
                    <div>À éviter: {chronotypes[chronotype].studySchedule.avoid}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-center">
            <Button 
              onClick={generatePlan} 
              disabled={!learningStyle || !chronotype || !timeframe || isGenerating}
              size="lg"
              className="flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Génération en cours...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  Générer le Plan Adaptatif
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderGeneratedPlan = () => (
    <div className="space-y-6">
      {/* En-tête du plan */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-green-500" />
                Plan de Maîtrise Personnalisé
              </CardTitle>
              <CardDescription>
                Objectif: {generatedPlan.targetScore} points TOEIC en {generatedPlan.timeframe} mois
              </CardDescription>
            </div>
            <Button onClick={() => setGeneratedPlan(null)} variant="outline">
              Modifier
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{generatedPlan.totalEstimatedTime}h</div>
              <div className="text-sm text-gray-600">Temps total</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{generatedPlan.dailyTimeNeeded}h</div>
              <div className="text-sm text-gray-600">Par jour requis</div>
            </div>
            <div className="text-center p-3 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{Math.round(generatedPlan.successProbability * 100)}%</div>
              <div className="text-sm text-gray-600">Probabilité succès</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{generatedPlan.concepts.length}</div>
              <div className="text-sm text-gray-600">Concepts à maîtriser</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="concepts" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="concepts">Concepts</TabsTrigger>
          <TabsTrigger value="schedule">Planning</TabsTrigger>
          <TabsTrigger value="milestones">Jalons</TabsTrigger>
          <TabsTrigger value="methods">Méthodes</TabsTrigger>
        </TabsList>

        <TabsContent value="concepts" className="space-y-4">
          {generatedPlan.concepts.map((concept, index) => (
            <Card key={index}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg">{concept.name}</CardTitle>
                    <CardDescription>{concept.subject}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getDifficultyColor(concept.difficulty)}>
                      Niveau {concept.difficulty}
                    </Badge>
                    <Badge variant="outline">
                      Priorité {concept.priority}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Estimation</h4>
                    <div className="space-y-1 text-sm">
                      <div>Temps: {concept.estimatedTime}h</div>
                      <div>Par semaine: {concept.weeklyGoal}h</div>
                      <div>Maîtrise actuelle: {Math.round((concept.mastery_level || 0) * 100)}%</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Méthodes sélectionnées</h4>
                    <div className="space-y-1">
                      {concept.selectedMethods.map((method, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {method}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Répétition espacée</h4>
                    <div className="text-xs space-y-1">
                      {concept.spacedRepetition.slice(0, 3).map((rep, idx) => (
                        <div key={idx}>J+{rep.day}: {rep.date.toLocaleDateString()}</div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="schedule" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Planning Hebdomadaire Optimisé</CardTitle>
              <CardDescription>
                Basé sur votre chronotype {chronotypes[generatedPlan.chronotype]?.name}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(generatedPlan.weeklySchedule).map(([day, schedule]) => (
                  <div key={day} className="p-3 border rounded-lg">
                    <h4 className="font-medium capitalize mb-2">{day}</h4>
                    <div className="space-y-1 text-sm">
                      {Object.entries(schedule).map(([activity, time]) => (
                        <div key={activity} className="flex justify-between">
                          <span className="capitalize">{activity}:</span>
                          <span className="text-gray-600">{time}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="milestones" className="space-y-4">
          {generatedPlan.milestones.map((milestone, index) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Mois {milestone.month} - Objectif: {milestone.targetScore} points
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {milestone.keyMilestones.map((goal, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span className="text-sm">{goal}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="methods" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Méthodes Pédagogiques Sélectionnées</CardTitle>
              <CardDescription>
                Style {learningMethods[generatedPlan.learningStyle]?.name} - Efficacité: {Math.round(learningMethods[generatedPlan.learningStyle]?.effectiveness * 100)}%
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {learningMethods[generatedPlan.learningStyle]?.techniques.map((technique, index) => (
                  <div key={index} className="p-3 border rounded-lg">
                    <h4 className="font-medium">{technique}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Technique optimisée pour votre profil d'apprentissage
                    </p>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium mb-2">Fonctionnalités Adaptatives Activées:</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {Object.entries(generatedPlan.adaptiveFeatures).map(([feature, enabled]) => (
                    <div key={feature} className="flex items-center gap-2">
                      <CheckCircle2 className="h-3 w-3 text-green-500" />
                      <span className="capitalize">{feature.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto">
      {generatedPlan ? renderGeneratedPlan() : renderPlanConfiguration()}
    </div>
  );
};

export default PlanGenerator;

