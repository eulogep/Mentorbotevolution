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
  Mic
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import DocumentUploader from './DocumentUploader';
import PlanGenerator from './PlanGenerator';
import ValidationChecklist from './ValidationChecklist';

const MasteryDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await fetch('/api/mastery/get-subjects');
      const data = await response.json();
      if (data.status === 'success') {
        setSubjects(data.subjects);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des matières:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'from-green-500 to-emerald-500';
      case 'in-progress': return 'from-blue-500 to-cyan-500';
      case 'not-started': return 'from-gray-400 to-gray-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'Maîtrisé';
      case 'in-progress': return 'En cours';
      case 'not-started': return 'À commencer';
      default: return 'Inconnu';
    }
  };

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 rounded-3xl p-8 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
              <BookOpen className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-3xl font-bold mb-2">Plans de Maîtrise Totale</h1>
              <p className="text-blue-100 text-lg">Transformez vos contenus en parcours d'apprentissage optimisés par l'IA</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: "Matières actives", value: subjects.length, icon: BookOpen },
              { label: "Concepts maîtrisés", value: subjects.reduce((acc, s) => acc + s.concepts.filter(c => c.status === 'completed').length, 0), icon: CheckCircle },
              { label: "Progression moyenne", value: `${Math.round(subjects.reduce((acc, s) => acc + s.progress, 0) / subjects.length || 0)}%`, icon: TrendingUp },
              { label: "Temps total", value: `${subjects.reduce((acc, s) => acc + s.total_time, 0)}h`, icon: Clock }
            ].map((stat, index) => (
              <div key={index} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
                <stat.icon className="h-6 w-6 mx-auto mb-2 text-white/80" />
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-white/70">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-4 right-4 w-32 h-32 bg-white/5 rounded-full"></div>
        <div className="absolute bottom-4 right-12 w-20 h-20 bg-white/5 rounded-full"></div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            title: "Uploader un Nouveau Contenu",
            description: "Transformez vos documents en plan de maîtrise",
            icon: Upload,
            gradient: "from-green-500 to-emerald-600",
            action: () => setActiveTab('upload')
          },
          {
            title: "Générer un Plan Personnalisé",
            description: "Créez un parcours adapté à vos objectifs",
            icon: Target,
            gradient: "from-purple-500 to-pink-600",
            action: () => setActiveTab('generator')
          },
          {
            title: "Valider vos Acquis",
            description: "Certifiez votre maîtrise par étapes",
            icon: CheckCircle,
            gradient: "from-blue-500 to-cyan-600",
            action: () => setActiveTab('validation')
          }
        ].map((action, index) => (
          <Card key={index} className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border-0 shadow-lg cursor-pointer" onClick={action.action}>
            <CardContent className="p-6 text-center">
              <div className={`w-16 h-16 bg-gradient-to-r ${action.gradient} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform duration-200`}>
                <action.icon className="h-8 w-8 text-white" />
              </div>
              <h3 className="font-bold text-lg mb-2 group-hover:text-blue-600 transition-colors">{action.title}</h3>
              <p className="text-gray-600 text-sm">{action.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Mes Matières */}
      <div>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Mes Matières</h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2].map((i) => (
              <Card key={i} className="border-0 shadow-lg">
                <CardContent className="p-6">
                  <div className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-6"></div>
                    <div className="space-y-3">
                      <div className="h-3 bg-gray-200 rounded"></div>
                      <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {subjects.map((subject) => (
              <Card key={subject.id} className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 border-0 shadow-lg">
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl font-bold text-gray-800 group-hover:text-blue-600 transition-colors">
                        {subject.name}
                      </CardTitle>
                      <CardDescription className="text-sm mt-1">
                        Objectif: {subject.target_score} • Actuel: {subject.current_score}
                      </CardDescription>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">{subject.progress}%</div>
                      <div className="text-xs text-gray-500">Progression</div>
                    </div>
                  </div>
                  <Progress value={subject.progress} className="h-2 mt-3" />
                </CardHeader>
                
                <CardContent className="pt-0">
                  <div className="mb-6">
                    <h4 className="font-semibold text-sm text-gray-700 mb-3 flex items-center gap-2">
                      <Brain className="h-4 w-4" />
                      Concepts ({subject.concepts.length})
                    </h4>
                    <div className="space-y-2">
                      {subject.concepts.map((concept) => (
                        <div key={concept.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${getStatusColor(concept.status)}`}></div>
                            <span className="text-sm font-medium">{concept.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {getStatusText(concept.status)}
                            </Badge>
                            <span className="text-sm font-semibold text-blue-600">{concept.mastery}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-center text-sm">
                    <div className="bg-blue-50 rounded-lg p-3">
                      <Clock className="h-4 w-4 mx-auto mb-1 text-blue-500" />
                      <div className="font-semibold text-blue-600">Prochaine session</div>
                      <div className="text-xs text-gray-600">{subject.next_session}</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-3">
                      <BarChart3 className="h-4 w-4 mx-auto mb-1 text-green-500" />
                      <div className="font-semibold text-green-600">Temps total</div>
                      <div className="text-xs text-gray-600">{subject.total_time}h</div>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-3">
                      <Award className="h-4 w-4 mx-auto mb-1 text-orange-500" />
                      <div className="font-semibold text-orange-600">Streak</div>
                      <div className="text-xs text-gray-600">{subject.streak} jours</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && subjects.length === 0 && (
          <Card className="border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors">
            <CardContent className="p-12 text-center">
              <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Plus className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Aucune matière pour le moment</h3>
              <p className="text-gray-500 mb-6">Commencez par uploader un document ou créer un plan personnalisé</p>
              <div className="flex gap-3 justify-center">
                <Button onClick={() => setActiveTab('upload')} className="bg-gradient-to-r from-blue-500 to-purple-600">
                  <Upload className="h-4 w-4 mr-2" />
                  Uploader un document
                </Button>
                <Button variant="outline" onClick={() => setActiveTab('generator')}>
                  <Target className="h-4 w-4 mr-2" />
                  Créer un plan
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-white/70 backdrop-blur-lg border-0 shadow-lg rounded-xl p-1">
          <TabsTrigger 
            value="overview" 
            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white rounded-lg transition-all duration-200"
          >
            <BookOpen className="h-4 w-4 mr-2" />
            Vue d'ensemble
          </TabsTrigger>
          <TabsTrigger 
            value="upload"
            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-green-500 data-[state=active]:to-emerald-600 data-[state=active]:text-white rounded-lg transition-all duration-200"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </TabsTrigger>
          <TabsTrigger 
            value="generator"
            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-500 data-[state=active]:to-pink-600 data-[state=active]:text-white rounded-lg transition-all duration-200"
          >
            <Target className="h-4 w-4 mr-2" />
            Générateur
          </TabsTrigger>
          <TabsTrigger 
            value="validation"
            className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-500 data-[state=active]:to-red-600 data-[state=active]:text-white rounded-lg transition-all duration-200"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Validation
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          {renderOverview()}
        </TabsContent>

        <TabsContent value="upload" className="mt-6">
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6 text-white mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Upload className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Upload de Contenu</h2>
                <p className="text-green-100">Transformez vos documents en plans de maîtrise intelligents</p>
              </div>
            </div>
          </div>
          <DocumentUploader onUploadSuccess={fetchSubjects} />
        </TabsContent>

        <TabsContent value="generator" className="mt-6">
          <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl p-6 text-white mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Target className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Générateur de Plans</h2>
                <p className="text-purple-100">Créez des parcours d'apprentissage personnalisés avec l'IA</p>
              </div>
            </div>
          </div>
          <PlanGenerator onPlanGenerated={fetchSubjects} />
        </TabsContent>

        <TabsContent value="validation" className="mt-6">
          <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-2xl p-6 text-white mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <CheckCircle className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Validation de Maîtrise</h2>
                <p className="text-orange-100">Certifiez votre apprentissage en 5 étapes de validation</p>
              </div>
            </div>
          </div>
          <ValidationChecklist subjects={subjects} onValidationComplete={fetchSubjects} />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MasteryDashboard;

