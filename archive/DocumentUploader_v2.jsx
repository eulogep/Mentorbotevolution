import React, { useState, useCallback } from 'react';
import { Upload, FileText, Image, File, CheckCircle, AlertCircle, Loader2, Brain, Target, BookOpen, Zap } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

const DocumentUploader = ({ onUploadComplete, onAnalysisStart }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(file => {
      // Support étendu pour plus de formats
      const validTypes = [
        'application/pdf', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain', 
        'image/jpeg', 
        'image/png',
        'image/gif',
        'image/webp'
      ];
      return validTypes.includes(file.type) && file.size <= 50 * 1024 * 1024; // 50MB max
    });

    const newFiles = validFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploaded',
      concepts: [],
      exercises: [],
      difficulty: 'medium',
      estimatedTime: 0,
      prerequisites: []
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return <FileText className="h-6 w-6 text-red-500" />;
    if (type.includes('image')) return <Image className="h-6 w-6 text-blue-500" />;
    if (type.includes('presentation')) return <FileText className="h-6 w-6 text-orange-500" />;
    return <File className="h-6 w-6 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Simulation d'analyse sémantique avancée
  const performSemanticAnalysis = async (file) => {
    // Simulation de l'OCR et analyse NLP
    const mockAnalysis = {
      concepts: [
        { name: 'Conditional Sentences', difficulty: 'high', importance: 0.9 },
        { name: 'Past Perfect Tense', difficulty: 'medium', importance: 0.7 },
        { name: 'Business Vocabulary', difficulty: 'medium', importance: 0.8 },
        { name: 'Listening Comprehension', difficulty: 'high', importance: 0.9 }
      ],
      prerequisites: ['Basic Grammar', 'Present Tense'],
      estimatedTime: Math.floor(Math.random() * 120) + 30, // 30-150 minutes
      complexity: Math.random() > 0.5 ? 'high' : 'medium',
      exercises: [
        { type: 'flashcard', count: 15, topic: 'Vocabulary' },
        { type: 'quiz', count: 10, topic: 'Grammar' },
        { type: 'listening', count: 5, topic: 'Comprehension' },
        { type: 'writing', count: 3, topic: 'Application' }
      ],
      fuzzyAreas: [
        'Complex conditional structures need more examples',
        'Business context vocabulary requires practical application'
      ]
    };

    return mockAnalysis;
  };

  const analyzeDocuments = async () => {
    if (uploadedFiles.length === 0) return;

    setIsAnalyzing(true);
    setAnalysisProgress(0);
    onAnalysisStart?.();

    try {
      const results = [];
      
      for (let i = 0; i < uploadedFiles.length; i++) {
        const file = uploadedFiles[i];
        setAnalysisProgress((i / uploadedFiles.length) * 100);

        // Analyse sémantique avancée
        const analysis = await performSemanticAnalysis(file);
        
        // Simulation du temps d'analyse
        await new Promise(resolve => setTimeout(resolve, 3000));

        // Mise à jour du fichier avec les résultats d'analyse
        const updatedFile = {
          ...file,
          status: 'analyzed',
          concepts: analysis.concepts,
          exercises: analysis.exercises,
          difficulty: analysis.complexity,
          estimatedTime: analysis.estimatedTime,
          prerequisites: analysis.prerequisites,
          fuzzyAreas: analysis.fuzzyAreas
        };

        setUploadedFiles(prev => prev.map(f => 
          f.id === file.id ? updatedFile : f
        ));

        results.push(updatedFile);
      }

      setAnalysisProgress(100);
      setAnalysisResults({
        totalFiles: results.length,
        totalConcepts: results.reduce((acc, file) => acc + file.concepts.length, 0),
        totalTime: results.reduce((acc, file) => acc + file.estimatedTime, 0),
        avgDifficulty: results.filter(f => f.difficulty === 'high').length / results.length > 0.5 ? 'high' : 'medium'
      });

      onUploadComplete?.(results);
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Zone d'upload améliorée */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Upload et Analyse Intelligente v2.0
          </CardTitle>
          <CardDescription>
            Téléchargez vos documents (PDF, Word, PowerPoint, images) pour une analyse sémantique avancée
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Glissez-déposez vos fichiers ici
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Formats supportés: PDF, Word, PowerPoint, Images (max 50MB)
            </p>
            <input
              type="file"
              multiple
              onChange={handleChange}
              className="hidden"
              id="file-upload"
              accept=".pdf,.docx,.pptx,.txt,.jpg,.jpeg,.png,.gif,.webp"
            />
            <label htmlFor="file-upload">
              <Button variant="outline" className="cursor-pointer">
                Sélectionner des fichiers
              </Button>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Liste des fichiers uploadés */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Fichiers Téléchargés ({uploadedFiles.length})</CardTitle>
            <div className="flex gap-2">
              <Button 
                onClick={analyzeDocuments} 
                disabled={isAnalyzing}
                className="flex items-center gap-2"
              >
                {isAnalyzing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Brain className="h-4 w-4" />
                )}
                {isAnalyzing ? 'Analyse en cours...' : 'Analyser les documents'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isAnalyzing && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Analyse sémantique en cours...</span>
                  <span>{Math.round(analysisProgress)}%</span>
                </div>
                <Progress value={analysisProgress} className="w-full" />
              </div>
            )}

            <div className="space-y-4">
              {uploadedFiles.map((file) => (
                <div key={file.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      {getFileIcon(file.type)}
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {file.status === 'analyzed' && (
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      )}
                      <Badge variant={file.status === 'analyzed' ? 'default' : 'secondary'}>
                        {file.status === 'analyzed' ? 'Analysé' : 'En attente'}
                      </Badge>
                    </div>
                  </div>

                  {file.status === 'analyzed' && (
                    <div className="mt-4 space-y-3">
                      <Tabs defaultValue="concepts" className="w-full">
                        <TabsList className="grid w-full grid-cols-4">
                          <TabsTrigger value="concepts">Concepts</TabsTrigger>
                          <TabsTrigger value="exercises">Exercices</TabsTrigger>
                          <TabsTrigger value="planning">Planning</TabsTrigger>
                          <TabsTrigger value="analysis">Analyse</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="concepts" className="space-y-2">
                          <div className="flex flex-wrap gap-2">
                            {file.concepts.map((concept, idx) => (
                              <Badge 
                                key={idx} 
                                className={getDifficultyColor(concept.difficulty)}
                              >
                                {concept.name}
                              </Badge>
                            ))}
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="exercises" className="space-y-2">
                          <div className="grid grid-cols-2 gap-4">
                            {file.exercises.map((exercise, idx) => (
                              <div key={idx} className="flex items-center gap-2">
                                <Target className="h-4 w-4 text-blue-500" />
                                <span className="text-sm">
                                  {exercise.count} {exercise.type} - {exercise.topic}
                                </span>
                              </div>
                            ))}
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="planning" className="space-y-2">
                          <div className="grid grid-cols-2 gap-4">
                            <div className="flex items-center gap-2">
                              <BookOpen className="h-4 w-4 text-green-500" />
                              <span className="text-sm">Temps estimé: {file.estimatedTime} min</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Zap className="h-4 w-4 text-orange-500" />
                              <span className="text-sm">Difficulté: {file.difficulty}</span>
                            </div>
                          </div>
                          {file.prerequisites.length > 0 && (
                            <div>
                              <p className="text-sm font-medium mb-1">Prérequis:</p>
                              <div className="flex flex-wrap gap-1">
                                {file.prerequisites.map((prereq, idx) => (
                                  <Badge key={idx} variant="outline" className="text-xs">
                                    {prereq}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </TabsContent>
                        
                        <TabsContent value="analysis" className="space-y-2">
                          {file.fuzzyAreas && (
                            <div>
                              <p className="text-sm font-medium mb-2">Zones nécessitant attention:</p>
                              <div className="space-y-1">
                                {file.fuzzyAreas.map((area, idx) => (
                                  <Alert key={idx}>
                                    <AlertCircle className="h-4 w-4" />
                                    <AlertDescription className="text-xs">
                                      {area}
                                    </AlertDescription>
                                  </Alert>
                                ))}
                              </div>
                            </div>
                          )}
                        </TabsContent>
                      </Tabs>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Résumé de l'analyse */}
      {analysisResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Analyse Terminée
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{analysisResults.totalFiles}</p>
                <p className="text-sm text-gray-600">Fichiers analysés</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{analysisResults.totalConcepts}</p>
                <p className="text-sm text-gray-600">Concepts identifiés</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">{analysisResults.totalTime}</p>
                <p className="text-sm text-gray-600">Minutes d'étude</p>
              </div>
              <div className="text-center">
                <Badge className={getDifficultyColor(analysisResults.avgDifficulty)}>
                  {analysisResults.avgDifficulty}
                </Badge>
                <p className="text-sm text-gray-600 mt-1">Difficulté moyenne</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DocumentUploader;

