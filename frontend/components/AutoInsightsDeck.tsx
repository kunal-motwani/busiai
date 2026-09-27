"use client";

import React from "react";
import {
  TrendingDown,
  TrendingUp,
  PieChart,
  GitBranch,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Zap,
} from "lucide-react";
import { BusinessInsight } from "@/lib/api";

interface AutoInsightsDeckProps {
  insights: BusinessInsight[];
  onInvestigateInsight: (question: string) => void;
  isLoading: boolean;
}

export const AutoInsightsDeck: React.FC<AutoInsightsDeckProps> = ({
  insights,
  onInvestigateInsight,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="clean-card p-5 rounded-xl animate-pulse">
            <div className="h-4 bg-slate-200 rounded w-1/3 mb-3"></div>
            <div className="h-5 bg-slate-300 rounded w-3/4 mb-2"></div>
            <div className="h-12 bg-slate-100 rounded mb-4"></div>
            <div className="h-8 bg-slate-200 rounded w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (insights.length === 0) {
    return (
      <div className="clean-card p-10 rounded-xl text-center border-dashed border-slate-300">
        <Sparkles className="h-8 w-8 text-blue-600 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-slate-900">No Key Anomalies Detected</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          The dataset metrics are currently within expected baseline limits. You can explore targeted questions in the AI Investigation tab.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <span>Automated Business Insights</span>
          </h2>
          <p className="text-xs text-slate-500">
            Discovered key changes, concentration risks, and metric correlations.
          </p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
          {insights.length} Detected
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {insights.map((insight) => {
          let Icon = Zap;
          let badgeColor = "bg-blue-50 text-blue-700 border-blue-200";

          if (insight.type === "trend_shift") {
            Icon = TrendingDown;
            badgeColor = "bg-rose-50 text-rose-700 border-rose-200";
          } else if (insight.type === "growth") {
            Icon = TrendingUp;
            badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
          } else if (insight.type === "concentration") {
            Icon = PieChart;
            badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
          } else if (insight.type === "correlation") {
            Icon = GitBranch;
            badgeColor = "bg-sky-50 text-sky-700 border-sky-200";
          } else if (insight.type === "anomaly") {
            Icon = AlertTriangle;
            badgeColor = "bg-purple-50 text-purple-700 border-purple-200";
          }

          return (
            <div
              key={insight.id}
              className="clean-card clean-card-hover p-5 rounded-xl flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div className={`p-1.5 rounded-md border ${badgeColor}`}>
                      <Icon className="h-3.5 w-3.5" />
                    </div>
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-600">
                      {insight.type.replace("_", " ")}
                    </span>
                  </div>

                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded uppercase ${
                      insight.importance === "high"
                        ? "bg-rose-50 text-rose-700 border border-rose-200 font-bold"
                        : "bg-slate-100 text-slate-600 border border-slate-200"
                    }`}
                  >
                    {insight.importance} priority
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-slate-900 mb-1.5 leading-snug">{insight.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4">{insight.description}</p>
              </div>

              {insight.suggested_question && (
                <button
                  onClick={() => onInvestigateInsight(insight.suggested_question!)}
                  className="w-full mt-2 flex items-center justify-between px-3 py-2 rounded-lg bg-slate-50 hover:bg-blue-50 border border-slate-200 hover:border-blue-200 text-xs font-semibold text-blue-700 transition group cursor-pointer"
                >
                  <span className="truncate pr-2">Investigate: &ldquo;{insight.suggested_question}&rdquo;</span>
                  <ArrowRight className="h-3.5 w-3.5 shrink-0 text-blue-600 group-hover:translate-x-0.5 transition" />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
