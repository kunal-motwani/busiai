"use client";

import React, { useEffect, useState } from "react";
import {
  Database,
  Calendar,
  Hash,
  Type,
  Key,
  Layers,
  Table,
} from "lucide-react";
import { DatasetInfo, DatasetProfile, getDatasetProfile } from "@/lib/api";

interface DatasetProfileViewProps {
  dataset: DatasetInfo;
}

export const DatasetProfileView: React.FC<DatasetProfileViewProps> = ({ dataset }) => {
  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const loadProfile = async () => {
      setIsLoading(true);
      try {
        const data = await getDatasetProfile(dataset.id);
        if (isMounted) setProfile(data);
      } catch (err) {
        console.error(err);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    loadProfile();
    return () => {
      isMounted = false;
    };
  }, [dataset.id]);

  if (isLoading) {
    return (
      <div className="clean-card p-10 rounded-2xl text-center animate-pulse">
        <Database className="h-7 w-7 text-blue-600 mx-auto mb-2 animate-spin" />
        <span className="text-xs font-semibold text-slate-600">Profiling dataset statistics with DuckDB...</span>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="space-y-6">
      {/* Overview Stats Header */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="clean-card p-4 rounded-xl">
          <span className="text-[10px] font-bold text-slate-500 uppercase">Total Rows</span>
          <div className="text-xl font-bold text-slate-900 mt-1 font-mono">{profile.total_rows.toLocaleString()}</div>
        </div>

        <div className="clean-card p-4 rounded-xl">
          <span className="text-[10px] font-bold text-slate-500 uppercase">Total Columns</span>
          <div className="text-xl font-bold text-slate-900 mt-1 font-mono">{profile.total_columns}</div>
        </div>

        <div className="clean-card p-4 rounded-xl border-emerald-200 bg-emerald-50/40">
          <span className="text-[10px] font-bold text-emerald-800 uppercase">Quality Score</span>
          <div className="text-xl font-bold text-emerald-700 mt-1 font-mono">{profile.quality_score}%</div>
        </div>

        <div className="clean-card p-4 rounded-xl">
          <span className="text-[10px] font-bold text-slate-500 uppercase">Primary Date</span>
          <div className="text-xs font-bold text-blue-700 mt-1.5 font-mono truncate">
            {profile.primary_date_column || "None detected"}
          </div>
        </div>
      </div>

      {/* Column Details Grid */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <Layers className="h-4 w-4 text-blue-600" />
          <span>Column Profiles & Types ({profile.columns.length})</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {profile.columns.map((col) => {
            let typeBadge = "bg-blue-50 text-blue-700 border-blue-200";
            let TypeIcon = Type;

            if (col.inferred_type === "numeric") {
              typeBadge = "bg-sky-50 text-sky-700 border-sky-200";
              TypeIcon = Hash;
            } else if (col.inferred_type === "datetime") {
              typeBadge = "bg-amber-50 text-amber-700 border-amber-200";
              TypeIcon = Calendar;
            } else if (col.inferred_type === "identifier") {
              typeBadge = "bg-purple-50 text-purple-700 border-purple-200";
              TypeIcon = Key;
            }

            return (
              <div
                key={col.name}
                className="clean-card p-4 rounded-xl flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-900 truncate max-w-[150px]">
                      {col.original_name}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border flex items-center space-x-1 ${typeBadge}`}>
                      <TypeIcon className="h-3 w-3" />
                      <span>{col.inferred_type}</span>
                    </span>
                  </div>

                  {/* Null Percentage */}
                  <div className="flex items-center justify-between text-[11px] text-slate-500 my-1">
                    <span>Nulls:</span>
                    <span className={`font-mono ${col.null_count > 0 ? "text-amber-600 font-bold" : "text-slate-600"}`}>
                      {col.null_count} ({col.null_percentage}%)
                    </span>
                  </div>

                  {/* Numeric Stats */}
                  {col.numeric_stats && (
                    <div className="mt-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] space-y-1 font-mono">
                      <div className="flex justify-between text-slate-500">
                        <span>Range:</span>
                        <span className="text-slate-800">
                          {col.numeric_stats.min?.toLocaleString()} &rarr; {col.numeric_stats.max?.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between text-slate-500">
                        <span>Mean / Median:</span>
                        <span className="text-slate-800">
                          {col.numeric_stats.mean?.toLocaleString()} / {col.numeric_stats.median?.toLocaleString()}
                        </span>
                      </div>
                      {col.numeric_stats.outlier_count > 0 && (
                        <div className="flex justify-between text-amber-700 font-bold">
                          <span>IQR Outliers:</span>
                          <span>{col.numeric_stats.outlier_count}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Categorical Stats */}
                  {col.categorical_stats && (
                    <div className="mt-2 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] space-y-1">
                      <div className="flex justify-between text-slate-500 font-mono">
                        <span>Distinct Values:</span>
                        <span className="text-slate-800">{col.categorical_stats.unique_count}</span>
                      </div>
                      {col.categorical_stats.top_values.length > 0 && (
                        <div className="text-[10px] text-slate-500 truncate pt-1">
                          Top: {col.categorical_stats.top_values.map((v) => `${v.value} (${v.count})`).join(", ")}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 10-Row Data Preview Table */}
      {dataset.preview_rows && dataset.preview_rows.length > 0 && (
        <div className="clean-card p-5 rounded-2xl space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-2">
              <Table className="h-4 w-4 text-blue-600" />
              <span>Dataset Preview (Top 10 Records)</span>
            </h3>
            <span className="text-[11px] text-slate-500 font-mono">Table: {dataset.table_name}</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  {Object.keys(dataset.preview_rows[0]).map((k) => (
                    <th key={k} className="py-2.5 px-3 text-slate-600 font-semibold uppercase text-[10px]">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {dataset.preview_rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 text-slate-800">
                    {Object.values(row).map((val: any, cIdx) => (
                      <td key={cIdx} className="py-2 px-3 whitespace-nowrap">
                        {typeof val === "number" ? val.toLocaleString() : String(val ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
