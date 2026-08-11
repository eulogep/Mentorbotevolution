import { useEffect, useState } from 'react';
import axios from 'axios';
import { BookOpenCheck, CalendarDays, CheckCircle2, Clock3, Loader2, PlusCircle, Target } from 'lucide-react';
import { useAuth } from '../../context/AuthContext.jsx';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';

const practiceLabels = {
  recall: 'Rappel actif',
  explanation: 'Auto-explication',
  listening: 'Écoute',
  timed_reading: 'Lecture chronométrée',
  diagnostic: 'Diagnostic',
  practice: 'Pratique guidée',
  production: 'Production',
};

const PlanGenerator = ({ onPlanGenerated }) => {
  const { token } = useAuth();
  const [catalog, setCatalog] = useState({ domains: [], templates: [] });
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [isCustom, setIsCustom] = useState(false);
  const [customPath, setCustomPath] = useState({ name: '', domain: 'general', description: '', objectiveLabel: 'Compétence visée' });
  const [weeklyHours, setWeeklyHours] = useState('3');
  const [targetDate, setTargetDate] = useState('');
  const [targetScore, setTargetScore] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [createdPath, setCreatedPath] = useState(null);
  const [error, setError] = useState(null);

  const selectedTemplate = catalog.templates.find((template) => template.id === selectedTemplateId);

  useEffect(() => {
    const loadCatalog = async () => {
      try {
        setLoading(true);
        const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
        const response = await axios.get('/api/mastery/catalog', config);
        if (response.data.status !== 'success') throw new Error(response.data.message || 'Catalogue indisponible');
        setCatalog({ domains: response.data.domains || [], templates: response.data.templates || [] });
      } catch (requestError) {
        setError(requestError.message || 'Impossible de charger les parcours.');
      } finally {
        setLoading(false);
      }
    };
    if (token) loadCatalog();
  }, [token]);

  const selectTemplate = (templateId) => {
    setIsCustom(false);
    setSelectedTemplateId(templateId);
    setCreatedPath(null);
    setError(null);
    setTargetScore('');
  };

  const selectCustom = () => {
    setIsCustom(true);
    setSelectedTemplateId('');
    setCreatedPath(null);
    setError(null);
  };

  const createPath = async () => {
    const payload = {
      weekly_hours: weeklyHours || undefined,
      target_date: targetDate || undefined,
    };
    if (isCustom) {
      payload.name = customPath.name;
      payload.domain = customPath.domain;
      payload.description = customPath.description;
      payload.objective_type = 'competency';
      payload.objective_label = customPath.objectiveLabel || 'Compétence visée';
    } else {
      payload.template_id = selectedTemplateId;
      if (selectedTemplate?.objective_type === 'exam_score' && targetScore) payload.target_score = targetScore;
    }

    if ((!isCustom && !selectedTemplateId) || (isCustom && !customPath.name.trim())) {
      setError('Choisissez un modèle ou renseignez le nom de votre parcours.');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
      const response = await axios.post('/api/mastery/create-path', payload, config);
      if (response.data.status !== 'success') throw new Error(response.data.message || 'Création impossible');
      const createdSubject = { ...response.data.subject, starterPack: response.data.starter_pack || null };
      setCreatedPath(createdSubject);
      onPlanGenerated?.(createdSubject);
    } catch (requestError) {
      setError(requestError.message || 'Impossible de créer le parcours.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="flex items-center gap-2 text-sm text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Chargement des parcours disponibles…</div>;

  return (
    <div className="space-y-6">
      <Card className="border-slate-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg"><BookOpenCheck className="h-5 w-5 text-indigo-700" />Créer un parcours de maîtrise</CardTitle>
          <CardDescription>Choisissez un modèle comme point de départ ou définissez votre propre domaine. Les modèles organisent un parcours ; ils ne mesurent pas votre niveau et ne prédisent pas votre réussite.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">Erreur : {error}</div>}

          <section aria-labelledby="template-title">
            <div className="mb-3 flex items-center justify-between gap-3"><h3 id="template-title" className="font-semibold text-slate-900">Modèles de parcours</h3><Button type="button" size="sm" variant={isCustom ? 'default' : 'outline'} onClick={selectCustom}><PlusCircle className="mr-2 h-4 w-4" />Parcours libre</Button></div>
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {catalog.templates.map((template) => (
                <button type="button" key={template.id} onClick={() => selectTemplate(template.id)} className={`rounded-xl border p-4 text-left transition ${selectedTemplateId === template.id && !isCustom ? 'border-indigo-600 bg-indigo-50 ring-1 ring-indigo-600' : 'border-slate-200 bg-white hover:border-indigo-300 hover:bg-slate-50'}`}>
                  <div className="flex items-start justify-between gap-2"><span className="font-semibold text-slate-900">{template.title}</span><Badge variant="outline" className="shrink-0 text-xs">{template.domain_label}</Badge></div>
                  <p className="mt-2 text-xs leading-5 text-slate-600">{template.description}</p>
                  <p className="mt-3 text-xs font-medium text-indigo-700">{template.concept_count ? `${template.concept_count} notions initiales` : 'Structure de départ personnalisable'}</p>
                </button>
              ))}
            </div>
          </section>

          {isCustom ? (
            <section className="space-y-4 rounded-2xl border border-indigo-100 bg-indigo-50/50 p-5" aria-labelledby="custom-title">
              <h3 id="custom-title" className="font-semibold text-slate-900">Votre parcours libre</h3>
              <div className="grid gap-4 md:grid-cols-2"><div><Label htmlFor="custom-path-name">Nom du parcours</Label><Input id="custom-path-name" value={customPath.name} onChange={(event) => setCustomPath((current) => ({ ...current, name: event.target.value }))} placeholder="Ex. Administration système Linux" className="mt-2 bg-white" /></div><div><Label htmlFor="custom-domain">Domaine</Label><select id="custom-domain" value={customPath.domain} onChange={(event) => setCustomPath((current) => ({ ...current, domain: event.target.value }))} className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-600">{catalog.domains.map((domain) => <option key={domain.id} value={domain.id}>{domain.label}</option>)}</select></div></div>
              <div><Label htmlFor="custom-objective">Objectif formulé</Label><Input id="custom-objective" value={customPath.objectiveLabel} onChange={(event) => setCustomPath((current) => ({ ...current, objectiveLabel: event.target.value }))} placeholder="Ex. Savoir automatiser des tableaux mensuels" className="mt-2 bg-white" /></div>
              <div><Label htmlFor="custom-description">Contexte ou résultat attendu</Label><Textarea id="custom-description" value={customPath.description} onChange={(event) => setCustomPath((current) => ({ ...current, description: event.target.value }))} placeholder="Ce que vous voulez savoir comprendre, réaliser ou expliquer…" className="mt-2 min-h-24 bg-white" /></div>
            </section>
          ) : selectedTemplate && (
            <section className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-5" aria-label="Détails du modèle sélectionné">
              <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start"><div><h3 className="font-semibold text-slate-900">{selectedTemplate.title}</h3><p className="mt-1 text-sm text-slate-600">{selectedTemplate.description}</p></div><Badge className="w-fit bg-indigo-700">{selectedTemplate.domain_label}</Badge></div>
              <div className="mt-4 flex flex-wrap gap-2">{selectedTemplate.practice_types.map((practiceType) => <Badge key={practiceType} variant="outline">{practiceLabels[practiceType] || practiceType}</Badge>)}</div>
              {selectedTemplate.objective_type === 'exam_score' && <div className="mt-4 max-w-xs"><Label htmlFor="target-score">{selectedTemplate.objective_label}</Label><Input id="target-score" type="number" min="0" value={targetScore} onChange={(event) => setTargetScore(event.target.value)} placeholder="Facultatif" className="mt-2 bg-white" /></div>}
            </section>
          )}

          <section className="grid gap-4 md:grid-cols-2" aria-label="Cadre de travail">
            <div><Label htmlFor="weekly-hours" className="flex items-center gap-2"><Clock3 className="h-4 w-4" />Temps disponible par semaine</Label><Input id="weekly-hours" type="number" min="0.25" max="80" step="0.25" value={weeklyHours} onChange={(event) => setWeeklyHours(event.target.value)} className="mt-2" /></div>
            <div><Label htmlFor="target-date" className="flex items-center gap-2"><CalendarDays className="h-4 w-4" />Échéance, si vous en avez une</Label><Input id="target-date" type="date" value={targetDate} onChange={(event) => setTargetDate(event.target.value)} className="mt-2" /></div>
          </section>

          <Button onClick={createPath} disabled={submitting || (!isCustom && !selectedTemplateId)} className="w-full bg-indigo-700 hover:bg-indigo-800">{submitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Création en cours…</> : <><Target className="mr-2 h-4 w-4" />Créer ce parcours</>}</Button>
        </CardContent>
      </Card>

      {createdPath && <Card className="border-emerald-200 bg-emerald-50 shadow-sm"><CardContent className="flex gap-3 p-5"><CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" /><div><p className="font-semibold text-emerald-950">Parcours créé : {createdPath.name}</p>{createdPath.starterPack ? <p className="mt-1 text-sm text-emerald-900">{createdPath.starterPack.cards_created} cartes de vocabulaire professionnel ont été ajoutées pour démarrer les révisions. Elles constituent un socle éditorial à compléter par vos propres contenus, l’écoute et la pratique.</p> : <p className="mt-1 text-sm text-emerald-900">Vous pouvez maintenant sélectionner une notion, importer vos propres ressources, puis créer les cartes ou activités pertinentes.</p>}</div></CardContent></Card>}
    </div>
  );
};

export default PlanGenerator;
