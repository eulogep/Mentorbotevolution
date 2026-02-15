/**
 * DocumentUploader Component
 * Connexion backend: /api/analysis/analyze-document (multipart/form-data)
 */
import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { Upload, FileText, Image, File, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';

const DocumentUploader = ({ onUploadComplete, onAnalysisStart }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);

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
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'image/jpeg', 'image/png'];
    const newFiles = fileArray
      .filter(file => validTypes.includes(file.type) && file.size <= 10 * 1024 * 1024)
      .map(file => ({
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploaded',
        concepts: [],
        exercises: []
      }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return <FileText className="h-6 w-6 text-red-500" />;
    if (type.includes('image')) return <Image className="h-6 w-6 text-blue-500" />;
    return <File className="h-6 w-6 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024; const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const analyzeDocuments = async () => {
    if (uploadedFiles.length === 0) return;
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    setError(null);
    onAnalysisStart?.();

    try {
      const analyzed = [];
      for (let i = 0; i < uploadedFiles.length; i++) {
        const item = uploadedFiles[i];
        setAnalysisProgress(Math.round((i / uploadedFiles.length) * 100));

        const form = new FormData();
        form.append('file', item.file, item.name);

        const res = await axios.post('/api/analysis/analyze-document', form);

        const data = res.data;
        if (data.status !== 'success') throw new Error(data.message || 'Erreur analyse');

        const concepts = (data.analysis?.concepts || []).map(c => c.name);
        const exGroups = data.generated_content?.exercises || [];
        const exercises = exGroups.flatMap(g => g.exercises?.map(e => e.type) || []);

        analyzed.push({
          id: item.id,
          name: item.name,
          size: item.size,
          type: item.type,
          status: 'analyzed',
          concepts,
          exercises,
          raw: data
        });

        // mettre à jour affichage incrémental
        setUploadedFiles(prev => prev.map(f => f.id === item.id ? { ...analyzed[analyzed.length - 1] } : f));
      }

      setAnalysisProgress(100);
      onUploadComplete?.(analyzed);
    } catch (e) {
      console.error(e);
      setError(e.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload de Contenu Éducatif
          </CardTitle>
          <CardDescription>
            Uploadez vos cours, documents ou images pour générer automatiquement un plan de maîtrise personnalisé
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">Glissez-déposez vos fichiers ici</p>
            <p className="text-sm text-gray-500 mb-4">ou cliquez pour sélectionner</p>
            <input type="file" multiple onChange={handleChange} accept=".pdf,.docx,.txt,.jpg,.jpeg,.png" className="hidden" id="file-upload" />
            <label htmlFor="file-upload">
              <Button variant="outline" className="cursor-pointer">Sélectionner des fichiers</Button>
            </label>
            <p className="text-xs text-gray-400 mt-2">PDF, DOCX, TXT, JPG, PNG (max 10MB)</p>
          </div>
        </CardContent>
      </Card>

      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Fichiers Uploadés ({uploadedFiles.length})</CardTitle>
            <CardDescription>Gérez vos documents et lancez l'analyse pour extraire les concepts clés</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getFileIcon(file.type)}
                    <div>
                      <p className="font-medium text-sm">{file.name}</p>
                      <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {file.status === 'analyzed' && (
                      <div className="flex items-center gap-1 text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span className="text-xs">Analysé</span>
                      </div>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => removeFile(file.id)} className="text-red-500 hover:text-red-700">Supprimer</Button>
                  </div>
                </div>
              ))}
            </div>

            {isAnalyzing && (
              <div className="mt-4">
                <div className="flex items-center gap-2 mb-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm font-medium">Analyse en cours...</span>
                </div>
                <Progress value={analysisProgress} className="w-full" />
                <p className="text-xs text-gray-500 mt-1">Extraction des concepts et génération d'exercices</p>
              </div>
            )}

            {error && (
              <Alert className="mt-4">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>Erreur: {error}</AlertDescription>
              </Alert>
            )}

            {!isAnalyzing && uploadedFiles.some(f => f.status === 'uploaded') && (
              <div className="mt-4">
                <Button onClick={analyzeDocuments} className="w-full">
                  <AlertCircle className="h-4 w-4 mr-2" />
                  Analyser les Documents
                </Button>
              </div>
            )}

            {uploadedFiles.some(f => f.status === 'analyzed') && (
              <Alert className="mt-4">
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>Analyse terminée ! Vous pouvez maintenant générer votre plan de maîtrise personnalisé.</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DocumentUploader;