"use client";

import React, { useState } from "react";
import {
  Search,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  TrendingUp,
  Brain,
  Layers,
  FileCheck,
} from "lucide-react";
import { EvidenceItem, Hypothesis, InvestigationResult, runInvestigation } from "@/lib/api";

interface AIInvestigationConsoleProps {
  datasetId: string;
  onOpenEvidence: (ev: EvidenceItem) => void;
  onNavigateToSimulator: () => void;
  onNavigateToGraph: (question?: string) => void;
  prefillQuestion?: string;
}

export const AIInvestigationConsole: React.FC<AIInvestigationConsoleProps> = ({
  datasetId,
  onOpenEvidence,
  onNavigateToSimulator,
  onNavigateToGraph,
  prefillQuestion = "",
}) => {
  const [question, setQuestion] = useState(prefillQuestion);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const sampleQuestions = [
    "Why did MRR drop in August 2025?",
    "Which product category generates the highest profit?",
    "What drove churn rate variance across segments?",
    "Why did sales fall in the South region?",
  ];

  const handleInvestigate = async (qText?: string) => {
    const query = qText || question;
    if (!query.trim() || !datasetId) return;

    setIsLoading(true);
    setError(null);
    try {
      const data = await runInvestigation(datasetId, query);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to execute investigation");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Console Header */}
      <div className="clean-card p-6 rounded-2xl">
        <div className="max-w-3xl mx-auto space-y-4">
          <div className="text-center space-y-1">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              AI Business Investigation
            </h1>
            <p className="text-xs text-slate-500">
              Formulate hypotheses, calculate exact SQL proofs, and attach verifiable evidence.
            </p>
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleInvestigate();
            }}
            className="relative flex items-center"
          >
            <div className="absolute left-4 text-slate-400">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input
              id="investigation-input"
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Why did revenue drop in August? Or what drove churn up?"
              disabled={isLoading}
              className="w-full bg-white border border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 rounded-xl py-3 pl-11 pr-28 text-sm text-slate-900 placeholder-slate-400 focus:outline-none transition shadow-xs"
            />
            <button
              id="submit-investigation-btn"
              type="submit"
              disabled={isLoading || !question.trim()}
              className="absolute right-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition shadow-xs cursor-pointer flex items-center space-x-1.5"
            >
              {isLoading ? (
                <>
                  <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Investigating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Investigate</span>
                </>
              )}
            </button>
          </form>

          {/* Quick Starter Pills */}
          <div className="flex flex-wrap items-center justify-center gap-1.5 pt-1">
            <span className="text-[11px] text-slate-500 font-medium">Suggested queries:</span>
            {sampleQuestions.map((q, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  setQuestion(q);
                  handleInvestigate(q);
                }}
                className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 text-[11px] text-slate-700 hover:text-blue-700 transition cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading State Skeleton */}
      {isLoading && (
        <div className="clean-card p-8 rounded-2xl space-y-4 animate-pulse">
          <div className="flex items-center space-x-2 text-blue-600 text-xs font-semibold">
            <Brain className="h-4 w-4 animate-spin" />
            <span>Formulating hypotheses and executing DuckDB analytical calculations...</span>
          </div>
          <div className="h-5 bg-slate-200 rounded w-1/3"></div>
          <div className="h-16 bg-slate-100 rounded"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="h-20 bg-slate-100 rounded"></div>
            <div className="h-20 bg-slate-100 rounded"></div>
          </div>
        </div>
      )}

      {/* Investigation Results */}
      {result && !isLoading && (
        <div className="space-y-6 animate-fade-in">
          {/* Executive Summary Card */}
          <div className="clean-card p-6 rounded-2xl border-blue-200 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-2">
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase bg-blue-50 text-blue-700 border border-blue-200">
                  Target: {result.target_metric}
                </span>
                <span className="text-xs text-slate-500 font-medium">Executive Summary</span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onNavigateToGraph(result?.question || question)}
                  className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 text-xs font-semibold text-slate-700 transition flex items-center space-x-1.5 cursor-pointer"
                >
                  <Layers className="h-3.5 w-3.5 text-blue-600" />
                  <span>Decision Graph</span>
                </button>
                <button
                  onClick={onNavigateToSimulator}
                  className="px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 border border-blue-200 text-xs font-semibold text-blue-700 transition flex items-center space-x-1.5 cursor-pointer"
                >
                  <TrendingUp className="h-3.5 w-3.5 text-blue-600" />
                  <span>Simulate Action</span>
                </button>
              </div>
            </div>

            <p className="text-sm text-slate-800 leading-relaxed font-normal">
              {result.executive_summary}
            </p>

            {/* Key findings bullets */}
            {result.key_findings.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Verified Data Findings:
                </span>
                <ul className="space-y-1.5 text-xs text-slate-700">
                  {result.key_findings.map((f, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Hypotheses Tested Scorecard */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <FileCheck className="h-4 w-4 text-blue-600" />
                <span>Hypotheses Tested Deterministically ({result.hypotheses_tested.length})</span>
              </h3>
              <span className="text-[11px] text-slate-500">Inspect exact SQL calculations below</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {result.hypotheses_tested.map((hyp) => {
                const isConfirmed = hyp.status === "confirmed";
                const isRefuted = hyp.status === "refuted";
                const evItem = result.evidence_package.find((e) => e.hypothesis_id === hyp.id);

                return (
                  <div
                    key={hyp.id}
                    className={`clean-card p-4 rounded-xl flex flex-col justify-between ${
                      isConfirmed
                        ? "border-emerald-200 bg-emerald-50/20"
                        : isRefuted
                        ? "border-slate-200 bg-slate-50/40"
                        : "border-slate-200"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                            isConfirmed
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : isRefuted
                              ? "bg-rose-50 text-rose-700 border-rose-200"
                              : "bg-slate-100 text-slate-600 border-slate-200"
                          }`}
                        >
                          {isConfirmed ? (
                            <CheckCircle2 className="h-3 w-3" />
                          ) : isRefuted ? (
                            <XCircle className="h-3 w-3" />
                          ) : (
                            <HelpCircle className="h-3 w-3" />
                          )}
                          <span>{hyp.status}</span>
                        </span>

                        <span className="text-[11px] font-semibold text-slate-500">
                          {hyp.confidence_score}% Confidence
                        </span>
                      </div>

                      <h4 className="text-xs font-bold text-slate-900 mb-1">{hyp.statement}</h4>
                      {hyp.explanation && (
                        <p className="text-[11px] text-slate-600 leading-relaxed mb-3">
                          {hyp.explanation}
                        </p>
                      )}
                    </div>

                    {evItem && (
                      <button
                        onClick={() => onOpenEvidence(evItem)}
                        className="mt-2 flex items-center justify-between px-3 py-1.5 rounded-lg bg-white hover:bg-blue-50 border border-slate-200 hover:border-blue-200 text-[11px] font-semibold text-blue-700 transition cursor-pointer shadow-2xs"
                      >
                        <span className="flex items-center space-x-1.5">
                          <ShieldCheck className="h-3.5 w-3.5 text-blue-600" />
                          <span>View Evidence Proof & SQL</span>
                        </span>
                        <ArrowRight className="h-3 w-3 text-blue-600" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="clean-card p-6 rounded-2xl border-slate-200 space-y-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <Sparkles className="h-4 w-4 text-blue-600" />
                <span>Recommended Business Interventions</span>
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {result.recommendations.map((rec) => (
                  <div
                    key={rec.id}
                    className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-slate-900">{rec.title}</span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                            rec.priority === "high"
                              ? "bg-rose-50 text-rose-700 border border-rose-200"
                              : "bg-blue-50 text-blue-700 border border-blue-200"
                          }`}
                        >
                          {rec.priority} priority
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed mb-3">{rec.description}</p>
                    </div>

                    <div className="pt-2 border-t border-slate-200 flex items-center justify-between text-[11px]">
                      <span className="text-slate-500 font-medium">Projected Impact:</span>
                      <span className="font-bold text-emerald-700">{rec.projected_impact}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
