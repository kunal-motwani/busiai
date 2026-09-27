"use client";

import React, { useEffect, useState } from "react";
import {
  Sliders,
  TrendingUp,
  RotateCcw,
  Sparkles,
  ShieldAlert,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { SimulationResult, runSimulation } from "@/lib/api";

interface WhatIfSimulatorProps {
  datasetId: string;
  targetMetric?: string;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({
  datasetId,
  targetMetric = "mrr",
}) => {
  const [priceChange, setPriceChange] = useState<number>(10);
  const [churnReduction, setChurnReduction] = useState<number>(15);
  const [conversionBoost, setConversionBoost] = useState<number>(5);
  const [costReduction, setCostReduction] = useState<number>(0);

  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSimulate = async () => {
    if (!datasetId) return;
    setIsLoading(true);
    try {
      const data = await runSimulation({
        dataset_id: datasetId,
        target_metric: targetMetric,
        price_change_pct: priceChange,
        churn_reduction_pct: churnReduction,
        conversion_boost_pct: conversionBoost,
        cost_reduction_pct: costReduction,
      });
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleSimulate();
  }, [datasetId, priceChange, churnReduction, conversionBoost, costReduction]);

  const handleReset = () => {
    setPriceChange(0);
    setChurnReduction(0);
    setConversionBoost(0);
    setCostReduction(0);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Sliders className="h-5 w-5 text-blue-600" />
            <span>Grounded What-If Simulator</span>
          </h2>
          <p className="text-xs text-slate-500">
            Simulate the impact of pricing, retention, and acquisition changes with statistical confidence bounds.
          </p>
        </div>

        <button
          onClick={handleReset}
          className="px-3.5 py-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition flex items-center space-x-1.5 cursor-pointer self-start shadow-2xs"
        >
          <RotateCcw className="h-3.5 w-3.5 text-slate-500" />
          <span>Reset Levers</span>
        </button>
      </div>

      {/* Main Simulation Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Interactive Control Sliders */}
        <div className="clean-card p-6 rounded-2xl space-y-5 self-start">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
            <span>Scenario Levers</span>
            <span className="text-blue-600 font-semibold lowercase">Target: {targetMetric}</span>
          </h3>

          {/* Slider 1: Price Change */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-700 font-medium">Price Adjustment</span>
              <span className={`font-mono font-bold ${priceChange >= 0 ? "text-blue-600" : "text-rose-600"}`}>
                {priceChange > 0 ? `+${priceChange}%` : `${priceChange}%`}
              </span>
            </div>
            <input
              type="range"
              min="-30"
              max="50"
              step="5"
              value={priceChange}
              onChange={(e) => setPriceChange(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>-30%</span>
              <span>0%</span>
              <span>+50%</span>
            </div>
          </div>

          {/* Slider 2: Churn Reduction */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-700 font-medium">Churn Reduction</span>
              <span className="font-mono font-bold text-emerald-600">+{churnReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              step="5"
              value={churnReduction}
              onChange={(e) => setChurnReduction(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0%</span>
              <span>20%</span>
              <span>40%</span>
            </div>
          </div>

          {/* Slider 3: Conversion Boost */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-700 font-medium">Conversion Lift</span>
              <span className="font-mono font-bold text-blue-600">+{conversionBoost}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              step="2"
              value={conversionBoost}
              onChange={(e) => setConversionBoost(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span>0%</span>
              <span>15%</span>
              <span>30%</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 space-y-1">
            <div className="flex items-center space-x-1.5 text-slate-800 font-bold">
              <ShieldAlert className="h-3.5 w-3.5 text-amber-600" />
              <span>Model Assumptions:</span>
            </div>
            <p>Calculates demand price elasticity curve (-0.3) and compounding retention lifetime value.</p>
          </div>
        </div>

        {/* Right: Projections Chart & Scenario Cards */}
        <div className="lg:col-span-2 space-y-6">
          {result && (
            <>
              {/* High-level KPI Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <div className="clean-card p-4 rounded-xl">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Baseline Value</span>
                  <div className="text-lg font-bold text-slate-900 mt-1 font-mono">
                    ${result.baseline_value.toLocaleString()}
                  </div>
                </div>

                <div className="clean-card p-4 rounded-xl border-blue-200 bg-blue-50/40">
                  <span className="text-[10px] font-bold text-blue-700 uppercase">Projected Output</span>
                  <div className="text-lg font-bold text-blue-700 mt-1 font-mono">
                    ${result.projected_value.toLocaleString()}
                  </div>
                </div>

                <div className="clean-card p-4 rounded-xl border-emerald-200 bg-emerald-50/40">
                  <span className="text-[10px] font-bold text-emerald-800 uppercase">Net Variance</span>
                  <div className="text-lg font-bold text-emerald-700 mt-1 font-mono">
                    {result.net_delta >= 0 ? `+$${result.net_delta.toLocaleString()}` : `-$${Math.abs(result.net_delta).toLocaleString()}`}
                    <span className="text-xs font-semibold ml-1.5">({result.net_delta_pct > 0 ? `+${result.net_delta_pct}%` : `${result.net_delta_pct}%`})</span>
                  </div>
                </div>
              </div>

              {/* 6-Month Projection Area Chart */}
              <div className="clean-card p-5 rounded-2xl space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    <span>6-Month Forward Projection Curve</span>
                  </h3>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    {result.confidence_score}% Statistical Confidence
                  </span>
                </div>

                <ResponsiveContainer width="100%" height={240}>
                    <AreaChart data={result.timeline_curve} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
                      <defs>
                        <linearGradient id="wif-colorOptimistic" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="wif-colorBase" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                          <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                      <YAxis stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `$${(v as number).toLocaleString()}`} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#ffffff",
                          borderColor: "#e2e8f0",
                          borderRadius: "0.5rem",
                          color: "#0f172a",
                          fontSize: "12px",
                          boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "8px" }} />
                      <Area
                        type="monotone"
                        dataKey="baseline"
                        stroke="#94a3b8"
                        strokeDasharray="4 4"
                        fill="none"
                        name="Baseline (Status Quo)"
                      />
                      <Area
                        type="monotone"
                        dataKey="projected_base"
                        stroke="#2563eb"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#wif-colorBase)"
                        name="Expected Base Case"
                      />
                      <Area
                        type="monotone"
                        dataKey="projected_optimistic"
                        stroke="#10b981"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#wif-colorOptimistic)"
                        name="Optimistic Upside"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
              </div>

              {/* Three Scenarios Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                {result.scenarios.map((sc, i) => (
                  <div
                    key={i}
                    className="clean-card p-4 rounded-xl space-y-1.5"
                  >
                    <span className="text-[10px] font-bold uppercase text-blue-700">
                      {sc.name.replace("_", " ")}
                    </span>
                    <div className="text-base font-bold text-slate-900 font-mono">
                      ${sc.projected_value.toLocaleString()}
                    </div>
                    <div className="text-xs font-bold text-emerald-700 font-mono">
                      {sc.delta_value >= 0 ? `+$${sc.delta_value.toLocaleString()}` : `-$${Math.abs(sc.delta_value).toLocaleString()}`} ({sc.delta_percentage > 0 ? `+${sc.delta_percentage}%` : `${sc.delta_percentage}%`})
                    </div>
                    <p className="text-[11px] text-slate-500 leading-snug pt-1">{sc.description}</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
