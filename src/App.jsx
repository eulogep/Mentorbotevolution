import { useState } from 'react';
import { BookOpen, Brain, ExternalLink, LogOut, Menu, ShieldCheck, Target, X } from 'lucide-react';
import { Button } from './components/ui/button.jsx';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card.jsx';
import MasteryDashboard from './components/MasteryPlan/MasteryDashboard.jsx';
import { useAuth } from './context/AuthContext.jsx';

const evidenceMethods = [
  {
    title: 'Récupération active',
    description: 'Retrouvez une réponse sans regarder avant de comparer avec la correction et d’évaluer l’effort.',
    source: 'Méta-analyse sur la récupération espacée',
    href: 'https://link.springer.com/article/10.1007/s10648-020-09572-8',
  },
  {
    title: 'Espacement adaptatif',
    description: 'Le calendrier ajuste chaque carte à partir de vos revues et de votre rétention cible, sans intervalle universel figé.',
    source: 'Documentation FSRS / Anki',
    href: 'https://faqs.ankiweb.net/what-spaced-repetition-algorithm',
  },
  {
    title: 'Auto-explication guidée',
    description: 'Expliquez le concept, appliquez-le dans un exemple, puis vérifiez votre raisonnement.',
    source: 'Méta-analyse sur l’auto-explication',
    href: 'https://link.springer.com/article/10.1007/s10648-018-9434-x',
  },
];

function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-700 text-white shadow-sm"><Brain className="h-5 w-5" /></div>
            <div>
              <h1 className="text-base font-bold tracking-tight text-slate-950">Mentor Evolution</h1>
              <p className="text-xs text-slate-500">Apprentissage multi-domaines fondé sur les preuves</p>
            </div>
          </div>
          <div className="hidden items-center gap-3 sm:flex">
            <span className="max-w-52 truncate text-sm text-slate-600">{user?.email || 'Utilisateur'}</span>
            <Button onClick={logout} variant="outline" size="sm"><LogOut className="mr-2 h-4 w-4" />Déconnexion</Button>
          </div>
          <button onClick={() => setMobileMenuOpen((open) => !open)} className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 sm:hidden" aria-label="Ouvrir le menu">
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="border-t border-slate-100 bg-white px-4 py-3 sm:hidden">
            <p className="truncate px-2 py-2 text-sm text-slate-600">{user?.email || 'Utilisateur'}</p>
            <Button onClick={logout} variant="outline" size="sm" className="w-full"><LogOut className="mr-2 h-4 w-4" />Déconnexion</Button>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
        <section className="relative overflow-hidden rounded-3xl bg-slate-950 px-6 py-8 text-white shadow-xl sm:px-8 sm:py-10">
          <div className="absolute -right-24 -top-32 h-64 w-64 rounded-full bg-indigo-500/30 blur-3xl" />
          <div className="absolute -bottom-28 left-1/3 h-56 w-56 rounded-full bg-teal-400/15 blur-3xl" />
          <div className="relative max-w-3xl">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-indigo-100"><ShieldCheck className="h-3.5 w-3.5" />Données réelles, règles explicables</div>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Construisez des compétences durables, dans le domaine qui compte pour vous.</h2>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">Créez un parcours pour l’anglais, l’informatique ou tout autre domaine. Transformez vos contenus en pratique, répondez sans aide et laissez le calendrier s’ajuster à vos rappels. Les chiffres affichés proviennent de vos propres activités.</p>
          </div>
        </section>

        <div className="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1fr)_320px]">
          <section aria-label="Espace d’apprentissage">
            <MasteryDashboard />
          </section>

          <aside className="space-y-5" aria-label="Méthodes et garde-fous">
            <Card className="border-indigo-100 shadow-sm">
              <CardHeader className="pb-3"><CardTitle className="flex items-center gap-2 text-base"><Target className="h-4 w-4 text-indigo-700" />Votre méthode de travail</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {evidenceMethods.map((method) => (
                  <article key={method.title} className="border-l-2 border-indigo-200 pl-3">
                    <h3 className="text-sm font-semibold text-slate-900">{method.title}</h3>
                    <p className="mt-1 text-xs leading-5 text-slate-600">{method.description}</p>
                    <a className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-indigo-700 hover:text-indigo-900 hover:underline" href={method.href} target="_blank" rel="noreferrer">{method.source}<ExternalLink className="h-3 w-3" /></a>
                  </article>
                ))}
              </CardContent>
            </Card>

            <Card className="border-amber-200 bg-amber-50 shadow-sm">
              <CardContent className="p-5">
                <div className="flex items-start gap-3"><BookOpen className="mt-0.5 h-5 w-5 shrink-0 text-amber-800" /><div>
                  <h3 className="text-sm font-semibold text-amber-950">Ce que l’application ne prétend pas faire</h3>
                  <p className="mt-1 text-xs leading-5 text-amber-900">Elle ne déduit pas votre « style d’apprentissage », ne diagnostique pas votre cerveau et ne garantit ni score d’examen ni certification. Elle propose des pratiques et une planification transparentes, à ajuster avec votre expérience.</p>
                </div></div>
              </CardContent>
            </Card>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;
