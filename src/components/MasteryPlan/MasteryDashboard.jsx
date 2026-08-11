import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { BarChart3, BookOpen, BrainCircuit, CheckCircle, ClipboardCheck, Clock3, FileUp, ListChecks, Sparkles, Target } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import DocumentUploader from './DocumentUploader';
import PlanGenerator from './PlanGenerator';
import ValidationChecklist from './ValidationChecklist';
import SpacedReview from './SpacedReview';
import SpacedAnalytics from './SpacedAnalytics';
import AdaptiveLearning from './AdaptiveLearning';
import ToeicReadingDiagnostic from './ToeicReadingDiagnostic';
import { useAuth } from '../../context/AuthContext.jsx';

const MasteryDashboard = () => {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [subjects, setSubjects] = useState([]);
  const [dueCount, setDueCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [analyzedDocs, setAnalyzedDocs] = useState([]);
  const [selectedConceptId, setSelectedConceptId] = useState('');
  const [reviewDomain, setReviewDomain] = useState(null);
  const [error, setError] = useState(null);

  const concepts = useMemo(
    () => subjects.flatMap((subject) => (subject.concepts || []).map((concept) => ({ ...concept, subjectName: subject.name }))),
    [subjects],
  );
  const selectedConcept = concepts.find((concept) => String(concept.id) === String(selectedConceptId));

  const refreshDashboard = useCallback(async () => {
    try {
      const authConfig = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
      setLoading(true);
      setError(null);
      const [subjectsResponse, dueResponse] = await Promise.all([
        axios.get('/api/mastery/get-subjects', authConfig),
        axios.get('/api/spaced-repetition/get-due-cards?limit=1', authConfig),
      ]);
      const subjectPayload = subjectsResponse.data;
      const nextSubjects = subjectPayload.status === 'success' ? subjectPayload.subjects : (Array.isArray(subjectPayload) ? subjectPayload : []);
      setSubjects(nextSubjects || []);
      setDueCount(dueResponse.data?.total_due || 0);
      setSelectedConceptId((current) => current || (nextSubjects?.[0]?.concepts?.[0]?.id ? String(nextSubjects[0].concepts[0].id) : ''));
    } catch (requestError) {
      setError(requestError.message || 'Impossible de charger votre espace d’apprentissage.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      refreshDashboard();
      return;
    }
    setSubjects([]);
    setDueCount(0);
    setLoading(false);
  }, [token, refreshDashboard]);

  const handleUploadComplete = (documents) => {
    setAnalyzedDocs(documents || []);
    refreshDashboard();
    setActiveTab('generator');
  };

  const selectConceptForValidation = (conceptId) => {
    setSelectedConceptId(String(conceptId));
    setActiveTab('validation');
  };

  const startDomainReview = (domain) => {
    setReviewDomain(domain);
    setActiveTab('spaced');
  };

  const renderOverview = () => (
    <div className="space-y-5">
      {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}
      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="border-slate-200 shadow-sm"><CardContent className="p-5"><div className="flex items-start justify-between"><div><p className="text-xs font-medium uppercase tracking-wide text-slate-500">Parcours actifs</p><p className="mt-2 text-3xl font-bold text-slate-950">{loading ? '—' : subjects.length}</p></div><BookOpen className="h-5 w-5 text-indigo-700" /></div><p className="mt-3 text-xs text-slate-600">Créez un parcours pour l’anglais, l’informatique ou toute autre compétence.</p></CardContent></Card>
        <Card className="border-slate-200 shadow-sm"><CardContent className="p-5"><div className="flex items-start justify-between"><div><p className="text-xs font-medium uppercase tracking-wide text-slate-500">À revoir maintenant</p><p className="mt-2 text-3xl font-bold text-slate-950">{loading ? '—' : dueCount}</p></div><Clock3 className="h-5 w-5 text-emerald-700" /></div><p className="mt-3 text-xs text-slate-600">Ce total reflète les échéances enregistrées dans votre calendrier.</p><Button size="sm" className="mt-3 bg-emerald-700 hover:bg-emerald-800" onClick={() => { setReviewDomain(null); setActiveTab('spaced'); }}>Démarrer la session</Button></CardContent></Card>
      </div>

      <Card className="border-slate-200 shadow-sm">
        <CardHeader><CardTitle className="flex items-center gap-2 text-base"><ListChecks className="h-4 w-4 text-indigo-700" />Vos compétences et notions</CardTitle><CardDescription>Choisissez une notion réelle pour lancer une auto-explication guidée ou une pratique de rappel.</CardDescription></CardHeader>
        <CardContent>
          {loading ? <p className="text-sm text-slate-500">Chargement de vos contenus…</p> : concepts.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center"><p className="font-medium text-slate-800">Votre espace est prêt à être structuré.</p><p className="mt-1 text-sm text-slate-600">Créez d’abord un parcours ou choisissez un modèle : TOEIC, informatique, Excel, Power BI, réseau ou cybersécurité.</p><Button className="mt-4" variant="outline" onClick={() => setActiveTab('generator')}><Target className="mr-2 h-4 w-4" />Créer un parcours</Button></div>
          ) : (
            <div className="space-y-3">{concepts.map((concept) => <div key={concept.id} className="flex flex-col gap-3 rounded-xl border border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between"><div><p className="font-semibold text-slate-900">{concept.name}</p><p className="mt-1 text-xs text-slate-500">{concept.subjectName} · {concept.competency_type || 'knowledge'} · Progression : {concept.mastery || 0} %</p></div><Button size="sm" variant="outline" onClick={() => selectConceptForValidation(concept.id)}>Auto-expliquer</Button></div>)}</div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="grid h-auto w-full grid-cols-3 gap-1 rounded-xl bg-slate-100 p-1 md:grid-cols-8">
        <TabsTrigger value="overview" className="text-xs sm:text-sm"><BookOpen className="mr-1.5 h-4 w-4" />Aujourd’hui</TabsTrigger>
        <TabsTrigger value="upload" className="text-xs sm:text-sm"><FileUp className="mr-1.5 h-4 w-4" />Importer</TabsTrigger>
        <TabsTrigger value="generator" className="text-xs sm:text-sm"><Target className="mr-1.5 h-4 w-4" />Parcours</TabsTrigger>
        <TabsTrigger value="diagnostic" className="text-xs sm:text-sm"><ClipboardCheck className="mr-1.5 h-4 w-4" />Diagnostiquer</TabsTrigger>
        <TabsTrigger value="validation" className="text-xs sm:text-sm"><CheckCircle className="mr-1.5 h-4 w-4" />Expliquer</TabsTrigger>
        <TabsTrigger value="spaced" className="text-xs sm:text-sm"><Sparkles className="mr-1.5 h-4 w-4" />Réviser</TabsTrigger>
        <TabsTrigger value="adaptive" className="text-xs sm:text-sm"><BrainCircuit className="mr-1.5 h-4 w-4" />Adapter</TabsTrigger>
        <TabsTrigger value="analytics" className="text-xs sm:text-sm"><BarChart3 className="mr-1.5 h-4 w-4" />Données</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="mt-6">{renderOverview()}</TabsContent>
      <TabsContent value="upload" className="mt-6"><DocumentUploader onUploadComplete={handleUploadComplete} /></TabsContent>
      <TabsContent value="generator" className="mt-6"><PlanGenerator analyzedDocuments={analyzedDocs} onPlanGenerated={refreshDashboard} /></TabsContent>
      <TabsContent value="diagnostic" className="mt-6"><ToeicReadingDiagnostic onRemediationCreated={refreshDashboard} /></TabsContent>
      <TabsContent value="validation" className="mt-6 space-y-4">
        {concepts.length ? <><Card className="border-slate-200 shadow-sm"><CardContent className="p-4"><label htmlFor="concept-select" className="mb-2 block text-sm font-semibold text-slate-800">Notion à expliquer</label><select id="concept-select" value={selectedConceptId} onChange={(event) => setSelectedConceptId(event.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600">{concepts.map((concept) => <option key={concept.id} value={concept.id}>{concept.subjectName} — {concept.name}</option>)}</select></CardContent></Card>{selectedConcept && <ValidationChecklist concept={selectedConcept} onValidationComplete={refreshDashboard} />}</> : <Card><CardContent className="p-6 text-sm text-slate-600">Créez d’abord une matière et une notion pour démarrer une auto-explication.</CardContent></Card>}
      </TabsContent>
      <TabsContent value="spaced" className="mt-6"><SpacedReview key={reviewDomain || 'all'} domain={reviewDomain} /></TabsContent>
      <TabsContent value="adaptive" className="mt-6"><AdaptiveLearning onStartDomainSession={startDomainReview} /></TabsContent>
      <TabsContent value="analytics" className="mt-6"><SpacedAnalytics /></TabsContent>
    </Tabs>
  );
};

export default MasteryDashboard;
