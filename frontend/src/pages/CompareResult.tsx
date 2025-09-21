import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Header from '../components/Header';

function formatNumber(n: any) {
    if (n === undefined || n === null) return '-';
    if (typeof n === 'number') return Math.round(n);
    const parsed = parseFloat(String(n));
    return Number.isNaN(parsed) ? '-' : Math.round(parsed);
}

function SingleResultView({ r }: { r: any }) {
    const { filename, score, strengths, weaknesses, summary, matched_skills, reasoning } = r;
    return (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-xl font-semibold">{filename || 'CV'}</h2>
                    {summary && <p className="text-gray-600 mt-1">{summary}</p>}
                </div>
                <div className="text-right">
                    <div className="text-sm text-gray-500">Score</div>
                    <div className="text-2xl font-bold text-[#F8485D]">{formatNumber(score)}</div>
                </div>
            </div>

            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-gray-100 p-3 rounded-[25px]">
                    <h4 className="font-semibold">Points forts</h4>
                    {strengths && strengths.length > 0 ? <ul className="list-disc list-inside text-sm mt-2">{strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}</ul> : <p className="text-gray-500 mt-2">Aucun</p>}
                </div>
                <div className="border border-gray-100 p-3 rounded-[25px]">
                    <h4 className="font-semibold">Points faibles</h4>
                    {weaknesses && weaknesses.length > 0 ? <ul className="list-disc list-inside text-sm mt-2">{weaknesses.map((w: string, i: number) => <li key={i}>{w}</li>)}</ul> : <p className="text-gray-500 mt-2">Aucun</p>}
                </div>
            </div>

            <div className="mt-4">
                <div className="border border-gray-100 p-3 rounded-[25px]">
                    <h4 className="font-semibold">Compétences</h4>
                    {matched_skills && matched_skills.length > 0 ? <div className="flex flex-wrap gap-2 mt-2">{matched_skills.map((m: string, i: number) => <span key={i} className="px-3 py-1 rounded-full bg-gray-100 text-sm">{m}</span>)}</div> : <p className="text-gray-500 mt-2">Aucune</p>}
                </div>
            </div>

            <div className="mt-4">
                <div className="border border-gray-100 p-3 rounded-[25px]">
                    <h4 className="font-semibold">Raisonnement</h4>
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 mt-2">{reasoning || JSON.stringify(r, null, 2)}</pre>
                </div>
            </div>

            {/* 'Voir en détail' button removed as requested */}
        </div>
    );
}

export default function CompareResult() {
    const location = useLocation();
    const navigate = useNavigate();

    // If navigated with a single result (via 'Voir en détail'), show single detail view
    const maybeSingle: any = (location.state && (location.state as any).result) || null;
    let results: any[] | null = null;

    if (!maybeSingle) {
        // Try router state (results array) then sessionStorage
        results = (location.state && (location.state as any).results) || null;
        if (!results) {
            try { const raw = sessionStorage.getItem('last_compare_results'); if (raw) results = JSON.parse(raw); } catch (_e) { }
        }
    }

    if (maybeSingle) {
        const r = maybeSingle;
        return (
            <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
                <Header title="" />
                <div className="container mx-auto px-4 py-12">
                    <div className="max-w-4xl mx-auto space-y-6">
                        <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-6">
                            <h1 className="text-2xl font-semibold">Détail du résultat</h1>
                            <p className="text-gray-600 mt-1">Analyse approfondie expliquant pourquoi ce profil est (ou n'est pas) adapté à la mission.</p>
                        </div>

                        <SingleResultView r={r} />

                        <div className="flex justify-start">
                            <button className="px-4 py-2 rounded-xl border" onClick={() => navigate('/compare')}>Retour à la comparaison</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (!results || !Array.isArray(results) || results.length === 0) {
        return (
            <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
                <Header title="" />
                <div className="container mx-auto px-4 py-12">
                    <div className="max-w-3xl mx-auto text-center">
                        <h2 className="text-2xl font-semibold mb-4">Aucun résultat disponible</h2>
                        <p className="text-gray-600 mb-6">Retournez à la page de comparaison pour relancer l'analyse.</p>
                        <div className="flex justify-center">
                            <button className="px-4 py-2 rounded-xl bg-[#F8485D] text-white" onClick={() => navigate('/compare')}>Retour à la comparaison</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // If multiple results, render overview list and allow navigating to single detail (same page)
    return (
        <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
            <Header title="" />
            <div className="container mx-auto px-4 py-12">
                <div className="max-w-4xl mx-auto space-y-6">
                    <div className="bg-white rounded-2xl shadow-md border border-gray-200 p-6">
                        <h1 className="text-2xl font-semibold">Résultats de la comparaison</h1>
                        <p className="text-gray-600 mt-1">CVs classés du plus pertinent au moins pertinent</p>
                    </div>
        <div className="grid grid-cols-1 gap-4">
                        {results.map((r: any, idx: number) => (
                            <div key={`ov-${idx}`} className={`${idx === 0 ? 'border-2 border-[#F8485D] p-2 rounded-[25px]' : 'p-2 border border-gray-100 rounded-[25px]'}`}>
                                <SingleResultView r={r} />
                            </div>
                        ))}
                    </div>

                    <div className="flex justify-start">
                        <button className="px-4 py-2 rounded-xl border" onClick={() => navigate('/compare')}>Retour à la comparaison</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
