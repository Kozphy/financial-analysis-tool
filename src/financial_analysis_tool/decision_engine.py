"""Decision mapping for financial and ESG risk signals."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Literal

from .risk_signals import RiskSignal


Decision = Literal[
    "HOLD",
    "REVIEW",
    "ENGAGE",
    "REDUCE_EXPOSURE",
    "ENHANCED_DUE_DILIGENCE",
]

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass(frozen=True, slots=True)
class DecisionRecommendation:
    """Business-facing recommendation derived from explainable risk signals."""

    company: str
    decision: Decision
    highest_severity: str
    signal_count: int
    key_drivers: list[str]
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        """Return the decision in JSON-serializable form."""
        return asdict(self)


def map_signals_to_decision(
    company: str,
    signals: Iterable[RiskSignal],
) -> DecisionRecommendation:
    """Map explainable risk signals to a portfolio monitoring decision.

    The mapping is deterministic and deliberately simple so analysts can explain
    why a company moves from monitoring to engagement, due diligence, or reduced
    exposure without relying on an opaque score.
    """
    signal_list = list(signals)
    if not signal_list:
        return DecisionRecommendation(
            company=company,
            decision="HOLD",
            highest_severity="LOW",
            signal_count=0,
            key_drivers=[],
            rationale="No financial or ESG risk signals breached the monitoring thresholds.",
        )

    highest_severity = max(signal_list, key=lambda signal: SEVERITY_RANK[signal.severity]).severity
    high_signals = [signal for signal in signal_list if signal.severity == "HIGH"]
    medium_signals = [signal for signal in signal_list if signal.severity == "MEDIUM"]
    high_types = {signal.signal_type for signal in high_signals}

    if len(high_signals) >= 3:
        decision: Decision = "REDUCE_EXPOSURE"
        rationale = "Multiple high-severity signals indicate concentrated downside risk."
    elif high_types & {"WEAK_GOVERNANCE", "ELEVATED_CONTROVERSY_RISK", "LIQUIDITY_STRESS"}:
        decision = "ENHANCED_DUE_DILIGENCE"
        rationale = "A high-severity governance, controversy, or liquidity signal requires deeper review."
    elif high_signals or any(
        signal.signal_type in {"HIGH_CARBON_INTENSITY", "TRANSITION_RISK_WATCHLIST"}
        for signal in medium_signals
    ):
        decision = "ENGAGE"
        rationale = "Risk signals are material enough to require active engagement with management."
    elif medium_signals:
        decision = "REVIEW"
        rationale = "Medium-severity signals should be reviewed in the next monitoring cycle."
    else:
        decision = "HOLD"
        rationale = "Only low-severity signals are present, so ongoing monitoring is sufficient."

    key_drivers = [
        f"{signal.signal_type}: {signal.reason}"
        for signal in sorted(
            signal_list,
            key=lambda signal: (SEVERITY_RANK[signal.severity], signal.signal_type),
            reverse=True,
        )[:3]
    ]

    return DecisionRecommendation(
        company=company,
        decision=decision,
        highest_severity=highest_severity,
        signal_count=len(signal_list),
        key_drivers=key_drivers,
        rationale=rationale,
    )
