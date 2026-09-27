"""Automated Business Insights Engine using DuckDB deterministic queries."""
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from app.core.database import db_manager
from app.ingestion.models import DatasetInfo
from app.profiling.models import DatasetProfile


class BusinessInsight(BaseModel):
    id: str
    type: str  # "trend_shift", "concentration", "anomaly", "correlation", "growth"
    importance: str  # "high", "medium", "low"
    title: str
    description: str
    metric: Optional[str] = None
    dimension: Optional[str] = None
    evidence_summary: dict[str, Any] = Field(default_factory=dict)
    suggested_question: Optional[str] = None


class InsightsService:
    """Generates automated business insights from uploaded datasets via DuckDB."""

    def generate_insights(
        self, dataset: DatasetInfo, profile: DatasetProfile
    ) -> List[BusinessInsight]:
        """Generate key automated business insights."""
        insights: List[BusinessInsight] = []
        table = dataset.table_name

        metrics = profile.key_metrics
        dimensions = profile.key_dimensions
        date_col = profile.primary_date_column

        # 1. Temporal Analysis & Trend Shifts
        if date_col and metrics:
            temporal_insights = self._analyze_time_series(table, date_col, metrics[:2])
            insights.extend(temporal_insights)

        # 2. Segment & Dimension Concentration (Pareto / Top Share)
        if metrics and dimensions:
            concentration_insights = self._analyze_concentration(
                table, metrics[0], dimensions[:3]
            )
            insights.extend(concentration_insights)

        # 3. Metric Correlations
        if len(metrics) >= 2:
            corr_insights = self._analyze_correlations(table, metrics)
            insights.extend(corr_insights)

        # 4. Outlier / Anomaly Detection
        if metrics:
            anomaly_insights = self._analyze_metric_outliers(profile)
            insights.extend(anomaly_insights)

        return insights

    def _analyze_time_series(
        self, table: str, date_col: str, metrics: List[str]
    ) -> List[BusinessInsight]:
        """Detect period-over-period spikes, drops, or growth trends via DuckDB."""
        insights: List[BusinessInsight] = []

        for metric in metrics:
            query = f"""
                WITH monthly_agg AS (
                    SELECT 
                        strftime("{date_col}"::DATE, '%Y-%m') AS period,
                        SUM("{metric}") AS total_metric
                    FROM "{table}"
                    WHERE "{date_col}" IS NOT NULL AND "{metric}" IS NOT NULL
                    GROUP BY period
                    ORDER BY period ASC
                ),
                period_changes AS (
                    SELECT 
                        period,
                        total_metric,
                        LAG(total_metric) OVER (ORDER BY period) AS prev_metric,
                        ROUND(((total_metric - LAG(total_metric) OVER (ORDER BY period)) / NULLIF(LAG(total_metric) OVER (ORDER BY period), 0)) * 100.0, 1) AS pct_change
                    FROM monthly_agg
                )
                SELECT period, total_metric, prev_metric, pct_change
                FROM period_changes
                WHERE pct_change IS NOT NULL
                ORDER BY pct_change ASC
            """
            try:
                rows = db_manager.execute_query(query)
                if not rows:
                    continue

                # Largest drop
                min_row = rows[0]
                if min_row["pct_change"] is not None and min_row["pct_change"] <= -10.0:
                    pct_drop = abs(float(min_row["pct_change"]))
                    period_name = str(min_row["period"])
                    insights.append(
                        BusinessInsight(
                            id=f"trend_drop_{metric}_{period_name}",
                            type="trend_shift",
                            importance="high" if pct_drop >= 20.0 else "medium",
                            title=f"Significant drop in {metric} ({period_name})",
                            description=f"{metric} dropped by {pct_drop}% in {period_name} compared to the previous period.",
                            metric=metric,
                            evidence_summary={
                                "period": period_name,
                                "percentage_change": -pct_drop,
                                "current_value": float(min_row["total_metric"]),
                                "previous_value": float(min_row["prev_metric"]),
                            },
                            suggested_question=f"Why did {metric} drop in {period_name}?",
                        )
                    )

                # Largest surge
                max_row = rows[-1]
                if max_row["pct_change"] is not None and max_row["pct_change"] >= 20.0:
                    pct_surge = float(max_row["pct_change"])
                    period_name = str(max_row["period"])
                    insights.append(
                        BusinessInsight(
                            id=f"trend_surge_{metric}_{period_name}",
                            type="growth",
                            importance="high" if pct_surge >= 40.0 else "medium",
                            title=f"Surge in {metric} ({period_name})",
                            description=f"{metric} grew by {pct_surge}% in {period_name}.",
                            metric=metric,
                            evidence_summary={
                                "period": period_name,
                                "percentage_change": pct_surge,
                                "current_value": float(max_row["total_metric"]),
                                "previous_value": float(max_row["prev_metric"]),
                            },
                            suggested_question=f"What drove the {pct_surge}% increase in {metric} during {period_name}?",
                        )
                    )
            except Exception:
                continue

        return insights

    def _analyze_concentration(
        self, table: str, metric: str, dimensions: List[str]
    ) -> List[BusinessInsight]:
        """Detect dimension dominance/concentration using DuckDB."""
        insights: List[BusinessInsight] = []
        try:
            total_sum = float(db_manager.execute_scalar(f'SELECT SUM("{metric}") FROM "{table}"') or 0.0)
            if total_sum <= 0:
                return insights

            for dim in dimensions:
                q = f"""
                    SELECT 
                        "{dim}"::VARCHAR AS dim_val,
                        SUM("{metric}") AS sum_val,
                        ROUND((SUM("{metric}") / {total_sum}) * 100.0, 1) AS share_pct,
                        COUNT(*) AS row_cnt
                    FROM "{table}"
                    WHERE "{dim}" IS NOT NULL AND "{metric}" IS NOT NULL
                    GROUP BY "{dim}"
                    ORDER BY sum_val DESC
                    LIMIT 5
                """
                rows = db_manager.execute_query(q)
                if not rows:
                    continue

                top_row = rows[0]
                top_share = float(top_row["share_pct"] or 0.0)
                top_dim_val = str(top_row["dim_val"])

                if top_share >= 40.0:
                    insights.append(
                        BusinessInsight(
                            id=f"concentration_{metric}_{dim}",
                            type="concentration",
                            importance="high" if top_share >= 60.0 else "medium",
                            title=f"High {dim} concentration in {metric}",
                            description=f"'{top_dim_val}' accounts for {top_share}% of total {metric} in the dataset.",
                            metric=metric,
                            dimension=dim,
                            evidence_summary={
                                "top_segment": top_dim_val,
                                "share_percentage": top_share,
                                "top_value": float(top_row["sum_val"]),
                                "total_dataset_value": total_sum,
                            },
                            suggested_question=f"How much does {top_dim_val} influence overall {metric} performance?",
                        )
                    )
        except Exception:
            pass

        return insights

    def _analyze_correlations(
        self, table: str, metrics: List[str]
    ) -> List[BusinessInsight]:
        """Detect strong correlations between metrics using DuckDB's CORR()."""
        insights: List[BusinessInsight] = []
        checked = set()

        for col_a in metrics:
            for col_b in metrics:
                if col_a != col_b and (col_b, col_a) not in checked:
                    checked.add((col_a, col_b))
                    try:
                        corr_q = f"""
                            SELECT CORR("{col_a}", "{col_b}") AS corr_val
                            FROM "{table}"
                            WHERE "{col_a}" IS NOT NULL AND "{col_b}" IS NOT NULL
                        """
                        val = db_manager.execute_scalar(corr_q)
                        if val is not None and abs(float(val)) >= 0.70:
                            corr_float = float(val)
                            direction = "positive" if corr_float > 0 else "negative"
                            insights.append(
                                BusinessInsight(
                                    id=f"corr_{col_a}_{col_b}",
                                    type="correlation",
                                    importance="medium",
                                    title=f"Strong {direction} correlation: {col_a} & {col_b}",
                                    description=f"A strong {direction} relationship (r = {corr_float:.2f}) was detected between {col_a} and {col_b}.",
                                    metric=col_a,
                                    evidence_summary={
                                        "metric_a": col_a,
                                        "metric_b": col_b,
                                        "correlation_coefficient": round(corr_float, 2),
                                    },
                                    suggested_question=f"How does changes in {col_a} impact {col_b}?",
                                )
                            )
                    except Exception:
                        continue

        return insights

    def _analyze_metric_outliers(
        self, profile: DatasetProfile
    ) -> List[BusinessInsight]:
        """Detect columns with notable outliers from statistical profiling."""
        insights: List[BusinessInsight] = []
        for col in profile.columns:
            if col.numeric_stats and col.numeric_stats.outlier_count > 0:
                outlier_cnt = col.numeric_stats.outlier_count
                outlier_pct = (outlier_cnt / profile.total_rows) * 100.0 if profile.total_rows > 0 else 0.0
                if outlier_pct >= 2.0:
                    insights.append(
                        BusinessInsight(
                            id=f"outlier_{col.name}",
                            type="anomaly",
                            importance="medium",
                            title=f"Statistical outliers detected in {col.name}",
                            description=f"{outlier_cnt} data points ({outlier_pct:.1f}%) in {col.name} fall outside 1.5x IQR boundaries.",
                            metric=col.name,
                            evidence_summary={
                                "outlier_count": outlier_cnt,
                                "outlier_percentage": round(outlier_pct, 1),
                                "min": col.numeric_stats.min,
                                "max": col.numeric_stats.max,
                                "mean": col.numeric_stats.mean,
                            },
                            suggested_question=f"What caused extreme values in {col.name}?",
                        )
                    )
        return insights


insights_service = InsightsService()
