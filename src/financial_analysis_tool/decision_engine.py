"""Decision mapping for financial and ESG risk signals.

This module is **policy logic, not a statistical or ML model**. It converts
explainable monitoring signals into deterministic portfolio actions that can be
shown in an API, dashboard, IC memo, or audit log.

Code enums stay stable for the API contract. Each enum also maps to a PE-style
portfolio monitoring label (Invest / Watch / Engage / Reduce). ``Pass`` is an
IC underwriting outcome documented in case memos, not an automated signal
output—kill criteria belong in human underwriting, not a black-box score.
"""

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

PEMonitoringAction = Literal[
    "Invest",
    "Watch",
    "Engage",
    "Reduce",
]

# Stable policy id for audit trails. Bump when precedence rules change.
DECISION_POLICY_VERSION = "pe-monitoring-v1"

# Code enum → PE portfolio monitoring language (post-investment monitoring).
# Pass is reserved for IC entry underwriting in memos, not auto-emitted here.
PE_ACTION_BY_DECISION: dict[Decision, PEMonitoringAction] = {
    "HOLD": "Invest",
    "REVIEW": "Watch",
    "ENGAGE": "Engage",
    "REDUCE_EXPOSURE": "Reduce",
    "ENHANCED_DUE_DILIGENCE": "Watch",
}

SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass(frozen=True, slots=True)
class DecisionRecommendation:
    """Explainable portfolio recommendation derived from rule-based signals.

    Attributes:
        company: Company receiving the recommendation.
        decision: Stable API/portfolio enum selected by policy rules.
        pe_action: PE monitoring label aligned to Invest/Watch/Engage/Reduce.
        highest_severity: Highest signal severity observed.
        signal_count: Number of signals considered.
        key_drivers: Top reasons that explain the decision (audit trail).
        rationale: Human-readable explanation of the selected action.
        policy_version: Version tag for the deterministic mapping policy.
    """

    company: str
    decision: Decision
    pe_action: PEMonitoringAction
    highest_severity: str
    signal_count: int
    key_drivers: list[str]
    rationale: str
    policy_version: str = DECISION_POLICY_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Convert the recommendation to a JSON-serializable dictionary.

        Returns:
            dict[str, Any]: Plain decision payload for API and audit logging.
        """
        return asdict(self)


def pe_action_for_decision(decision: Decision) -> PEMonitoringAction:
    """Map a stable code enum to PE portfolio monitoring language.

    Args:
        decision: Existing API decision enum.

    Returns:
        PEMonitoringAction: Invest, Watch, Engage, or Reduce.
    """
    return PE_ACTION_BY_DECISION[decision]


def map_signals_to_decision(
    company: str,
    signals: Iterable[RiskSignal],
) -> DecisionRecommendation:
    """Map explainable risk signals to a portfolio monitoring decision.

    Args:
        company: Company receiving the decision recommendation.
        signals: Financial and ESG monitoring signals for the company.

    Returns:
        DecisionRecommendation: Code enum, PE action label, severity, signal
        count, drivers, rationale, and policy version.

    Notes:
        Precedence is deterministic and fully explainable from inputs:
        three or more high-severity signals → ``REDUCE_EXPOSURE`` (Reduce);
        high governance, controversy, or liquidity → ``ENHANCED_DUE_DILIGENCE``
        (Watch + diligence); carbon/transition → ``ENGAGE`` (Engage);
        medium-only → ``REVIEW`` (Watch); no signals → ``HOLD`` (Invest /
        maintain). No ML scoring is used.
    """
    signal_list = list(signals)
    if not signal_list:
        decision: Decision = "HOLD"
        return DecisionRecommendation(
            company=company,
            decision=decision,
            pe_action=pe_action_for_decision(decision),
            highest_severity="LOW",
            signal_count=0,
            key_drivers=[],
            rationale=(
                "No financial or ESG risk signals breached monitoring thresholds; "
                "PE monitoring action is Invest (maintain position) under "
                f"{DECISION_POLICY_VERSION}."
            ),
        )

    highest_severity = max(signal_list, key=lambda signal: SEVERITY_RANK[signal.severity]).severity
    high_signals = [signal for signal in signal_list if signal.severity == "HIGH"]
    medium_signals = [signal for signal in signal_list if signal.severity == "MEDIUM"]
    high_types = {signal.signal_type for signal in high_signals}

    if len(high_signals) >= 3:
        decision = "REDUCE_EXPOSURE"
        rationale = (
            "Multiple high-severity signals indicate concentrated downside risk; "
            "PE monitoring action is Reduce."
        )
    elif high_types & {"WEAK_GOVERNANCE", "ELEVATED_CONTROVERSY_RISK", "LIQUIDITY_STRESS"}:
        decision = "ENHANCED_DUE_DILIGENCE"
        rationale = (
            "A high-severity governance, controversy, or liquidity signal requires "
            "deeper review; PE monitoring action is Watch with enhanced diligence "
            "(Pass remains an IC judgment, not an auto-exit)."
        )
    elif high_signals or any(
        signal.signal_type in {"HIGH_CARBON_INTENSITY", "TRANSITION_RISK_WATCHLIST"}
        for signal in medium_signals
    ):
        decision = "ENGAGE"
        rationale = (
            "Risk signals are material enough to require active engagement with "
            "management; PE monitoring action is Engage."
        )
    elif medium_signals:
        decision = "REVIEW"
        rationale = (
            "Medium-severity signals should be reviewed in the next monitoring "
            "cycle; PE monitoring action is Watch."
        )
    else:
        decision = "HOLD"
        rationale = (
            "Only low-severity signals are present, so ongoing monitoring is "
            "sufficient; PE monitoring action is Invest (maintain)."
        )

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
        pe_action=pe_action_for_decision(decision),
        highest_severity=highest_severity,
        signal_count=len(signal_list),
        key_drivers=key_drivers,
        rationale=rationale,
    )
