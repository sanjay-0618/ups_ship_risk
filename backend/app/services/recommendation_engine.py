"""
Recommendation Engine — generates deterministic, template-based recommendations.
LLM integration is optional (uses templates when no key is present).
"""
from __future__ import annotations
from typing import Any
from app.services.external_providers import GeminiLLMProvider


class RecommendationEngine:
    def __init__(self):
        self.llm = GeminiLLMProvider()

    def generate_route_recommendation(
        self, routes: list[dict], optimization_mode: str
    ) -> dict[str, Any]:
        """Generate recommendation text for the best route."""
        if not routes:
            return self._format("No routes available", "No data", "N/A", "LOW")

        best = routes[0]
        worst = routes[-1] if len(routes) > 1 else best
        route_name = best.get("route_name", "Route A")
        risk_level = best.get("risk_level", "LOW")

        delay_saved = int(worst.get("risk_adjusted_time_minutes", 0) - best.get("risk_adjusted_time_minutes", 0))
        delay_str = self._format_minutes(delay_saved)

        dist_diff = int(best.get("distance_km", 0) - worst.get("distance_km", 0))
        sla_pct = int(best.get("sla_breach_probability", 0) * 100)

        if optimization_mode == "safest":
            action = f"Take {route_name} — it has the lowest disruption risk."
            reason = (
                f"{route_name} has a risk score of {best.get('overall_risk_score', 0):.1f}/10, "
                f"significantly lower than alternatives. "
                f"SLA breach probability is just {sla_pct}%."
            )
            benefit = f"Reduces risk-adjusted travel time by approximately {delay_str} compared to the highest-risk option."
        elif optimization_mode == "fastest":
            action = f"Take {route_name} — it offers the fastest risk-adjusted arrival time."
            reason = (
                f"{route_name} has a risk-adjusted time of "
                f"{self._format_minutes(int(best.get('risk_adjusted_time_minutes', 0)))} "
                f"including all expected delays."
            )
            benefit = f"Fastest estimated arrival with {sla_pct}% SLA breach probability."
        else:  # balanced
            action = f"Take {route_name} — optimal balance of speed, distance, and safety."
            if dist_diff > 0:
                reason = (
                    f"Although {route_name} is {abs(dist_diff)} km longer than the shortest option, "
                    f"its lower disruption risk ({best.get('overall_risk_score', 0):.1f}/10) results in "
                    f"a faster expected arrival time."
                )
            else:
                reason = (
                    f"{route_name} offers the best combined score across travel time, distance, "
                    f"and disruption risk ({best.get('overall_risk_score', 0):.1f}/10)."
                )
            benefit = f"Reduces predicted delay by approximately {delay_str}. SLA breach probability: {sla_pct}%."

        # Optional Gemini generative enrichment
        if hasattr(self, 'llm') and self.llm.is_available():
            try:
                p = f"Corridor from {best.get('origin', 'origin')} to {best.get('destination', 'destination')}: Recommend {route_name} with risk score {best.get('overall_risk_score', 0):.1f}/10 and SLA breach prob {sla_pct}%. Optimization mode: {optimization_mode}. Explain in 1-2 tactical sentences why dispatchers should select this route."
                llm_reason = self.llm.generate_explanation(p)
                if llm_reason:
                    reason = llm_reason
            except Exception:
                pass

        return self._format(action, reason, benefit, "HIGH" if risk_level == "LOW" else "MEDIUM")

    def generate_disruption_recommendation(self, disruption_data: dict) -> dict[str, Any]:
        """Generate recommendation after a disruption simulation."""
        scenario = disruption_data.get("scenario", "Disruption")
        location = disruption_data.get("location", "the affected area")
        severity = disruption_data.get("severity", "HIGH")
        before_delay = disruption_data.get("before_avg_delay", 30)
        after_delay = disruption_data.get("after_avg_delay", 180)
        delay_reduction = after_delay - before_delay

        scenario_actions = {
            "Severe Weather": f"Reroute shipments to avoid the weather corridor near {location}.",
            "Major Traffic Congestion": f"Switch to alternative routes bypassing {location} until congestion clears.",
            "Hub Congestion": f"Divert affected shipments to alternative processing hubs near {location}.",
            "Flight Delay": f"Arrange ground transport alternatives for air shipments affected by delays near {location}.",
            "Port Delay": f"Redirect port-bound shipments to alternative terminals or hold at origin.",
            "Geopolitical Event": f"Activate contingency routing plan to avoid {location} corridor.",
            "Road Closure": f"Reroute ground shipments away from the closure near {location}.",
        }

        action = scenario_actions.get(scenario, f"Implement contingency routing to avoid {location}.")

        reason = (
            f"{scenario} near {location} (severity: {severity}) is causing an estimated "
            f"{self._format_minutes(int(delay_reduction))} additional delay per affected shipment. "
            f"SLA breach risk has significantly increased for shipments on this corridor."
        )

        benefit = (
            f"Rerouting could reduce predicted delay by approximately "
            f"{self._format_minutes(int(delay_reduction))} per shipment and lower SLA breach risk."
        )

        confidence = "HIGH" if severity in ("HIGH", "CRITICAL") else "MEDIUM"
        return self._format(action, reason, benefit, confidence)

    def generate_shipment_recommendation(
        self, shipment: dict, risk: dict
    ) -> dict[str, Any]:
        """Generate recommendation for a specific shipment."""
        risk_level = risk.get("risk_level", "LOW")
        risk_score = risk.get("overall_risk_score", 1.0)
        sla_prob = risk.get("sla_breach_probability", 0.05)
        delay = risk.get("expected_delay_minutes", 0)
        priority = shipment.get("priority", "Normal")

        top_factors = risk.get("risk_factors", [])
        factor_str = top_factors[0] if top_factors else "multiple risk factors"

        if risk_level == "CRITICAL":
            action = f"URGENT: Immediate intervention required for {shipment.get('tracking_number', 'this shipment')}."
            reason = f"Risk score {risk_score:.1f}/10 with {int(sla_prob*100)}% SLA breach probability. Primary cause: {factor_str}."
            benefit = f"Proactive rerouting could save up to {self._format_minutes(int(delay * 0.6))} delay."
            confidence = "HIGH"
        elif risk_level == "HIGH":
            action = f"Monitor closely and consider alternative routing for {shipment.get('tracking_number', 'this shipment')}."
            reason = f"Risk score {risk_score:.1f}/10 with {int(sla_prob*100)}% SLA breach probability. {factor_str}."
            benefit = f"Rerouting may reduce expected delay by {self._format_minutes(int(delay * 0.4))}."
            confidence = "MEDIUM"
        elif risk_level == "MEDIUM":
            action = f"Keep under observation — {shipment.get('tracking_number', 'shipment')} has elevated risk."
            reason = f"Risk score {risk_score:.1f}/10. {factor_str}."
            benefit = "No immediate action needed; monitor for deterioration."
            confidence = "MEDIUM"
        else:
            action = "No action required."
            reason = f"Risk score {risk_score:.1f}/10 — shipment is on track."
            benefit = "Continue standard monitoring."
            confidence = "HIGH"

        return self._format(action, reason, benefit, confidence)

    # ──────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────

    def _format(self, action: str, reason: str, benefit: str, confidence: str) -> dict:
        return {
            "action": action,
            "reason": reason,
            "expected_benefit": benefit,
            "confidence": confidence,
        }

    def _format_minutes(self, minutes: int) -> str:
        if minutes < 60:
            return f"{minutes}m"
        h = minutes // 60
        m = minutes % 60
        if m == 0:
            return f"{h}h"
        return f"{h}h {m}m"
