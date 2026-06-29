/**
 * Euloge Learning Platform - Plateforme d'Apprentissage IA
 * 
 * @author EULOGE MABIALA
 * @description Plateforme d'apprentissage moderne basée sur l'IA et les neurosciences
 * @version 2.0.0
 * @license MIT
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Brain, Target, Users, Zap, BookOpen, BarChart3, Calendar, Sparkles, TrendingUp, Clock, Award, Menu, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card.jsx';
import { Button } from './components/ui/button.jsx';
import { Progress } from './components/ui/progress.jsx';
import { Badge } from './components/ui/badge.jsx';
import MasteryDashboard from './components/MasteryPlan/MasteryDashboard.jsx';
import { useAuth } from './context/AuthContext';

// UI polish inspired by reactbits.dev: animated number counter
function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
function useAnimatedNumber(value, duration = 800) {
  const [display, setDisplay] = useState(value);
  const prevRef = React.useRef(value);
  useEffect(() => {
    const start = performance.now();
    const startVal = prevRef.current;
    const delta = value - startVal;
    let raf;
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      setDisplay(Math.round(startVal + delta * easeOutCubic(t)));
      if (t < 1) raf = requestAnimationFrame(tick); else prevRef.current = value;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value, duration]);
  return display;
}

const AnimatedStat = ({ value, suffix = '' }) => {
  const v = useAnimatedNumber(value);
  return <span>{v}{suffix}</span>;
};

function App() {
  const [activeModule, setActiveModule] = useState('mastery');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  // Données de progression simulées
  const progressData = {
    currentScore: 650,
    targetScore: 800,
    listening: 340,
    reading: 310,
    speaking: 140,
    writing: 130,
    streakDays: 12,
    sessionsToday: 3,
    totalSessions: 5,
    nextReview: "2h",
    weeklyProgress: 29,
    totalHours: 77,
    averageStreak: 10
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
      type: "review",
      title: "Révision espacée optimale",
      description: "Moment idéal pour réviser le vocabulaire",
      priority: "medium",
      icon: Brain,
      color: "from-purple-500 to-indigo-500"
    }
  ];

  const modules = [
    {
      id: 'mastery',
      name: 'Plans de Maîtrise',
      description: 'Gestion complète des matières avec IA',
      icon: BookOpen,
      gradient: 'from-blue-500 to-blue-600',
      bgGradient: 'from-blue-50 to-blue-100'
    },
    {
      id: 'neuroscience',
      name: 'Neurosciences',
      description: 'Techniques basées sur la science du cerveau',
      icon: Brain,
      gradient: 'from-purple-500 to-purple-600',
      bgGradient: 'from-purple-50 to-purple-100'
    },
    {
      id: 'ai-tools',
      name: 'Outils IA',
      description: 'Assistant intelligent et quiz adaptatifs',
      icon: Zap,
      gradient: 'from-green-500 to-green-600',
      bgGradient: 'from-green-50 to-green-100'
    },
    {
      id: 'productivity',
      name: 'Productivité',
      description: 'Deep Work et optimisation cognitive',
      icon: Target,
      gradient: 'from-orange-500 to-orange-600',
      bgGradient: 'from-orange-50 to-orange-100'
    },
    {
      id: 'collaboration',
      name: 'Collaboration',
      description: 'Groupes d\'étude et mentorat',
      icon: Users,
      gradient: 'from-pink-500 to-pink-600',
      bgGradient: 'from-pink-50 to-pink-100'
    },
    {
      id: 'analytics',
      name: 'Analytics',
      description: 'Suivi détaillé et prédictions',
      icon: BarChart3,
      gradient: 'from-indigo-500 to-indigo-600',
      bgGradient: 'from-indigo-50 to-indigo-100'
    }
  ];

  const renderModuleContent = () => {
    switch (activeModule) {
      case 'mastery':
        return <MasteryDashboard />;

      case 'neuroscience':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <Brain className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Techniques Neuroscientifiques</h2>
                  <p className="text-purple-100">Optimisez votre apprentissage avec la science du cerveau</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                {
                  title: "Répétition Espacée",
                  description: "Optimise la consolidation mnésique selon la courbe d'oubli",
                  icon: Clock,
                  gradient: "from-blue-500 to-cyan-500",
                  progress: 85
                },
                {
                  title: "Technique Feynman",
                  description: "Apprenez en expliquant simplement les concepts",
                  icon: Brain,
                  gradient: "from-purple-500 to-pink-500",
                  progress: 70
                },
                {
                  title: "Méthode des Lieux",
                  description: "Utilisez la mémoire spatiale pour mémoriser",
                  icon: Target,
                  gradient: "from-green-500 to-emerald-500",
                  progress: 60
                },
                {
                  title: "Dual Coding",
                  description: "Combinez informations visuelles et verbales",
                  icon: Sparkles,
                  gradient: "from-orange-500 to-red-500",
                  progress: 45
                }
              ].map((technique, index) => (
                <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-0 shadow-lg">
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4">
                      <div className={`w-12 h-12 bg-gradient-to-r ${technique.gradient} rounded-xl flex items-center justify-center shadow-lg`}>
                        <technique.icon className="h-6 w-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-lg mb-2">{technique.title}</h3>
                        <p className="text-gray-600 text-sm mb-4">{technique.description}</p>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500">Maîtrise</span>
                            <span className="font-semibold">{technique.progress}%</span>
                          </div>
                          <Progress value={technique.progress} className="h-2" />
                        </div>
                        <Button className={`mt-4 bg-gradient-to-r ${technique.gradient} hover:shadow-lg transition-all duration-200`} size="sm">
                          Pratiquer
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'ai-tools':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <Zap className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Assistant IA Conversationnel</h2>
                  <p className="text-green-100">Votre tuteur personnel disponible 24h/24</p>
                </div>
              </div>
            </div>

            <Card className="border-0 shadow-xl">
              <CardContent className="p-6">
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 mb-6">
                  <p className="text-gray-700 mb-4 font-medium">💬 Posez votre question à l'IA:</p>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      placeholder="Ex: Quelle est la différence entre 'will' et 'going to'?"
                      className="flex-1 p-3 border-0 rounded-xl bg-white shadow-sm focus:ring-2 focus:ring-green-500 transition-all"
                    />
                    <Button className="bg-gradient-to-r from-green-500 to-emerald-600 hover:shadow-lg px-6">
                      Demander
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    {
                      title: "Quiz Adaptatif",
                      description: "Questions personnalisées selon votre niveau",
                      icon: Target,
                      gradient: "from-blue-500 to-cyan-500"
                    },
                    {
                      title: "Explication Feynman",
                      description: "Simplification automatique des concepts",
                      icon: Brain,
                      gradient: "from-purple-500 to-pink-500"
                    }
                  ].map((tool, index) => (
                    <Button key={index} variant="outline" className="h-auto p-6 text-left border-2 hover:border-green-300 hover:shadow-lg transition-all duration-200 group">
                      <div className="flex items-start gap-4">
                        <div className={`w-10 h-10 bg-gradient-to-r ${tool.gradient} rounded-lg flex items-center justify-center`}>
                          <tool.icon className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">{tool.title}</div>
                          <div className="text-sm text-gray-500 mt-1">{tool.description}</div>
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        );

      case 'productivity':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <Target className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Deep Work & Productivité</h2>
                  <p className="text-orange-100">Optimisez vos sessions selon votre chronotype</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  title: "Session Deep Work",
                  description: "45 min de concentration pure",
                  icon: Calendar,
                  gradient: "from-blue-500 to-cyan-500",
                  action: "Démarrer",
                  status: "Prêt"
                },
                {
                  title: "Pic d'Énergie",
                  description: "Votre moment optimal: 14h-16h",
                  icon: Brain,
                  gradient: "from-green-500 to-emerald-500",
                  action: "Configurer",
                  status: "Optimal"
                },
                {
                  title: "Niveau d'Énergie",
                  description: "Actuellement: Élevé",
                  icon: Zap,
                  gradient: "from-orange-500 to-red-500",
                  action: "Mettre à jour",
                  status: "Élevé"
                }
              ].map((item, index) => (
                <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-1 border-0 shadow-lg">
                  <CardContent className="p-6 text-center">
                    <div className={`w-16 h-16 bg-gradient-to-r ${item.gradient} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-200`}>
                      <item.icon className="h-8 w-8 text-white" />
                    </div>
                    <h3 className="font-bold text-lg mb-2">{item.title}</h3>
                    <p className="text-gray-600 text-sm mb-4">{item.description}</p>
                    <Badge className={`mb-4 bg-gradient-to-r ${item.gradient} text-white border-0`}>
                      {item.status}
                    </Badge>
                    <Button className={`w-full bg-gradient-to-r ${item.gradient} hover:shadow-lg transition-all duration-200`} size="sm">
                      {item.action}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'collaboration':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <Users className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Apprentissage Collaboratif</h2>
                  <p className="text-pink-100">Rejoignez des groupes d'étude et bénéficiez de mentorat</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {[
                {
                  title: "TOEIC 800+ Challenge",
                  members: "12 membres",
                  nextSession: "Aujourd'hui 19h",
                  description: "Groupe d'étude intensif pour atteindre 800+ points",
                  status: "Actif",
                  statusColor: "bg-green-500",
                  gradient: "from-blue-500 to-cyan-500"
                },
                {
                  title: "Mentor: Sarah K.",
                  members: "Score: 850",
                  nextSession: "47 sessions complétées",
                  description: "Spécialiste Business English & Stratégie TOEIC",
                  status: "Disponible",
                  statusColor: "bg-green-500",
                  gradient: "from-purple-500 to-pink-500"
                }
              ].map((item, index) => (
                <Card key={index} className="border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 bg-gradient-to-r ${item.gradient} rounded-xl flex items-center justify-center shadow-lg`}>
                          <Users className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-bold text-lg">{item.title}</h3>
                          <p className="text-gray-600 text-sm">{item.members} • {item.nextSession}</p>
                        </div>
                      </div>
                      <Badge className={`${item.statusColor} text-white border-0`}>
                        {item.status}
                      </Badge>
                    </div>
                    <p className="text-gray-700 mb-4">{item.description}</p>
                    <Button className={`bg-gradient-to-r ${item.gradient} hover:shadow-lg transition-all duration-200`} size="sm">
                      {index === 0 ? "Rejoindre la session" : "Programmer une session"}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        );

      case 'analytics':
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <BarChart3 className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Analytics & Prédictions IA</h2>
                  <p className="text-indigo-100">Analyse détaillée de vos performances et recommandations</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-indigo-500" />
                    Progression Hebdomadaire
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { label: "Sessions complétées", value: "21/25", progress: 84 },
                      { label: "Heures d'étude", value: "15.5h", progress: 77 },
                      { label: "Précision quiz", value: "87%", progress: 87 }
                    ].map((stat, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">{stat.label}</span>
                          <span className="font-semibold">{stat.value}</span>
                        </div>
                        <Progress value={stat.progress} className="h-2" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-purple-500" />
                    Prédiction IA
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 text-center">
                    <div className="w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <span className="text-2xl font-bold text-white">85%</span>
                    </div>
                    <div className="text-lg font-semibold text-gray-800 mb-1">Probabilité d'atteindre 800</div>
                    <div className="text-sm text-gray-600">Estimation: {new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
                    <Badge className="mt-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white border-0">
                      Très probable
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        );

      default:
        return <div>Module non trouvé</div>;
    }
  };

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const parts = location.pathname.split('/').filter(Boolean);
    if (parts[0] === 'module' && parts[1]) {
      setActiveModule(parts[1]);
    } else if (location.pathname === '/') {
      setActiveModule('mastery');
    }
  }, [location.pathname]);

  const navigateToModule = (id, action) => {
    setActiveModule(id);
    const path = action ? `/module/${id}/${action}` : `/module/${id}`;
    if (location.pathname !== path) navigate(path);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* En-tête avec glassmorphism */}
      <header className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                  Euloge Learning Platform
                </h1>
                <p className="text-sm text-gray-500">IA & Neurosciences pour le TOEIC</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  {user?.email || 'Utilisateur'}
                </div>
                <div className="text-xs text-gray-500">Score: <AnimatedStat value={progressData.currentScore} /></div>
              </div>
              <Button onClick={() => logout()} variant="outline" size="sm" className="hidden sm:inline-flex hover:text-red-600 hover:border-red-200 transition-all duration-200">
                Déconnexion
              </Button>
              {/* Mobile hamburger menu button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
                aria-label="Menu"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile slide-out menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed top-16 left-0 right-0 bg-white/95 backdrop-blur-lg shadow-2xl border-b border-gray-200 max-h-[70vh] overflow-y-auto animate-fade-in-up">
            <nav className="p-4 space-y-2">
              {modules.map((module) => {
                const IconComponent = module.icon;
                const isActive = activeModule === module.id;
                return (
                  <button
                    key={module.id}
                    onClick={() => { setActiveModule(module.id); setMobileMenuOpen(false); }}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-200 ${isActive
                      ? `bg-gradient-to-r ${module.gradient} text-white shadow-lg`
                      : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isActive
                      ? 'bg-white/20'
                      : `bg-gradient-to-r ${module.gradient}`
                    }`}>
                      <IconComponent className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <div className={`font-semibold text-sm ${isActive ? 'text-white' : 'text-gray-800'}`}>{module.name}</div>
                      <div className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-500'}`}>{module.description}</div>
                    </div>
                  </button>
                );
              })}
              <div className="pt-3 border-t border-gray-200">
                <div className="px-4 py-2 text-sm text-gray-600">{user?.email}</div>
                <Button onClick={() => { logout(); setMobileMenuOpen(false); }} variant="outline" size="sm" className="w-full hover:text-red-600 hover:border-red-200">
                  Déconnexion
                </Button>
              </div>
            </nav>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-50 via-white to-emerald-100 p-6 md:p-10 border border-emerald-100 shadow-xl animate-fade-in-up">
          <div className="absolute -top-10 -left-10 h-40 w-40 rounded-full bg-emerald-300/30 blur-3xl" />
          <div className="absolute -bottom-10 -right-10 h-40 w-40 rounded-full bg-green-400/20 blur-3xl" />
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div>
              <h2 className="text-2xl md:text-4xl font-bold text-gray-900 leading-tight">Préparez le TOEIC avec l'IA</h2>
              <p className="mt-2 text-gray-600">Plans intelligents, répétition espacée, et analytics pour atteindre 800+.</p>
            </div>
            <div className="flex items-center gap-3">
              <Button className="bg-green-600 hover:bg-green-600/90 text-white shadow-lg px-5 py-2 rounded-md">Commencer gratuitement</Button>
              <Button variant="outline" className="border-2" onClick={() => navigateToModule('ai-tools', 'demo')}>Voir la démo</Button>
            </div>
          </div>
        </div>
      </div>

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Comment ça marche */}
        <div className="bg-white/80 backdrop-blur-lg border border-gray-100 rounded-2xl p-6 md:p-8 shadow-lg mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h3 className="text-xl md:text-2xl font-bold">Comment ça marche</h3>
              <p className="text-gray-600 mt-2">Suivez ces étapes simples pour créer un plan personnalisé et progresser efficacement vers votre objectif TOEIC.</p>
            </div>
            <div className="flex gap-3">
              <Button className="bg-green-600 hover:bg-green-600/90 text-white shadow-lg px-4 py-2 rounded-md">Commencer</Button>
              <Button variant="outline" className="border-2">Voir la démo</Button>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center text-white shadow">
                <BookOpen className="h-6 w-6" />
              </div>
              <div>
                <div className="font-semibold">1. Définissez votre objectif</div>
                <div className="text-sm text-gray-600">Indiquez votre score cible et votre disponibilité.</div>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-purple-500 to-indigo-500 flex items-center justify-center text-white shadow">
                <Clock className="h-6 w-6" />
              </div>
              <div>
                <div className="font-semibold">2. Suivez un plan intelligent</div>
                <div className="text-sm text-gray-600">Plan généré par IA + répétition espacée pour maximiser la rétention.</div>
              </div>
            </div>

            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center text-white shadow">
                <Zap className="h-6 w-6" />
              </div>
              <div>
                <div className="font-semibold">3. Pratiquez & analysez</div>
                <div className="text-sm text-gray-600">Quiz adaptatifs, chat IA et analytics pour ajuster votre trajectoire.</div>
              </div>
            </div>
          </div>
        </div>

        {/* Fonctionnalités principales (grid) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {modules.slice(0, 6).map((m, idx) => (
            <Card
              key={m.id}
              className="hover:shadow-xl transition-all duration-200 border-0 animate-fade-in-up"
              style={{ animationDelay: `${idx * 80}ms` }}
            >
              <CardContent className="p-5">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${m.gradient} flex items-center justify-center text-white shadow`}>
                    <m.icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold">{m.name}</div>
                    <div className="text-sm text-gray-600 mt-1">{m.description}</div>
                    <div className="mt-4 flex items-center gap-3">
                      <Button onClick={() => navigateToModule(m.id)} className={`bg-gradient-to-r ${m.gradient} text-white px-3 py-1 rounded-md`} size="sm">Voir</Button>
                      <Button onClick={() => navigateToModule(m.id, 'try')} variant="outline" size="sm">Essayer</Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar moderne avec glassmorphism — hidden on mobile */}
          <div className="hidden lg:block w-80 flex-shrink-0">
            <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-lg">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-500" />
                  Modules
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <nav className="space-y-2 p-4">
                  {modules.map((module) => {
                    const IconComponent = module.icon;
                    const isActive = activeModule === module.id;
                    return (
                      <button
                        key={module.id}
                        onClick={() => setActiveModule(module.id)}
                        className={`w-full flex items-center gap-4 px-4 py-4 text-left rounded-xl transition-all duration-200 group ${isActive
                          ? `bg-gradient-to-r ${module.gradient} text-white shadow-lg transform scale-105`
                          : 'hover:bg-gray-50 hover:shadow-md hover:transform hover:scale-102'
                          }`}
                      >
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${isActive
                          ? 'bg-white/20 backdrop-blur-sm'
                          : `bg-gradient-to-r ${module.gradient} group-hover:shadow-lg`
                          }`}>
                          <IconComponent className={`h-5 w-5 ${isActive ? 'text-white' : 'text-white'}`} />
                        </div>
                        <div>
                          <div className={`font-semibold text-sm ${isActive ? 'text-white' : 'text-gray-800'}`}>
                            {module.name}
                          </div>
                          <div className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                            {module.description}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </nav>
              </CardContent>
            </Card>

            {/* Progression rapide avec design amélioré */}
            <Card className="mt-6 border-0 shadow-xl bg-white/70 backdrop-blur-lg">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-blue-500" />
                  Progression TOEIC
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs mb-2">
                      <span className="text-gray-600">Vers 800 points</span>
                      <span className="font-semibold text-blue-600">
                        {Math.round(((progressData.currentScore - 400) / (progressData.targetScore - 400)) * 100)}%
                      </span>
                    </div>
                    <Progress
                      value={((progressData.currentScore - 400) / (progressData.targetScore - 400)) * 100}
                      className="h-3 bg-gray-200"
                    />
                  </div>
                  <div className="text-xs text-gray-500 bg-blue-50 rounded-lg p-3">
                    Vous êtes à <span className="font-semibold text-blue-600">{progressData.targetScore - progressData.currentScore} points</span> de votre objectif
                  </div>

                  {/* Stats rapides */}
                  <div className="grid grid-cols-2 gap-3 pt-2">
                    {[
                      { label: "Matières actives", value: 2, suffix: '', icon: BookOpen },
                      { label: "Progression globale", value: progressData.weeklyProgress, suffix: '%', icon: TrendingUp },
                      { label: "Temps cette semaine", value: progressData.totalHours, suffix: 'h', icon: Clock },
                      { label: "Streak moyen", value: progressData.averageStreak, suffix: ' jours', icon: Award }
                    ].map((stat, index) => (
                      <div key={index} className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-3 text-center group hover:shadow-md transition-all">
                        <stat.icon className="h-4 w-4 mx-auto mb-1 text-gray-600 group-hover:scale-110 transition-transform" />
                        <div className="text-lg font-bold text-gray-800">
                          <AnimatedStat value={stat.value} suffix={stat.suffix} />
                        </div>
                        <div className="text-xs text-gray-500">{stat.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recommandations avec design moderne */}
            <Card className="mt-6 border-0 shadow-xl bg-white/70 backdrop-blur-lg">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-purple-500" />
                  Recommandations IA
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {recommendations.map((rec, index) => {
                  const IconComponent = rec.icon;
                  return (
                    <div key={index} className={`bg-gradient-to-r ${rec.color} rounded-xl p-4 text-white shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105`}>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                          <IconComponent className="h-4 w-4" />
                        </div>
                        <div className="flex-1">
                          <div className="font-semibold text-sm mb-1">{rec.title}</div>
                          <div className="text-xs text-white/80">{rec.description}</div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Contenu principal */}
          <div className="flex-1">
            {renderModuleContent()}
          </div>
        </div>
      </div>

      {/* Footer avec attribution */}
      <footer className="bg-gradient-to-r from-gray-900 to-gray-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-bold mb-2">Euloge Learning Platform</h3>
              <p className="text-gray-300 text-sm">
                Plateforme d'apprentissage moderne basée sur l'IA et les neurosciences
              </p>
            </div>
            <div className="text-center md:text-right">
              <p className="text-sm text-gray-300 mb-1">
                Développé avec ❤️ par
              </p>
              <p className="text-lg font-bold text-blue-400">
                EULOGE MABIALA
              </p>
              <p className="text-xs text-gray-400 mt-1">
                                © {new Date().getFullYear()} - Tous droits réservés
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
