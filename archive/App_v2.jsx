import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Target, 
  Users, 
  Zap, 
  BookOpen, 
  BarChart3, 
  Calendar, 
  Settings, 
  Sparkles, 
  TrendingUp, 
  Clock, 
  Award,
  Bell,
  Activity,
  Star,
  Flame,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Progress } from './components/ui/progress';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Alert, AlertDescription } from './components/ui/alert';
import MasteryDashboard from './MasteryDashboard_v2';

function App() {
  const [activeModule, setActiveModule] = useState('mastery');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [notifications, setNotifications] = useState([]);
  const [userProfile, setUserProfile] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    loadUserProfile();
    loadNotifications();
    return () => clearInterval(timer);
  }, []);

  const loadUserProfile = async () => {
    // Simulation du profil utilisateur avec nouvelles métriques
    const profile = {
      name: "Euloge MABIALA",
      currentScore: 700,
      targetScore: 800,
      studyStreak: 12,
      totalStudyTime: 156, // heures
      masteryLevel: 0.72,
      retentionRate: 0.84,
      learningVelocity: 1.3, // concepts par jour
      consistencyScore: 0.89,
      nextReview: "2h",
      weeklyProgress: 29,
      monthlyGoal: 85,
      achievements: [
        { name: "Streak Master", description: "12 jours consécutifs", icon: Flame },
        { name: "Grammar Expert", description: "90% de maîtrise", icon: Star },
        { name: "Consistent Learner", description: "89% de régularité", icon: Award }
      ],
      weakAreas: ["Reading Speed", "Business Vocabulary"],
      strongAreas: ["Grammar", "Listening Comprehension"]
    };
    setUserProfile(profile);
  };

  const loadNotifications = async () => {
    // Simulation de notifications intelligentes
    const mockNotifications = [
      {
        id: 1,
        type: "review",
        title: "Révision programmée",
        message: "5 concepts à réviser maintenant",
        priority: "high",
        time: "maintenant",
        icon: Clock
      },
      {
        id: 2,
        type: "achievement",
        title: "Objectif atteint !",
        message: "Vous avez maîtrisé 3 nouveaux concepts cette semaine",
        priority: "medium",
        time: "il y a 1h",
        icon: Award
      },
      {
        id: 3,
        type: "suggestion",
        title: "Moment optimal",
        message: "C'est votre pic d'énergie cognitive. Idéal pour apprendre !",
        priority: "medium",
        time: "il y a 30min",
        icon: Brain
      },
      {
        id: 4,
        type: "warning",
        title: "Attention",
        message: "Votre rétention sur 'Conditional Sentences' diminue",
        priority: "high",
        time: "il y a 2h",
        icon: AlertCircle
      }
    ];
    setNotifications(mockNotifications);
  };

  // Données de progression avec nouvelles métriques
  const progressData = {
    currentScore: userProfile?.currentScore || 700,
    targetScore: userProfile?.targetScore || 800,
    listening: 380,
    reading: 320,
    speaking: 140,
    writing: 130,
    streakDays: userProfile?.studyStreak || 12,
    sessionsToday: 3,
    totalSessions: 5,
    nextReview: userProfile?.nextReview || "2h",
    weeklyProgress: userProfile?.weeklyProgress || 29,
    totalHours: userProfile?.totalStudyTime || 156,
    averageStreak: 10,
    masteryLevel: userProfile?.masteryLevel || 0.72,
    retentionRate: userProfile?.retentionRate || 0.84,
    learningVelocity: userProfile?.learningVelocity || 1.3,
    consistencyScore: userProfile?.consistencyScore || 0.89
  };

  const recommendations = [
    {
      type: "focus",
      title: "Concentrez-vous sur le Reading",
      description: "Votre score le plus faible. +30 points possibles",
      priority: "high",
      icon: Target,
      color: "from-red-500 to-pink-500"
    },
    {
      type: "timing",
      title: "Session Deep Work recommandée",
      description: "Votre pic d'énergie: 14h-16h",
      priority: "medium",
      icon: Clock,
      color: "from-blue-500 to-cyan-500"
    },
    {
      type: "method",
      title: "Technique Feynman suggérée",
      description: "Pour les concepts complexes de grammaire",
      priority: "medium",
      icon: Brain,
      color: "from-purple-500 to-indigo-500"
    },
    {
      type: "social",
      title: "Session collaborative disponible",
      description: "3 autres apprenants en ligne",
      priority: "low",
      icon: Users,
      color: "from-green-500 to-emerald-500"
    }
  ];

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const renderHeader = () => (
    <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-3xl p-6 text-white mb-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
            <Brain className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Plateforme Euloge v2.0</h1>
            <p className="text-blue-100">IA + Neurosciences pour la maîtrise totale</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <Button variant="ghost" size="sm" className="text-white hover:bg-white/20">
              <Bell className="h-5 w-5" />
              {notifications.filter(n => n.priority === 'high').length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {notifications.filter(n => n.priority === 'high').length}
                </span>
              )}
            </Button>
          </div>
          
          {/* Score actuel */}
          <div className="text-right">
            <div className="text-2xl font-bold">{progressData.currentScore}</div>
            <div className="text-blue-200 text-sm">Score TOEIC estimé</div>
          </div>
        </div>
      </div>
      
      {/* Métriques rapides */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
        {[
          { label: "Maîtrise", value: `${Math.round(progressData.masteryLevel * 100)}%`, icon: Target },
          { label: "Rétention", value: `${Math.round(progressData.retentionRate * 100)}%`, icon: Brain },
          { label: "Série", value: `${progressData.streakDays}j`, icon: Flame },
          { label: "Vitesse", value: `${progressData.learningVelocity}/j`, icon: Zap },
          { label: "Régularité", value: `${Math.round(progressData.consistencyScore * 100)}%`, icon: Activity }
        ].map((metric, index) => (
          <div key={index} className="bg-white/10 backdrop-blur-sm rounded-lg p-3 text-center">
            <metric.icon className="h-4 w-4 mx-auto mb-1 text-white/80" />
            <div className="font-bold">{metric.value}</div>
            <div className="text-xs text-white/70">{metric.label}</div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderNotifications = () => (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5 text-blue-500" />
          Notifications Intelligentes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {notifications.slice(0, 3).map((notification) => (
            <div key={notification.id} className={`p-3 rounded-lg border-l-4 ${getPriorityColor(notification.priority)}`}>
              <div className="flex items-start gap-3">
                <notification.icon className="h-5 w-5 mt-0.5 text-gray-600" />
                <div className="flex-1">
                  <div className="font-medium">{notification.title}</div>
                  <div className="text-sm text-gray-600">{notification.message}</div>
                  <div className="text-xs text-gray-500 mt-1">{notification.time}</div>
                </div>
                <Badge variant={notification.priority === 'high' ? 'destructive' : 'secondary'}>
                  {notification.priority}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const renderQuickStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Progression vers l'objectif</p>
              <p className="text-2xl font-bold text-blue-600">
                {Math.round((progressData.currentScore / progressData.targetScore) * 100)}%
              </p>
            </div>
            <Target className="h-8 w-8 text-blue-500" />
          </div>
          <Progress 
            value={(progressData.currentScore / progressData.targetScore) * 100} 
            className="mt-3" 
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Temps d'étude total</p>
              <p className="text-2xl font-bold text-green-600">{progressData.totalHours}h</p>
            </div>
            <Clock className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            +{Math.round(progressData.totalHours / 30)} heures ce mois
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Série d'étude</p>
              <p className="text-2xl font-bold text-orange-600">{progressData.streakDays}</p>
            </div>
            <Flame className="h-8 w-8 text-orange-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Record personnel: {progressData.averageStreak + 5} jours
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Prochaine révision</p>
              <p className="text-2xl font-bold text-purple-600">{progressData.nextReview}</p>
            </div>
            <Calendar className="h-8 w-8 text-purple-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {progressData.sessionsToday}/{progressData.totalSessions} sessions aujourd'hui
          </p>
        </CardContent>
      </Card>
    </div>
  );

  const renderRecommendations = () => (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-yellow-500" />
          Recommandations IA Personnalisées
        </CardTitle>
        <CardDescription>
          Basées sur votre profil d'apprentissage et vos performances
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, index) => (
            <div key={index} className={`p-4 rounded-lg bg-gradient-to-r ${rec.color} text-white`}>
              <div className="flex items-start gap-3">
                <rec.icon className="h-6 w-6 mt-1" />
                <div className="flex-1">
                  <h4 className="font-semibold mb-1">{rec.title}</h4>
                  <p className="text-sm opacity-90">{rec.description}</p>
                  <Badge 
                    variant="secondary" 
                    className="mt-2 bg-white/20 text-white border-white/30"
                  >
                    {rec.priority}
                  </Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );

  const renderAchievements = () => (
    userProfile?.achievements && (
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5 text-yellow-500" />
            Réalisations Récentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {userProfile.achievements.map((achievement, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
                <achievement.icon className="h-8 w-8 text-yellow-600" />
                <div>
                  <div className="font-medium">{achievement.name}</div>
                  <div className="text-sm text-gray-600">{achievement.description}</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  );

  const renderPerformanceInsights = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-500" />
            Points Forts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {userProfile?.strongAreas?.map((area, index) => (
              <div key={index} className="flex items-center gap-2">
                <Star className="h-4 w-4 text-green-500" />
                <span className="text-sm">{area}</span>
                <Badge variant="outline" className="ml-auto">Excellent</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-orange-500" />
            Zones à Améliorer
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {userProfile?.weakAreas?.map((area, index) => (
              <div key={index} className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-orange-500" />
                <span className="text-sm">{area}</span>
                <Badge variant="outline" className="ml-auto">À travailler</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  if (activeModule === 'mastery') {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto p-6">
          {renderHeader()}
          {renderNotifications()}
          {renderQuickStats()}
          {renderRecommendations()}
          {renderAchievements()}
          {renderPerformanceInsights()}
          <MasteryDashboard />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-6">
        {renderHeader()}
        <div className="text-center py-20">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Module en développement
          </h2>
          <p className="text-gray-600 mb-8">
            Cette fonctionnalité sera bientôt disponible dans la plateforme Euloge v2.0
          </p>
          <Button onClick={() => setActiveModule('mastery')}>
            Retour au Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}

export default App;

