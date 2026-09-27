"use client";

import React, { useState } from "react";
import { Upload, FileSpreadsheet, Sparkles, AlertCircle, X, ArrowRight } from "lucide-react";
import { uploadDataset, uploadSampleCsv, DatasetInfo } from "@/lib/api";

interface DatasetUploaderProps {
  isOpen: boolean;
  onClose: () => void;
  onDatasetUploaded: (dataset: DatasetInfo) => void;
}

const SAMPLE_SAAS = `date,mrr,arr,churn_rate,new_customers,churned_customers,cac,ltv,region,plan_tier
2025-01-01,120000,1440000,2.1,45,8,420,5200,North America,Enterprise
2025-01-01,65000,780000,3.4,80,22,210,2400,EMEA,Pro
2025-01-01,35000,420000,4.2,60,18,150,1600,APAC,Starter
2025-02-01,128000,1536000,1.9,48,7,410,5400,North America,Enterprise
2025-02-01,69000,828000,3.1,84,20,205,2500,EMEA,Pro
2025-02-01,37000,444000,3.9,64,16,145,1650,APAC,Starter
2025-03-01,135000,1620000,1.8,52,6,395,5600,North America,Enterprise
2025-03-01,73000,876000,2.9,90,19,200,2600,EMEA,Pro
2025-03-01,39000,468000,3.8,68,15,140,1700,APAC,Starter
2025-04-01,142000,1704000,2.0,50,7,405,5500,North America,Enterprise
2025-04-01,77000,924000,3.0,92,20,198,2650,EMEA,Pro
2025-04-01,41000,492000,3.7,70,15,138,1750,APAC,Starter
2025-05-01,151000,1812000,1.7,55,5,390,5800,North America,Enterprise
2025-05-01,82000,984000,2.8,96,18,195,2700,EMEA,Pro
2025-05-01,44000,528000,3.5,75,14,135,1800,APAC,Starter
2025-06-01,160000,1920000,1.6,58,5,385,5950,North America,Enterprise
2025-06-01,86000,1032000,2.7,100,17,190,2750,EMEA,Pro
2025-06-01,46000,552000,3.4,78,13,132,1850,APAC,Starter
2025-07-01,169000,2028000,1.5,60,4,380,6100,North America,Enterprise
2025-07-01,91000,1092000,2.6,105,16,188,2800,EMEA,Pro
2025-07-01,48000,576000,3.3,80,12,130,1900,APAC,Starter
2025-08-01,122000,1464000,5.8,25,32,620,4100,North America,Enterprise
2025-08-01,72000,864000,4.9,55,36,310,2100,EMEA,Pro
2025-08-01,36000,432000,5.2,40,25,210,1400,APAC,Starter
2025-09-01,138000,1656000,3.2,42,14,480,4800,North America,Enterprise
2025-09-01,80000,960000,3.5,78,21,240,2500,EMEA,Pro
2025-09-01,42000,504000,3.9,65,16,160,1680,APAC,Starter
2025-10-01,152000,1824000,2.2,52,8,410,5400,North America,Enterprise
2025-10-01,88000,1056000,2.9,92,19,205,2680,EMEA,Pro
2025-10-01,45000,540000,3.5,72,14,142,1760,APAC,Starter`;

const SAMPLE_ECOMMERCE = `order_id,order_date,customer_segment,product_category,sub_category,region,sales_amount,cost_amount,profit,discount_rate,quantity
ORD-1001,2025-01-05,Consumer,Electronics,Smartphones,North,1200.0,750.0,450.0,0.05,2
ORD-1002,2025-01-07,Corporate,Furniture,Chairs,South,450.0,280.0,170.0,0.10,3
ORD-1003,2025-01-12,Small Business,Office Supplies,Binders,East,85.0,35.0,50.0,0.00,5
ORD-1004,2025-01-18,Consumer,Electronics,Laptops,West,2400.0,1600.0,800.0,0.05,2
ORD-1005,2025-02-03,Consumer,Furniture,Tables,North,890.0,620.0,270.0,0.15,1
ORD-1006,2025-02-14,Corporate,Electronics,Accessories,East,150.0,60.0,90.0,0.00,4
ORD-1007,2025-02-22,Consumer,Office Supplies,Paper,South,65.0,25.0,40.0,0.00,10
ORD-1008,2025-03-01,Small Business,Electronics,Smartphones,West,1800.0,1150.0,650.0,0.08,3
ORD-1009,2025-03-10,Consumer,Furniture,Chairs,North,620.0,380.0,240.0,0.10,4
ORD-1010,2025-03-25,Corporate,Electronics,Laptops,South,3600.0,2400.0,1200.0,0.05,3
ORD-1011,2025-04-04,Consumer,Office Supplies,Storage,East,320.0,180.0,140.0,0.00,2
ORD-1012,2025-04-18,Small Business,Furniture,Bookcases,West,1100.0,790.0,310.0,0.12,2
ORD-1013,2025-05-02,Consumer,Electronics,Smartphones,North,2400.0,1500.0,900.0,0.05,4
ORD-1014,2025-05-19,Corporate,Office Supplies,Appliances,South,780.0,460.0,320.0,0.00,2
ORD-1015,2025-06-08,Consumer,Furniture,Tables,East,950.0,660.0,290.0,0.10,1
ORD-1016,2025-06-21,Small Business,Electronics,Laptops,West,4800.0,3200.0,1600.0,0.05,4
ORD-1017,2025-07-04,Consumer,Electronics,Accessories,North,280.0,110.0,170.0,0.00,6
ORD-1018,2025-07-29,Corporate,Furniture,Chairs,East,1250.0,780.0,470.0,0.08,8
ORD-1019,2025-08-11,Consumer,Office Supplies,Binders,South,95.0,40.0,55.0,0.00,6
ORD-1020,2025-08-25,Small Business,Electronics,Smartphones,West,1200.0,750.0,450.0,0.05,2
ORD-1021,2025-09-03,Consumer,Furniture,Bookcases,North,1400.0,980.0,420.0,0.10,2
ORD-1022,2025-09-17,Corporate,Electronics,Laptops,East,6000.0,4000.0,2000.0,0.05,5
ORD-1023,2025-10-05,Consumer,Office Supplies,Paper,West,120.0,45.0,75.0,0.00,12
ORD-1024,2025-10-22,Small Business,Furniture,Chairs,South,750.0,460.0,290.0,0.05,5`;

export const DatasetUploader: React.FC<DatasetUploaderProps> = ({ isOpen, onClose, onDatasetUploaded }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    try {
      const dataset = await uploadDataset(file);
      onDatasetUploaded(dataset);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to upload file");
    } finally {
      setIsUploading(false);
    }
  };

  const handleLoadSample = async (type: "saas" | "ecommerce") => {
    setIsUploading(true);
    setError(null);
    try {
      let dataset: DatasetInfo;
      if (type === "saas") {
        dataset = await uploadSampleCsv("saas_monthly_metrics.csv", SAMPLE_SAAS, "SaaS Growth & Churn Metrics");
      } else {
        dataset = await uploadSampleCsv("ecommerce_orders.csv", SAMPLE_ECOMMERCE, "E-Commerce Global Sales");
      }
      onDatasetUploaded(dataset);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to load sample dataset");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fade-in">
      <div className="relative w-full max-w-xl bg-white rounded-2xl p-6 shadow-2xl border border-slate-200">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center h-12 w-12 rounded-xl bg-blue-50 border border-blue-100 text-blue-600 mb-2">
            <Upload className="h-6 w-6" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Ingest Business Data</h2>
          <p className="text-xs text-slate-500 mt-0.5">Upload CSV or Excel files for deterministic AI investigation.</p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-center space-x-2 text-rose-700 text-xs">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Dropzone */}
        <label className="relative flex flex-col items-center justify-center p-8 border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl bg-slate-50 hover:bg-blue-50/40 transition cursor-pointer group">
          <FileSpreadsheet className="h-9 w-9 text-slate-400 group-hover:text-blue-600 transition mb-2" />
          <span className="text-xs font-semibold text-slate-800">
            {isUploading ? "Ingesting & Profiling Dataset..." : "Click or drag CSV / Excel file here"}
          </span>
          <span className="text-[11px] text-slate-500 mt-1">Supports .csv, .xlsx, .xls, .parquet up to 50MB</span>
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.parquet"
            onChange={handleFileUpload}
            disabled={isUploading}
            className="hidden"
          />
        </label>

        {/* 1-Click Sample Loaders */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-600 flex items-center space-x-1.5">
              <Sparkles className="h-3.5 w-3.5 text-blue-600" />
              <span>Or test with pre-built business datasets:</span>
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <button
              onClick={() => handleLoadSample("saas")}
              disabled={isUploading}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 text-left transition group cursor-pointer"
            >
              <div>
                <div className="text-xs font-bold text-slate-900 group-hover:text-blue-700">SaaS Metrics Demo</div>
                <div className="text-[10px] text-slate-500 mt-0.5">MRR, ARR, Churn rate, CAC, LTV</div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
            </button>

            <button
              onClick={() => handleLoadSample("ecommerce")}
              disabled={isUploading}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 text-left transition group cursor-pointer"
            >
              <div>
                <div className="text-xs font-bold text-slate-900 group-hover:text-blue-700">E-Commerce Orders</div>
                <div className="text-[10px] text-slate-500 mt-0.5">Sales, Profit, Discounts, Categories</div>
              </div>
              <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
