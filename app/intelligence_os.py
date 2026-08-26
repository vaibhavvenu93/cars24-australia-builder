from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ==========================================================
# REPOSITORY IMPORT PATH
# ==========================================================

REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ==========================================================
# VIEW IMPORTS
# ==========================================================

from app.views.builder import (
    render_experiments,
    render_opportunity_radar,
    render_scenario_lab,
)
from app.views.growth import (
    render_funnel_analytics,
    render_growth_intelligence,
    render_market_intelligence,
)
from app.views.inventory import (
    render_capital_intelligence,
    render_portfolio,
    render_vehicle_360,
)
from app.views.operations import (
    render_action_centre,
    render_location_performance,
    render_transfer_intelligence,
    render_vendor_intelligence,
)

from data.integrations import (
    get_integration_sources,
    get_intelligence_coverage,
)
from engines.data_hub import (
    describe_detection,
    detect_dataset,
)
from models.integration import (
    IntelligenceCapability,
    IntegrationCategory,
    IntegrationStatus,
)


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="CARS24 Australia Intelligence OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# DESIGN SYSTEM
# ==========================================================

st.markdown(
    """
<style>

.stApp {
    background:
        radial-gradient(
            circle at 82% -8%,
            rgba(77, 81, 255, 0.08),
            transparent 30%
        ),
        #F7F8FA;
    color: #12141A;
}

.block-container {
    max-width: 1540px;
    padding-top: 2.2rem;
    padding-bottom: 5rem;
    padding-left: 2.2rem;
    padding-right: 2.2rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #0C0D10;
    border-right: 1px solid #202126;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] * {
    color: #F6F7F9;
}

section[data-testid="stSidebar"]
div[role="radiogroup"] > label {
    padding: 8px 9px;
    margin-bottom: 2px;
    border-radius: 8px;
}

section[data-testid="stSidebar"]
div[role="radiogroup"] > label:hover {
    background: #17191F;
}

section[data-testid="stSidebar"]
div[data-baseweb="select"] * {
    color: #17191E !important;
}


/* TYPOGRAPHY */

h1 {
    color: #101217 !important;
    font-size: 3.0rem !important;
    line-height: 1.02 !important;
    letter-spacing: -0.055em !important;
    font-weight: 780 !important;
}

h2 {
    color: #12141A !important;
    letter-spacing: -0.035em !important;
    font-weight: 720 !important;
}

h3 {
    color: #17191E !important;
    letter-spacing: -0.025em !important;
}

p {
    line-height: 1.55;
}


/* METRICS */

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.88);
    border: 1px solid #E2E4E9;
    border-radius: 14px;
    padding: 17px 18px;
    min-height: 122px;
    box-shadow:
        0 1px 2px rgba(16,24,40,0.02),
        0 3px 10px rgba(16,24,40,0.025);
}

div[data-testid="stMetricLabel"] {
    font-weight: 630;
    color: #656A73;
}

div[data-testid="stMetricValue"] {
    letter-spacing: -0.035em;
}


/* BUTTONS */

.stButton > button {
    min-height: 42px;
    border-radius: 9px;
    font-weight: 650;
    border: 1px solid #D0D3DA;
    background: white;
}

.stButton > button:hover {
    border-color: #16181D;
}

.stButton > button[kind="primary"] {
    background: #111318;
    color: white;
    border-color: #111318;
}


/* CONTAINERS */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

div[data-testid="stExpander"] {
    border-radius: 10px;
    background: rgba(255,255,255,0.70);
}


/* INPUTS */

div[data-baseweb="select"] > div {
    border-radius: 9px;
}

div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.70);
    border-radius: 14px;
}


/* CUSTOM */

.eyebrow {
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    color: #6B7079;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.kicker {
    font-size: 1.05rem;
    color: #60656E;
    max-width: 850px;
    margin-top: -7px;
}

.brand-mark {
    font-size: 1.28rem;
    font-weight: 850;
    letter-spacing: -0.04em;
    color: #FFFFFF;
    margin-bottom: 2px;
}

.brand-sub {
    font-size: 0.67rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #92969F;
}

.status-green {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: #21B26F;
    margin-right: 7px;
}

.hero-strip {
    padding: 15px 18px;
    border: 1px solid #E1E3E8;
    background: rgba(255,255,255,0.72);
    border-radius: 12px;
    font-size: 0.88rem;
    color: #565B64;
}

.priority-red {
    color: #D13F3F;
    font-weight: 700;
}

.priority-amber {
    color: #B57913;
    font-weight: 700;
}

.priority-green {
    color: #16895A;
    font-weight: 700;
}

</style>
""",
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================


def pretty_enum(value: str) -> str:
    return value.replace("_", " ").title()


def capability_name(
    capability: IntelligenceCapability,
) -> str:
    return pretty_enum(
        capability.value
    )


def status_text(
    status: IntegrationStatus,
) -> str:

    if status == IntegrationStatus.CONNECTED:
        return "● CONNECTED"

    if status == IntegrationStatus.SIMULATED:
        return "● SIMULATED"

    if status == IntegrationStatus.READY:
        return "○ READY"

    return "○ NOT CONNECTED"


def render_page_header(
    eyebrow: str,
    title: str,
    description: str,
) -> None:

    st.markdown(
        f'<div class="eyebrow">{eyebrow}</div>',
        unsafe_allow_html=True,
    )

    st.title(title)

    st.markdown(
        f'<div class="kicker">{description}</div>',
        unsafe_allow_html=True,
    )

    st.write("")


def read_uploaded_dataset(
    uploaded_file,
) -> pd.DataFrame:

    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        return pd.read_csv(
            uploaded_file
        )

    if (
        name.endswith(".xlsx")
        or name.endswith(".xls")
    ):

        try:
            return pd.read_excel(
                uploaded_file
            )

        except ImportError:
            raise RuntimeError(
                "Excel support requires openpyxl. "
                "Upload CSV for now or install openpyxl."
            )

    raise ValueError(
        "Supported formats are CSV, XLSX and XLS."
    )


# ==========================================================
# INTELLIGENCE STATE
# ==========================================================

integration_sources = (
    get_integration_sources()
)

coverage = (
    get_intelligence_coverage()
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-mark">
            ⚡ CARS24
        </div>

        <div class="brand-sub">
            Australia Intelligence OS
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.write("")

    environment = st.selectbox(
        "Operating environment",
        [
            "Executive",
            "Growth",
            "Inventory",
            "Operations",
            "Builder",
        ],
    )

    st.write("")

    navigation_by_environment = {
        "Executive": [
            "Command Centre",
            "Morning Brief",
        ],
        "Growth": [
            "Growth Intelligence",
            "Funnel Analytics",
            "Market Intelligence",
        ],
        "Inventory": [
            "Portfolio",
            "Vehicle 360",
            "Capital Intelligence",
        ],
        "Operations": [
            "Location Performance",
            "Vendor Intelligence",
            "Transfer Intelligence",
            "Action Centre",
        ],
        "Builder": [
            "Opportunity Radar",
            "Scenario Lab",
            "Experiments",
            "Data Hub",
            "Integrations",
        ],
    }

    page = st.radio(
        "Navigation",
        navigation_by_environment[
            environment
        ],
        label_visibility="collapsed",
    )

    st.write("")
    st.write("")

    st.caption(
        "SYSTEM"
    )

    st.markdown(
        """
        <div style="
            padding:11px 12px;
            background:#15171C;
            border:1px solid #262930;
            border-radius:9px;
            margin-bottom:11px;
        ">
            <span class="status-green"></span>
            Intelligence engine active
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "INTELLIGENCE COVERAGE"
    )

    st.markdown(
        f"### {coverage.overall_score:.0f}%"
    )

    st.progress(
        coverage.overall_score / 100
    )

    st.caption(
        f"{len(coverage.unlocked_capabilities)} "
        "capabilities unlocked"
    )

    st.write("")

    st.caption(
        "Prototype uses synthetic operational data. "
        "No confidential CARS24 data is connected."
    )


# ==========================================================
# EXECUTIVE — COMMAND CENTRE
# ==========================================================

if page == "Command Centre":

    render_page_header(
        "Executive Command",
        "Good morning. Here's what changed.",
        (
            "One operating view across growth, inventory, "
            "capital and execution."
        ),
    )

    top_left, top_right = (
        st.columns(
            [4, 1]
        )
    )

    with top_left:

        st.markdown(
            """
            <div class="hero-strip">
                <b>Australia</b>
                &nbsp;&nbsp;•&nbsp;&nbsp;
                All locations
                &nbsp;&nbsp;•&nbsp;&nbsp;
                Last simulated refresh: 08:42 AEST
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_right:

        st.button(
            "↻ Refresh Intelligence",
            type="primary",
            use_container_width=True,
        )

    st.write("")

    c1, c2, c3, c4, c5 = (
        st.columns(5)
    )

    c1.metric(
        "Revenue",
        "$12.4M",
        "8.2%",
    )

    c2.metric(
        "Gross Profit",
        "$1.37M",
        "7.2%",
    )

    c3.metric(
        "Capital Deployed",
        "$8.42M",
        "$310K",
    )

    c4.metric(
        "Average Inventory Age",
        "41.2 days",
        "-3.1 days",
    )

    c5.metric(
        "Capital at Risk",
        "$624K",
        "-$81K",
        delta_color="inverse",
    )

    st.divider()

    left, right = st.columns(
        [1.55, 0.9]
    )

    with left:

        st.subheader(
            "Today's Intelligence"
        )

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="priority-red">'
                'P0 · CAPITAL'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                "### $184K of margin is newly exposed"
            )

            st.write(
                "12 vehicles crossed critical ageing thresholds. "
                "Four appear economically better suited to transfer "
                "than immediate markdown."
            )

            a1, a2 = st.columns(
                2
            )

            a1.button(
                "Investigate",
                key="cc_capital_investigate",
                use_container_width=True,
            )

            a2.button(
                "Simulate interventions",
                key="cc_capital_simulate",
                use_container_width=True,
            )

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="priority-amber">'
                'P1 · MARKET'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                "### Brisbane SUV demand is outrunning supply"
            )

            st.write(
                "The system identified seven Melbourne SUVs "
                "whose transfer economics appear favourable "
                "against current regional demand."
            )

            m1, m2 = st.columns(
                2
            )

            m1.button(
                "View market evidence",
                key="cc_market_evidence",
                use_container_width=True,
            )

            m2.button(
                "Run transfer model",
                key="cc_transfer_model",
                use_container_width=True,
            )

        with st.container(
            border=True
        ):

            st.markdown(
                '<div class="priority-green">'
                'P2 · GROWTH'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                "### RAV4 acquisition gap detected"
            )

            st.write(
                "Brisbane demand is high, local supply is "
                "constrained and historical unit economics "
                "remain attractive."
            )

            st.button(
                "Explore acquisition opportunity",
                key="cc_acquisition",
                use_container_width=True,
            )

    with right:

        st.subheader(
            "Business Pulse"
        )

        with st.container(
            border=True
        ):

            st.metric(
                "Intelligence Coverage",
                f"{coverage.overall_score:.0f}%",
            )

            st.progress(
                coverage.overall_score
                / 100
            )

            st.divider()

            st.markdown(
                "**Recommended next connection**"
            )

            st.write(
                coverage
                .recommended_next_connection
            )

            st.caption(
                coverage
                .recommendation_reason
            )

        with st.container(
            border=True
        ):

            st.markdown(
                "**Decision queue**"
            )

            st.metric(
                "Open decisions",
                "14",
            )

            st.write(
                "🔴 3 require executive review"
            )

            st.write(
                "🟠 6 require operator review"
            )

            st.write(
                "⚪ 5 being monitored"
            )


# ==========================================================
# EXECUTIVE — MORNING BRIEF
# ==========================================================

elif page == "Morning Brief":

    render_page_header(
        "Executive Intelligence",
        "Since you were last here",
        (
            "Only meaningful changes. "
            "No dashboard hunting, no raw data dump."
        ),
    )

    st.metric(
        "Meaningful changes",
        "7",
    )

    events = [
        (
            "Revenue",
            "Weekend sales finished 11.2% above simulated forecast.",
            "Positive",
        ),
        (
            "Inventory",
            "9 vehicles crossed the 45-day ageing threshold.",
            "Review",
        ),
        (
            "Market",
            "Brisbane SUV demand index increased 14%.",
            "Opportunity",
        ),
        (
            "Operations",
            "Melbourne recon turnaround deteriorated by 1.8 days.",
            "Review",
        ),
        (
            "Growth",
            "Paid-search enquiry → test-drive conversion fell 6pp.",
            "Review",
        ),
        (
            "Experiment",
            "Sydney response-time experiment reached scale confidence.",
            "Positive",
        ),
        (
            "Capital",
            "$182K moved into critical ageing inventory.",
            "Critical",
        ),
    ]

    for category, message, state in events:

        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [1, 5]
            )

            with c1:

                st.caption(
                    category.upper()
                )

            with c2:

                st.markdown(
                    f"**{message}**"
                )

                st.caption(
                    f"Signal: {state}"
                )

    st.button(
        "Show only decisions requiring action",
        type="primary",
    )


# ==========================================================
# GROWTH
# ==========================================================

elif page == "Growth Intelligence":

    render_growth_intelligence()


elif page == "Funnel Analytics":

    render_funnel_analytics()


elif page == "Market Intelligence":

    render_market_intelligence()


# ==========================================================
# INVENTORY
# ==========================================================

elif page == "Portfolio":

    render_portfolio()


elif page == "Vehicle 360":

    render_vehicle_360()


elif page == "Capital Intelligence":

    render_capital_intelligence()


# ==========================================================
# OPERATIONS
# ==========================================================

elif page == "Location Performance":

    render_location_performance()


elif page == "Vendor Intelligence":

    render_vendor_intelligence()


elif page == "Transfer Intelligence":

    render_transfer_intelligence()


elif page == "Action Centre":

    render_action_centre()


# ==========================================================
# BUILDER
# ==========================================================

elif page == "Opportunity Radar":

    render_opportunity_radar()


elif page == "Scenario Lab":

    render_scenario_lab()


elif page == "Experiments":

    render_experiments()


# ==========================================================
# DATA HUB
# ==========================================================

elif page == "Data Hub":

    render_page_header(
        "Adaptive Data Layer",
        "Bring CARS24 data. The OS adapts.",
        (
            "Upload operational data, detect its role in the "
            "vehicle lifecycle, map it to a canonical schema "
            "and identify which intelligence capabilities "
            "become available."
        ),
    )

    st.info(
        "Prototype mode: uploaded data is processed only "
        "inside the current Streamlit session. "
        "No CARS24 production systems are connected."
    )

    upload_col, help_col = st.columns(
        [1.7, 1]
    )

    with upload_col:

        uploaded_file = (
            st.file_uploader(
                "Upload operational dataset",
                type=[
                    "csv",
                    "xlsx",
                    "xls",
                ],
            )
        )

    with help_col:

        with st.container(
            border=True
        ):

            st.markdown(
                "**Supported operational domains**"
            )

            for category in (
                IntegrationCategory
            ):

                st.write(
                    "• "
                    + pretty_enum(
                        category.value
                    )
                )

    if uploaded_file is None:

        st.write("")

        st.subheader(
            "How Data Hub works"
        )

        h1, h2, h3, h4 = (
            st.columns(4)
        )

        cards = [
            (
                h1,
                "01",
                "Upload",
                "Bring CSV or spreadsheet data.",
            ),
            (
                h2,
                "02",
                "Detect",
                "Infer its operational domain.",
            ),
            (
                h3,
                "03",
                "Map",
                "Translate it to the canonical model.",
            ),
            (
                h4,
                "04",
                "Unlock",
                "Recalculate available intelligence.",
            ),
        ]

        for (
            column,
            number,
            title,
            copy,
        ) in cards:

            with column:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### {number}"
                    )

                    st.markdown(
                        f"**{title}**"
                    )

                    st.caption(
                        copy
                    )

        st.divider()

        st.subheader(
            "Current Data Coverage"
        )

        for (
            category,
            score,
        ) in (
            coverage
            .category_scores
            .items()
        ):

            name_col, bar_col, score_col = (
                st.columns(
                    [1.4, 4, 0.7]
                )
            )

            with name_col:

                st.write(
                    pretty_enum(
                        category.value
                    )
                )

            with bar_col:

                st.progress(
                    score / 100
                )

            with score_col:

                st.write(
                    f"{score:.0f}%"
                )

    else:

        try:

            dataframe = (
                read_uploaded_dataset(
                    uploaded_file
                )
            )

            detection = detect_dataset(
                list(
                    dataframe.columns
                )
            )

            st.success(
                describe_detection(
                    detection
                )
            )

            c1, c2, c3, c4 = (
                st.columns(4)
            )

            c1.metric(
                "Rows",
                f"{len(dataframe):,}",
            )

            c2.metric(
                "Source Columns",
                len(
                    dataframe.columns
                ),
            )

            c3.metric(
                "Mapped Fields",
                len(
                    detection
                    .matched_fields
                ),
            )

            c4.metric(
                "Detection Confidence",
                f"{detection.confidence:.0f}%",
            )

            st.divider()

            left, right = st.columns(
                [1.15, 1]
            )

            with left:

                st.subheader(
                    "Schema Mapping"
                )

                mapping_rows = []

                for source_column in (
                    dataframe.columns
                ):

                    canonical = (
                        detection
                        .column_mapping
                        .get(
                            source_column
                        )
                    )

                    mapping_rows.append(
                        {
                            "Source column": (
                                source_column
                            ),
                            "Canonical field": (
                                canonical
                                if canonical
                                else "Unmapped"
                            ),
                            "Status": (
                                "Mapped"
                                if canonical
                                else "Review"
                            ),
                        }
                    )

                st.dataframe(
                    pd.DataFrame(
                        mapping_rows
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            with right:

                st.subheader(
                    "Intelligence Impact"
                )

                with st.container(
                    border=True
                ):

                    st.caption(
                        "DETECTED SYSTEM"
                    )

                    st.markdown(
                        "### "
                        + pretty_enum(
                            detection
                            .category
                            .value
                        )
                    )

                    st.write(
                        "Detection confidence: "
                        f"**{detection.confidence:.0f}%**"
                    )

                with st.container(
                    border=True
                ):

                    st.caption(
                        "CAPABILITIES THIS DATA SUPPORTS"
                    )

                    for capability in (
                        detection
                        .unlocked_capabilities
                    ):

                        st.write(
                            "✓ "
                            + capability_name(
                                capability
                            )
                        )

                with st.container(
                    border=True
                ):

                    st.caption(
                        "MISSING CANONICAL FIELDS"
                    )

                    if (
                        detection
                        .missing_fields
                    ):

                        for field in (
                            detection
                            .missing_fields
                        ):

                            st.write(
                                "○ "
                                + pretty_enum(
                                    field
                                )
                            )

                    else:

                        st.success(
                            "Canonical schema coverage complete."
                        )

            st.divider()

            st.subheader(
                "Preview"
            )

            st.dataframe(
                dataframe.head(
                    25
                ),
                use_container_width=True,
            )

            c1, c2 = st.columns(
                [1, 3]
            )

            with c1:

                import_clicked = (
                    st.button(
                        "Import & Recalculate",
                        type="primary",
                        use_container_width=True,
                    )
                )

            with c2:

                st.caption(
                    "Production behaviour would persist the mapped "
                    "dataset, update the business graph and rerun "
                    "affected intelligence engines."
                )

            if import_clicked:

                st.success(
                    (
                        f"{len(dataframe):,} records accepted. "
                        f"{pretty_enum(detection.category.value)} "
                        "intelligence recalculated."
                    )
                )

        except Exception as exc:

            st.error(
                "Unable to process dataset: "
                f"{exc}"
            )


# ==========================================================
# INTEGRATIONS
# ==========================================================

elif page == "Integrations":

    render_page_header(
        "Connected Systems",
        "The OS gets smarter as the data graph grows.",
        (
            "A decision layer above existing operational systems, "
            "not a replacement for them."
        ),
    )

    c1, c2, c3 = (
        st.columns(3)
    )

    active_count = sum(
        1
        for source
        in integration_sources
        if source.status
        in {
            IntegrationStatus.CONNECTED,
            IntegrationStatus.SIMULATED,
        }
    )

    c1.metric(
        "Active / simulated sources",
        active_count,
    )

    c2.metric(
        "Intelligence coverage",
        f"{coverage.overall_score:.0f}%",
    )

    c3.metric(
        "Capabilities unlocked",
        len(
            coverage
            .unlocked_capabilities
        ),
    )

    st.write("")

    filter_option = (
        st.selectbox(
            "Show systems",
            [
                "All",
                "Active / Simulated",
                "Not Connected",
            ],
        )
    )

    visible_sources = (
        integration_sources
    )

    if (
        filter_option
        == "Active / Simulated"
    ):

        visible_sources = [
            source
            for source
            in integration_sources
            if source.status
            in {
                IntegrationStatus.CONNECTED,
                IntegrationStatus.SIMULATED,
            }
        ]

    elif (
        filter_option
        == "Not Connected"
    ):

        visible_sources = [
            source
            for source
            in integration_sources
            if source.status
            in {
                IntegrationStatus.READY,
                IntegrationStatus.NOT_CONNECTED,
            }
        ]

    for source in (
        visible_sources
    ):

        with st.container(
            border=True
        ):

            top1, top2, top3 = (
                st.columns(
                    [3, 1, 1]
                )
            )

            with top1:

                st.subheader(
                    source.name
                )

                st.caption(
                    pretty_enum(
                        source
                        .category
                        .value
                    )
                )

            with top2:

                st.metric(
                    "Coverage",
                    f"{source.coverage_pct:.0f}%",
                )

            with top3:

                st.caption(
                    status_text(
                        source.status
                    )
                )

                st.caption(
                    source.last_sync
                )

            st.write(
                source.description
            )

            if (
                source.capabilities
            ):

                st.markdown(
                    "**Intelligence enabled**"
                )

                capability_cols = (
                    st.columns(
                        min(
                            len(
                                source
                                .capabilities
                            ),
                            4,
                        )
                    )
                )

                for (
                    index,
                    capability,
                ) in enumerate(
                    source.capabilities
                ):

                    with capability_cols[
                        index
                        % len(
                            capability_cols
                        )
                    ]:

                        st.caption(
                            "✓ "
                            + capability_name(
                                capability
                            )
                        )

            if (
                source.status
                == IntegrationStatus.NOT_CONNECTED
            ):

                st.button(
                    "Configure connection",
                    key=(
                        "connect_"
                        + source.source_id
                    ),
                )

    st.divider()

    st.subheader(
        "Capability Map"
    )

    unlocked_col, locked_col = (
        st.columns(2)
    )

    with unlocked_col:

        st.markdown(
            "### Available"
        )

        for capability in (
            coverage
            .unlocked_capabilities
        ):

            st.write(
                "✓ "
                + capability_name(
                    capability
                )
            )

    with locked_col:

        st.markdown(
            "### Needs more data"
        )

        for capability in (
            coverage
            .locked_capabilities
        ):

            st.write(
                "○ "
                + capability_name(
                    capability
                )
            )


# ==========================================================
# SAFETY FALLBACK
# ==========================================================

else:

    render_page_header(
        "CARS24 Intelligence OS",
        "Environment unavailable",
        (
            "This navigation route has not been configured "
            "correctly."
        ),
    )

    st.warning(
        "Please select another operating environment."
    )


# ==========================================================
# FOOTER
# ==========================================================

st.write("")
st.write("")

st.caption(
    "CARS24 AUSTRALIA INTELLIGENCE OS • "
    "Independent builder prototype • "
    "Synthetic operating data • "
    "No confidential CARS24 systems or data."
)
