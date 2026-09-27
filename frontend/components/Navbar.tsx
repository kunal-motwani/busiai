"use client";

import React from "react";
import {
  Brain,
  Database,
  Sparkles,
  Search,
  Network,
  Sliders,
  Terminal,
  Upload,
  ChevronDown,
} from "lucide-react";
import { DatasetInfo } from "@/lib/api";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  datasets: DatasetInfo[];
  selectedDataset: DatasetInfo | null;
  setSelectedDataset: (d: DatasetInfo) => void;
  onOpenUploadModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  datasets,
  selectedDataset,
  setSelectedDataset,
  onOpenUploadModal,
}) => {
  const tabs = [
    { id: "overview", label: "Auto Insights", icon: Sparkles },
    { id: "investigate", label: "AI Investigation", icon: Search },
    { id: "graph", label: "Decision Graph", icon: Network },
    { id: "simulator", label: "What-If Simulator", icon: Sliders },
    { id: "profile", label: "Data Profile", icon: Database },
    { id: "workbench", label: "SQL Workbench", icon: Terminal },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center shadow-xs">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-slate-900">
                  Busi<span className="text-blue-600">AI</span>
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-100">
                  Decision Engine
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">From data to decisions. With proof.</p>
            </div>
          </div>

          {/* Dataset Selector & Upload */}
          <div className="flex items-center space-x-3">
            {datasets.length > 0 && (
              <div className="relative">
                <select
                  value={selectedDataset?.id || ""}
                  onChange={(e) => {
                    const found = datasets.find((d) => d.id === e.target.value);
                    if (found) setSelectedDataset(found);
                  }}
                  className="appearance-none bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 text-xs font-medium rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 cursor-pointer transition"
                >
                  {datasets.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.row_count} rows)
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-slate-500 pointer-events-none" />
              </div>
            )}

            <button
              id="upload-data-btn"
              onClick={onOpenUploadModal}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Upload className="h-3.5 w-3.5" />
              <span>Upload Dataset</span>
            </button>
          </div>
        </div>

        {/* Minimalist Navigation Tabs */}
        <div className="flex space-x-1 overflow-x-auto py-1.5 border-t border-slate-100 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all cursor-pointer ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
