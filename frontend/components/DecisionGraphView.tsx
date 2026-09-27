"use client";

import React, { useEffect, useState } from "react";
import {
  Network,
  Search,
  CheckCircle2,
  FileText,
  Sliders,
  Sparkles,
  ArrowDown,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { DecisionGraphResponse, buildDecisionGraph } from "@/lib/api";

interface DecisionGraphViewProps {
  datasetId: string;
  defaultQuestion?: string;
  onSelectSimulation: () => void;
}

export const DecisionGraphView: React.FC<DecisionGraphViewProps> = ({
  datasetId,
  defaultQuestion = "What drove the primary variance in performance?",
  onSelectSimulation,
}) => {
  const [question, setQuestion] = useState(defaultQuestion);
  const [graphData, setGraphData] = useState<DecisionGraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  const loadGraph = async (qText?: string) => {
    const q = (qText !== undefined ? qText : question).trim();
    if (!datasetId || !q) return;
    setIsLoading(true);
    try {
      const data = await buildDecisionGraph(datasetId, q);
      setGraphData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (defaultQuestion) {
      setQuestion(defaultQuestion);
      loadGraph(defaultQuestion);
    } else {
      loadGraph();
    }
  }, [datasetId, defaultQuestion]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Network className="h-5 w-5 text-blue-600" />
            <span>Decision Graph</span>
          </h2>
          <p className="text-xs text-slate-500">
            Visual reasoning chain from business question to proven data points and recommendations.
          </p>
        </div>

        <button
          onClick={() => loadGraph()}
          disabled={isLoading}
          className="px-3.5 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 border border-blue-200 text-xs font-semibold text-blue-700 transition flex items-center space-x-1.5 cursor-pointer self-start"
        >
          <Sparkles className="h-3.5 w-3.5 text-blue-600" />
          <span>Regenerate Graph</span>
        </button>
      </div>

      {/* Interactive Question Search Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          loadGraph();
        }}
        className="relative flex items-center"
      >
        <div className="absolute left-4 text-slate-400">
          <Search className="h-4 w-4 text-slate-400" />
        </div>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask any question to build a custom decision graph..."
          disabled={isLoading}
          className="w-full bg-white border border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 rounded-xl py-2.5 pl-11 pr-32 text-xs sm:text-sm text-slate-900 placeholder-slate-400 focus:outline-none transition shadow-xs"
        />
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="absolute right-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition cursor-pointer flex items-center space-x-1.5"
        >
          {isLoading ? (
            <>
              <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Building...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-3.5 w-3.5" />
              <span>Build Graph</span>
            </>
          )}
        </button>
      </form>

      {isLoading && (
        <div className="clean-card p-12 rounded-2xl text-center animate-pulse">
          <Layers className="h-7 w-7 text-blue-600 mx-auto mb-2 animate-spin" />
          <span className="text-xs font-semibold text-slate-600">Building reasoning graph nodes...</span>
        </div>
      )}

      {graphData && !isLoading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Visual Node Map */}
          <div className="lg:col-span-2 clean-card p-6 rounded-2xl space-y-5 relative overflow-hidden bg-slate-50/40">
            {/* 1. Root Question Node */}
            <div className="flex justify-center relative z-10">
              {graphData.nodes
                .filter((n) => n.type === "question")
                .map((node) => (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className="p-4 rounded-xl bg-blue-600 border border-blue-700 shadow-md cursor-pointer hover:bg-blue-700 transition max-w-md text-center text-white"
                  >
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-blue-500/30 text-blue-100 border border-blue-400/40">
                      {node.data.badge}
                    </span>
                    <h3 className="text-sm font-bold text-white mt-1.5">&ldquo;{node.data.label}&rdquo;</h3>
                  </div>
                ))}
            </div>

            <div className="flex justify-center my-0.5">
              <ArrowDown className="h-4 w-4 text-slate-400" />
            </div>

            {/* 2. Hypotheses Layer */}
            <div className="space-y-2 relative z-10">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider text-center">
                Hypotheses Formulated
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {graphData.nodes
                  .filter((n) => n.type === "hypothesis")
                  .map((node) => {
                    const isConfirmed = node.data.status === "confirmed";
                    return (
                      <div
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        className={`p-3.5 rounded-xl border transition cursor-pointer clean-card-hover ${
                          isConfirmed
                            ? "bg-emerald-50/60 border-emerald-200"
                            : "bg-white border-slate-200"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <span
                            className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                              isConfirmed
                                ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                                : "bg-slate-100 text-slate-600 border border-slate-200"
                            }`}
                          >
                            {node.data.status}
                          </span>
                          <span className="text-[10px] text-slate-500 font-medium">{node.data.confidence}% Conf</span>
                        </div>
                        <p className="text-xs font-semibold text-slate-800">{node.data.label}</p>
                      </div>
                    );
                  })}
              </div>
            </div>

            <div className="flex justify-center my-0.5">
              <ArrowDown className="h-4 w-4 text-slate-400" />
            </div>

            {/* 3. Evidence Layer */}
            <div className="space-y-2 relative z-10">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider text-center">
                Verified DuckDB Evidence Proofs
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {graphData.nodes
                  .filter((n) => n.type === "evidence")
                  .map((node) => (
                    <div
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className="p-3.5 rounded-xl bg-white border border-blue-200 hover:border-blue-400 transition cursor-pointer clean-card-hover"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded uppercase bg-blue-50 text-blue-700 border border-blue-100 flex items-center space-x-1">
                          <ShieldCheck className="h-3 w-3" />
                          <span>Calculated Proof</span>
                        </span>
                        <span className="text-[10px] font-bold text-emerald-700 font-mono">
                          {String(node.data.proof_value)}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-slate-800">{node.data.summary}</p>
                    </div>
                  ))}
              </div>
            </div>

            <div className="flex justify-center my-0.5">
              <ArrowDown className="h-4 w-4 text-slate-400" />
            </div>

            {/* 4. Action Recommendation Nodes */}
            <div className="space-y-2 relative z-10">
              <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider text-center">
                Action Recommendations
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {graphData.nodes
                  .filter((n) => n.type === "action")
                  .map((node) => (
                    <div
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className="p-3.5 rounded-xl bg-white border border-slate-200 hover:border-blue-300 transition cursor-pointer clean-card-hover"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded uppercase bg-blue-50 text-blue-700 border border-blue-100">
                          {node.data.badge}
                        </span>
                        <span className="text-[10px] font-bold text-emerald-700">{node.data.impact}</span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-900 mb-1">{node.data.label}</h4>
                      <p className="text-[11px] text-slate-600">{node.data.description}</p>
                    </div>
                  ))}
              </div>
            </div>

            {/* 5. What-If Simulation Trigger */}
            <div className="flex justify-center pt-2 relative z-10">
              <button
                onClick={onSelectSimulation}
                className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition flex items-center space-x-2 cursor-pointer"
              >
                <Sliders className="h-4 w-4" />
                <span>Simulate Grounded Scenario with What-If Engine</span>
              </button>
            </div>
          </div>

          {/* Node Inspector Side Panel */}
          <div className="clean-card p-5 rounded-2xl space-y-4 self-start">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Node Details Inspector
            </h3>

            {selectedNode ? (
              <div className="space-y-3 animate-fade-in">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <span className="text-[10px] font-bold text-blue-700 uppercase">Type:</span>
                  <div className="text-xs font-bold text-slate-900 uppercase">{selectedNode.type}</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <span className="text-[10px] font-bold text-blue-700 uppercase">Label / Description:</span>
                  <p className="text-xs text-slate-800 font-medium">{selectedNode.data.label || selectedNode.data.description}</p>
                </div>

                {selectedNode.data.sql && (
                  <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                    <span className="text-[10px] font-bold text-blue-400 uppercase">Underlying DuckDB SQL:</span>
                    <pre className="text-[10px] font-mono text-blue-200 overflow-x-auto whitespace-pre-wrap">
                      {selectedNode.data.sql}
                    </pre>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400 text-xs">
                Click on any node in the decision tree to view details, SQL calculation, or impact metrics.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
