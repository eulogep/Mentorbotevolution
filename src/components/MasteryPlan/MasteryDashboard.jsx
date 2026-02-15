/**
 * MISE À JOUR DES TABS: ajout Répétition espacée + Analytics
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, BookOpen, Target, CheckCircle, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import DocumentUploader from './DocumentUploader';
import PlanGenerator from './PlanGenerator';
import ValidationChecklist from './ValidationChecklist';
import SpacedReview from './SpacedReview';
import SpacedAnalytics from './SpacedAnalytics';

const MasteryDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzedDocs, setAnalyzedDocs] = useState([]);

  useEffect(() => { fetchSubjects(); }, []);

  const fetchSubjects = async () => {
    try {
      const response = await axios.get('/api/mastery/get-subjects');
      const data = response.data;
      if (data.status === 'success') setSubjects(data.subjects); else if (Array.isArray(data)) setSubjects(data);
    } catch (e) { console.error('Erreur lors du chargement des matières:', e); } finally { setLoading(false); }
  };

  const handleUploadComplete = (docs) => { setAnalyzedDocs(docs || []); fetchSubjects(); setActiveTab('generator'); };

  const renderOverview = () => (
    <div className="space-y-3">
      <Card className="border-0 shadow-xl bg-white/70 backdrop-blur-lg">
        <CardHeader><CardTitle className="text-lg flex items-center gap-2"><Sparkles className="h-5 w-5 text-purple-500" />Bienvenue</CardTitle></CardHeader>
        <CardContent>Générez vos plans, révisez vos cartes et suivez votre progression.</CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6 bg-white/70 backdrop-blur-lg border-0 shadow-lg rounded-xl p-1">
          <TabsTrigger value="overview"><BookOpen className="h-4 w-4 mr-2" />Vue d'ensemble</TabsTrigger>
          <TabsTrigger value="upload"><Upload className="h-4 w-4 mr-2" />Upload</TabsTrigger>
          <TabsTrigger value="generator"><Target className="h-4 w-4 mr-2" />Générateur</TabsTrigger>
          <TabsTrigger value="validation"><CheckCircle className="h-4 w-4 mr-2" />Validation</TabsTrigger>
          <TabsTrigger value="spaced"><Sparkles className="h-4 w-4 mr-2" />Répétition</TabsTrigger>
          <TabsTrigger value="analytics"><Sparkles className="h-4 w-4 mr-2" />Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">{renderOverview()}</TabsContent>

        <TabsContent value="upload" className="mt-6">
          <DocumentUploader onUploadComplete={handleUploadComplete} />
        </TabsContent>

        <TabsContent value="generator" className="mt-6">
          <PlanGenerator analyzedDocuments={analyzedDocs} onPlanGenerated={fetchSubjects} />
        </TabsContent>

        <TabsContent value="validation" className="mt-6">
          <ValidationChecklist concept={{ id: 'concept_ui', name: 'Concept' }} onValidationComplete={fetchSubjects} />
        </TabsContent>

        <TabsContent value="spaced" className="mt-6">
          <SpacedReview />
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <SpacedAnalytics />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MasteryDashboard;