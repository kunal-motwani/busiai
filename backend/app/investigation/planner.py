"""Investigation Planner for decomposing business questions into hypotheses."""
import logging
import re
import uuid
from typing import List, Optional
from app.ingestion.models import DatasetInfo
from app.llm.provider import DeterministicReasoner, get_llm_provider
from app.investigation.models import Hypothesis, HypothesisStatus, InvestigationPlan
from app.profiling.models import DatasetProfile

logger = logging.getLogger(__name__)


class InvestigationPlanner:
    """Creates deterministic and LLM-guided structured investigation plans."""

    async def create_plan(
        self,
        dataset: DatasetInfo,
        profile: DatasetProfile,
        question: str,
        focus_metric: Optional[str] = None,
    ) -> InvestigationPlan:
        """Create an LLM-guided plan, falling back to deterministic hypotheses."""
        fallback_plan = self._create_deterministic_plan(dataset, profile, question, focus_metric)
        provider = get_llm_provider()
        if isinstance(provider, DeterministicReasoner):
            return fallback_plan

        prompt = (
            "Create up to four testable business hypotheses for this investigation. "
            "Use only the supplied metrics and dimensions.\n\n"
            f"Business question: {question}\n"
            f"Target metric: {fallback_plan.target_metric}\n"
            f"Available metrics: {profile.key_metrics}\n"
            f"Available dimensions: {profile.key_dimensions}\n"
            f"Rows: {profile.total_rows}"
        )
        schema = (
            '{"hypotheses": [{"statement": "...", "rationale": "...", '
            '"target_metric": "metric", "target_dimension": "dimension or null"}]}'
        )

        try:
            generated = await provider.generate_json(prompt, schema)
            hypotheses = self._hypotheses_from_llm(
                generated,
                fallback_plan.target_metric,
                profile.key_metrics,
                profile.key_dimensions,
            )
            if hypotheses:
                logger.info("Groq generated %d investigation hypotheses", len(hypotheses))
                fallback_plan.hypotheses = hypotheses
        except Exception:
            logger.exception("Groq hypothesis generation failed; using deterministic plan")

        return fallback_plan

    def _create_deterministic_plan(
        self,
        dataset: DatasetInfo,
        profile: DatasetProfile,
        question: str,
        focus_metric: Optional[str] = None,
    ) -> InvestigationPlan:
        """Formulate a comprehensive investigation plan with testable hypotheses."""
        target_metric = focus_metric or self._detect_target_metric(question, profile)
        target_period = self._detect_target_period(question)

        hypotheses: List[Hypothesis] = []
        dimensions = profile.key_dimensions or ["category", "region", "segment"]
        metrics = profile.key_metrics or [target_metric]

        # Hypothesis 1: Segment/Dimension Breakdown Shift
        if dimensions:
            dim_name = dimensions[0]
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:6]}",
                    statement=f"A specific {dim_name} drove the primary variance in {target_metric}.",
                    rationale=f"Concentration and variance across {dim_name} categories often account for major top-level swings.",
                    target_metric=target_metric,
                    target_dimension=dim_name,
                    status=HypothesisStatus.PENDING,
                )
            )

        # Hypothesis 2: Secondary Dimension Shift
        if len(dimensions) > 1:
            dim_name2 = dimensions[1]
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:6]}",
                    statement=f"Performance drop or surge was concentrated within specific {dim_name2} segments.",
                    rationale=f"Cross-segment differences in {dim_name2} may isolate the root cause.",
                    target_metric=target_metric,
                    target_dimension=dim_name2,
                    status=HypothesisStatus.PENDING,
                )
            )

        # Hypothesis 3: Correlated Secondary Metric Impact (e.g., churn, discount, cost, CAC)
        secondary_metrics = [m for m in metrics if m != target_metric]
        if secondary_metrics:
            sec_metric = secondary_metrics[0]
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:6]}",
                    statement=f"Adverse or favorable shift in {sec_metric} directly impacted {target_metric}.",
                    rationale=f"Changes in underlying operational metrics such as {sec_metric} influence aggregate performance.",
                    target_metric=sec_metric,
                    target_dimension=dimensions[0] if dimensions else None,
                    status=HypothesisStatus.PENDING,
                )
            )

        # Hypothesis 4: Extreme Outliers / Anomalies
        hypotheses.append(
            Hypothesis(
                id=f"hyp_{uuid.uuid4().hex[:6]}",
                statement=f"One or more statistical outlier events heavily skewed aggregate {target_metric}.",
                rationale="Extreme transactional anomalies or one-off records can distort overall trend numbers.",
                target_metric=target_metric,
                status=HypothesisStatus.PENDING,
            )
        )

        return InvestigationPlan(
            dataset_id=dataset.id,
            business_question=question,
            target_metric=target_metric,
            target_period=target_period,
            hypotheses=hypotheses,
        )

    def _hypotheses_from_llm(
        self,
        payload: dict,
        default_metric: str,
        metrics: List[str],
        dimensions: List[str],
    ) -> List[Hypothesis]:
        """Validate the model's structured hypotheses against the dataset schema."""
        hypotheses: List[Hypothesis] = []
        for item in payload.get("hypotheses", [])[:4]:
            if not isinstance(item, dict) or not item.get("statement"):
                continue
            metric = item.get("target_metric")
            dimension = item.get("target_dimension")
            hypotheses.append(
                Hypothesis(
                    id=f"hyp_{uuid.uuid4().hex[:6]}",
                    statement=str(item["statement"]),
                    rationale=str(item.get("rationale") or "LLM-generated business hypothesis."),
                    target_metric=metric if metric in metrics else default_metric,
                    target_dimension=dimension if dimension in dimensions else None,
                    status=HypothesisStatus.PENDING,
                )
            )
        return hypotheses

    def _detect_target_metric(self, question: str, profile: DatasetProfile) -> str:
        """Infer which metric the user is asking about."""
        q_lower = question.lower()
        for metric in profile.key_metrics:
            if metric.lower() in q_lower:
                return metric

        # Common business keywords mapping
        keywords = {
            "revenue": ["revenue", "sales", "mrr", "arr", "amount", "income"],
            "profit": ["profit", "margin", "earnings"],
            "churn": ["churn", "churn_rate", "attrition", "lost"],
            "cac": ["cac", "acquisition_cost", "spend", "ad_spend"],
            "cost": ["cost", "expense", "spend"],
        }

        for std_name, aliases in keywords.items():
            if any(alias in q_lower for alias in aliases):
                for metric in profile.key_metrics:
                    if any(alias in metric.lower() for alias in aliases):
                        return metric

        return profile.key_metrics[0] if profile.key_metrics else "metric"

    def _detect_target_period(self, question: str) -> Optional[str]:
        """Extract explicit months or years mentioned in the question."""
        months = [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
            "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
        ]
        q_lower = question.lower()
        for m in months:
            if re.search(r"\b" + m + r"\b", q_lower):
                return m.capitalize()
        # Look for YYYY or YYYY-MM
        match = re.search(r"\b(20\d{2}(-\d{2})?)\b", question)
        if match:
            return match.group(1)
        return None


investigation_planner = InvestigationPlanner()
