"""Decision Graph Builder transforming investigations into visual node trees."""
from typing import List
from app.graph.models import (
    DecisionGraphEdge,
    DecisionGraphNode,
    DecisionGraphResponse,
    GraphNodePosition,
)
from app.investigation.models import HypothesisStatus, InvestigationResult


class DecisionGraphBuilder:
    """Builds React Flow-compatible graph representation of the investigation reasoning chain."""

    def build_graph(self, result: InvestigationResult) -> DecisionGraphResponse:
        nodes: List[DecisionGraphNode] = []
        edges: List[DecisionGraphEdge] = []

        # 1. Root Question Node
        root_id = "node_question"
        nodes.append(
            DecisionGraphNode(
                id=root_id,
                type="question",
                data={
                    "label": result.question,
                    "target_metric": result.target_metric,
                    "badge": "Business Question",
                },
                position=GraphNodePosition(x=400.0, y=50.0),
            )
        )

        y_hyp = 180.0
        y_ev = 340.0
        y_act = 500.0
        y_sim = 650.0

        x_spacing = 280.0
        total_hyps = len(result.hypotheses_tested)
        start_x = 400.0 - ((total_hyps - 1) * x_spacing / 2.0) if total_hyps > 0 else 400.0

        evidence_by_hyp = {ev.hypothesis_id: ev for ev in result.evidence_package if ev.hypothesis_id}

        for idx, hyp in enumerate(result.hypotheses_tested):
            hyp_x = start_x + (idx * x_spacing)
            hyp_node_id = f"node_hyp_{hyp.id}"

            # Hypothesis Node
            is_confirmed = hyp.status == HypothesisStatus.CONFIRMED
            nodes.append(
                DecisionGraphNode(
                    id=hyp_node_id,
                    type="hypothesis",
                    data={
                        "label": hyp.statement,
                        "status": hyp.status.value,
                        "confidence": hyp.confidence_score,
                        "badge": f"Hypothesis ({hyp.status.value})",
                    },
                    position=GraphNodePosition(x=hyp_x, y=y_hyp),
                )
            )

            # Edge Question -> Hypothesis
            edges.append(
                DecisionGraphEdge(
                    id=f"edge_q_{hyp.id}",
                    source=root_id,
                    target=hyp_node_id,
                    label="tested by",
                    animated=is_confirmed,
                )
            )

            # Evidence Node
            ev_item = evidence_by_hyp.get(hyp.id)
            if ev_item:
                ev_node_id = f"node_ev_{ev_item.id}"
                nodes.append(
                    DecisionGraphNode(
                        id=ev_node_id,
                        type="evidence",
                        data={
                            "label": ev_item.title,
                            "summary": ev_item.summary,
                            "sql": ev_item.sql_query,
                            "proof_value": ev_item.proof.calculated_value,
                            "confidence": ev_item.proof.confidence_pct,
                            "badge": "Calculated Evidence",
                        },
                        position=GraphNodePosition(x=hyp_x, y=y_ev),
                    )
                )

                # Edge Hypothesis -> Evidence
                edges.append(
                    DecisionGraphEdge(
                        id=f"edge_h_e_{hyp.id}",
                        source=hyp_node_id,
                        target=ev_node_id,
                        label="proved by",
                        animated=is_confirmed,
                    )
                )

        # Recommendation / Action Nodes
        total_recs = len(result.recommendations)
        rec_start_x = 400.0 - ((total_recs - 1) * 320.0 / 2.0) if total_recs > 0 else 400.0

        for r_idx, rec in enumerate(result.recommendations):
            rec_x = rec_start_x + (r_idx * 320.0)
            rec_node_id = f"node_rec_{rec.id}"
            nodes.append(
                DecisionGraphNode(
                    id=rec_node_id,
                    type="action",
                    data={
                        "label": rec.title,
                        "description": rec.description,
                        "impact": rec.projected_impact,
                        "priority": rec.priority,
                        "badge": f"Action Recommendation ({rec.priority.upper()})",
                    },
                    position=GraphNodePosition(x=rec_x, y=y_act),
                )
            )

            # Connect from confirmed hypotheses
            for hyp in result.hypotheses_tested:
                if hyp.status == HypothesisStatus.CONFIRMED:
                    ev_item = evidence_by_hyp.get(hyp.id)
                    src_id = f"node_ev_{ev_item.id}" if ev_item else f"node_hyp_{hyp.id}"
                    edges.append(
                        DecisionGraphEdge(
                            id=f"edge_ev_rec_{hyp.id}_{rec.id}",
                            source=src_id,
                            target=rec_node_id,
                            label="recommends",
                            animated=True,
                        )
                    )

        # Final Simulation Node
        sim_node_id = "node_simulation"
        nodes.append(
            DecisionGraphNode(
                id=sim_node_id,
                type="simulation",
                data={
                    "label": "Grounded What-If Simulator",
                    "description": f"Simulate impact of recommendations on {result.target_metric}.",
                    "badge": "What-If Scenario",
                },
                position=GraphNodePosition(x=400.0, y=y_sim),
            )
        )

        for rec in result.recommendations:
            edges.append(
                DecisionGraphEdge(
                    id=f"edge_rec_sim_{rec.id}",
                    source=f"node_rec_{rec.id}",
                    target=sim_node_id,
                    label="simulate",
                    animated=True,
                )
            )

        return DecisionGraphResponse(
            nodes=nodes,
            edges=edges,
            summary=f"Decision graph generated with {len(nodes)} reasoning nodes and {len(edges)} verified links.",
        )


decision_graph_builder = DecisionGraphBuilder()
