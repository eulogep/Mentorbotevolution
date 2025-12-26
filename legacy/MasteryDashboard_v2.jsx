import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  BookOpen, 
  Target, 
  CheckCircle, 
  Clock, 
  TrendingUp, 
  Sparkles,
  Brain,
  Zap,
  Award,
  Calendar,
  Users,
  BarChart3,
  Plus,
  FileText,
  Image,
  Video,
  Mic,
  AlertTriangle,
  Star,
  Activity,
  Flame
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import DocumentUploader from './DocumentUploader_v2';
import PlanGenerator from './PlanGenerator';
import ValidationChecklist from './ValidationChecklist_v2';

const MasteryDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toiecPrediction, setToiecPrediction] = useState(null);
  const [masteryMetrics, setMasteryMetrics] = useState(null);

  useEffect(() => {
    fetchSubjects();
    fetchToiecPrediction();
    fetchMasteryMetrics();
  }, []);

  const fetchSubjects = async () => {
    try {
      // Simulation de données avec nouvelles métriques
      const mockSubjects = [
        {
          id: 1,
          name: 'TOEIC Listening',
          progress: 75,
          total_time: 45,
          concepts: [
            { name: 'Short Conversations', status: 'completed', mastery_level: 0.9, retention_rate: 0.85 },
            { name: 'Long Conversations', status: 'in-progress', mastery_level: 0.6, retention_rate: 0.7 },
            { name: 'Short Talks', status: 'not-started', mastery_level: 0, retention_rate: 0 }
          ],
          predicted_score: 380,
          target_score: 400,
          next_review: '2h',
          difficulty_trend: 'increasing',
          weak_areas: ['Fast speech recognition', 'Business vocabulary']
        },
        {
          id: 2,
          name: 'TOEIC Reading',
          progress: 60,
          total_time: 38,
          concepts: [
            { name: 'Incomplete Sentences', status: 'completed', mastery_level: 0.8, retention_rate: 0.9 },
            { name: 'Text Completion', status: 'in-progress', mastery_level: 0.5, retention_rate: 0.6 },
            { name: 'Reading Comprehension', status: 'in-progress', mastery_level: 0.4, retention_rate: 0.5 }
          ],
          predicted_score: 320,
          target_score: 400,
          next_review: '4h',
          difficulty_trend: 'stable',
          weak_areas: ['Complex grammar structures', 'Time management']
        }
      ];
      setSubjects(mockSubjects);
    } catch (error) {
      console.error('Erreur lors du chargement des matières:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchToiecPrediction = async () => {
    // Simulation de prédiction TOEIC basée sur les performances
    const mockPrediction = {
      current_estimated_score: 700,
      target_score: 800,
      probability_success: 0.78,
      estimated_time_to_target: 45, // jours
      confidence_interval: [680, 720],
      improvement_rate: 12, // points par semaine
      bottlenecks: [
        { area: 'Reading Speed', impact: 'high', improvement_potential: 50 },
        { area: 'Business Vocabulary', impact: 'medium', improvement_potential: 30 }
      ]
    };
    setToiecPrediction(mockPrediction);
  };

  const fetchMasteryMetrics = async () => {
    // Simulation de métriques de maîtrise avancées
    const mockMetrics = {
      overall_mastery: 0.72,
      retention_rate: 0.84,
      learning_velocity: 1.3, // concepts par jour
      consistency_score: 0.89,
      deep_understanding: 0.68,
      application_ability: 0.75,
      transfer_capability: 0.62,
      teaching_readiness: 0.58,
      streak_days: 12,
      total_study_sessions: 156,
      avg_session_quality: 0.81
    };
    setMasteryMetrics(mockMetrics);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'from-green-500 to-emerald-500';
      case 'in-progress': return 'from-blue-500 to-cyan-500';
      case 'not-started': return 'from-gray-400 to-gray-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getMasteryColor = (level) => {
    if (level >= 0.8) return 'text-green-600 bg-green-100';
    if (level >= 0.6) return 'text-yellow-600 bg-yellow-100';
    if (level >= 0.4) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Hero Section avec prédiction TOEIC */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-3xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <Brain className="h-8 w-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold mb-2">Plateforme de Maîtrise Totale v2.0</h1>
                <p className="text-blue-100 text-lg">IA + Neurosciences pour atteindre 800 au TOEIC</p>
              </div>
            </div>
            {toiecPrediction && (
              <div className="text-right">
                <div className="text-4xl font-bold">{toiecPrediction.current_estimated_score}</div>
                <div className="text-blue-200">Score TOEIC estimé</div>
                <div className="text-sm text-blue-300">
                  Objectif: {toiecPrediction.target_score} ({toiecPrediction.probability_success * 100}% de réussite)
                </div>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {[
              { label: "Maîtrise Globale", value: `${Math.round((masteryMetrics?.overall_mastery || 0) * 100)}%`, icon: Target },
              { label: "Rétention", value: `${Math.round((masteryMetrics?.retention_rate || 0) * 100)}%`, icon: Brain },
              { label: "Série", value: `${masteryMetrics?.streak_days || 0} jours`, icon: Flame },
              { label: "Vitesse", value: `${masteryMetrics?.learning_velocity || 0}/j`, icon: Zap },
              { label: "Qualité", value: `${Math.round((masteryMetrics?.avg_session_quality || 0) * 100)}%`, icon: Star }
            ].map((stat, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <stat.icon className="h-5 w-5 mx-auto mb-2 text-white/80" />
                <div className="text-xl font-bold">{stat.value}</div>
                <div className="text-xs text-white/70">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Prédiction TOEIC détaillée */}
      {toiecPrediction && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-500" />
              Prédiction TOEIC Avancée
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium">Progression vers l'objectif</span>
                    <span className="text-sm text-gray-600">
                      {toiecPrediction.current_estimated_score}/{toiecPrediction.target_score}
                    </span>
                  </div>
                  <Progress 
                    value={(toiecPrediction.current_estimated_score / toiecPrediction.target_score) * 100} 
                    className="h-3"
                  />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {toiecPrediction.estimated_time_to_target} jours
                  </div>
                  <div className="text-sm text-gray-600">pour atteindre l'objectif</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Goulots d'étranglement</h4>
                {toiecPrediction.bottlenecks.map((bottleneck, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm">{bottleneck.area}</span>
                    <Badge variant={bottleneck.impact === 'high' ? 'destructive' : 'secondary'}>
                      +{bottleneck.improvement_potential}pts
                    </Badge>
                  </div>
                ))}
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Métriques de Performance</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>Taux d'amélioration:</span>
                    <span className="font-medium">+{toiecPrediction.improvement_rate}pts/semaine</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Intervalle de confiance:</span>
                    <span className="font-medium">
                      {toiecPrediction.confidence_interval[0]}-{toiecPrediction.confidence_interval[1]}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Probabilité de succès:</span>
                    <span className="font-medium text-green-600">
                      {Math.round(toiecPrediction.probability_success * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Métriques de Maîtrise Multidimensionnelles */}
      {masteryMetrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-purple-500" />
              Métriques de Maîtrise Multidimensionnelles
            </CardTitle>
            <CardDescription>
              Évaluation approfondie de votre compréhension selon 5 dimensions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                {[
                  { name: 'Compréhension Théorique', value: masteryMetrics.deep_understanding, icon: Brain },
                  { name: 'Application Pratique', value: masteryMetrics.application_ability, icon: Target },
                  { name: 'Transfert de Connaissances', value: masteryMetrics.transfer_capability, icon: Zap },
                  { name: 'Capacité d\'Enseignement', value: masteryMetrics.teaching_readiness, icon: Users }
                ].map((metric, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <metric.icon className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium">{metric.name}</span>
                      </div>
                      <span className="text-sm font-bold">{Math.round(metric.value * 100)}%</span>
                    </div>
                    <Progress value={metric.value * 100} className="h-2" />
                  </div>
                ))}
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Indicateurs de Qualité</h4>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Consistance', value: masteryMetrics.consistency_score, color: 'blue' },
                    { label: 'Rétention', value: masteryMetrics.retention_rate, color: 'green' },
                    { label: 'Vitesse', value: masteryMetrics.learning_velocity / 2, color: 'orange' }, // Normalisé
                    { label: 'Qualité', value: masteryMetrics.avg_session_quality, color: 'purple' }
                  ].map((indicator, idx) => (
                    <div key={idx} className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className={`text-lg font-bold text-${indicator.color}-600`}>
                        {Math.round(indicator.value * 100)}%
                      </div>
                      <div className="text-xs text-gray-600">{indicator.label}</div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Activité Récente</span>
                  </div>
                  <div className="text-xs text-gray-600">
                    {masteryMetrics.total_study_sessions} sessions • {masteryMetrics.streak_days} jours consécutifs
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Matières avec métriques avancées */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {subjects.map((subject) => (
          <Card key={subject.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{subject.name}</CardTitle>
                <Badge className={getMasteryColor(subject.predicted_score / subject.target_score)}>
                  {subject.predicted_score}/{subject.target_score}
                </Badge>
              </div>
              <CardDescription>
                Prochaine révision: {subject.next_review} • Tendance: {subject.difficulty_trend}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Progression globale</span>
                  <span>{subject.progress}%</span>
                </div>
                <Progress value={subject.progress} className="h-2" />
              </div>
              
              <div className="space-y-2">
                <h5 className="text-sm font-medium">Concepts par niveau de maîtrise</h5>
                {subject.concepts.map((concept, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span>{concept.name}</span>
                    <div className="flex items-center gap-2">
                      <Badge className={getMasteryColor(concept.mastery_level)} variant="outline">
                        {Math.round(concept.mastery_level * 100)}%
                      </Badge>
                      <span className="text-gray-500">
                        R: {Math.round(concept.retention_rate * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              
              {subject.weak_areas.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium flex items-center gap-1 mb-2">
                    <AlertTriangle className="h-3 w-3 text-orange-500" />
                    Zones à renforcer
                  </h5>
                  <div className="flex flex-wrap gap-1">
                    {subject.weak_areas.map((area, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {area}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="upload">Upload & Analyse</TabsTrigger>
          <TabsTrigger value="planning">Planification</TabsTrigger>
          <TabsTrigger value="validation">Validation</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {renderOverview()}
        </TabsContent>

        <TabsContent value="upload" className="space-y-6">
          <DocumentUploader 
            onUploadComplete={(files) => {
              console.log('Fichiers analysés:', files);
              // Mettre à jour les sujets avec les nouveaux contenus
            }}
            onAnalysisStart={() => {
              console.log('Analyse démarrée');
            }}
          />
        </TabsContent>

        <TabsContent value="planning" className="space-y-6">
          <PlanGenerator subjects={subjects} />
        </TabsContent>

        <TabsContent value="validation" className="space-y-6">
          <ValidationChecklist subjects={subjects} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MasteryDashboard;

