"""Streamlit interface for the CrewAI order management workflow."""

import os

import streamlit as st

from order_management.data import assess_escalation, get_order
from order_management.local_resolution import resolve_locally


st.set_page_config(
    page_title="Order Support | Smart Commerce",
    page_icon="📦",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 10% 0%, rgba(223, 217, 255, .55), transparent 36%),
            #f7f8fc;
        color: #20243a;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .brand-row {
        display: flex;
        align-items: center;
        gap: .7rem;
        margin-bottom: 1.2rem;
        color: #292644;
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: -.02em;
    }
    .brand-icon {
        display: inline-grid;
        width: 2.4rem;
        height: 2.4rem;
        place-items: center;
        border-radius: .8rem;
        background: linear-gradient(135deg, #7758e8, #a54ee5);
        box-shadow: 0 7px 18px rgba(119, 88, 232, .24);
        color: white;
        font-size: 1.2rem;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.2rem 2.4rem;
        border-radius: 1.4rem;
        background: linear-gradient(115deg, #4e43b8 0%, #7350d8 56%, #a550d0 100%);
        box-shadow: 0 18px 42px rgba(83, 65, 174, .2);
        color: white;
    }
    .hero:after {
        position: absolute;
        top: -5.8rem;
        right: -2.4rem;
        width: 17rem;
        height: 17rem;
        border: 1px solid rgba(255,255,255,.17);
        border-radius: 50%;
        box-shadow: 0 0 0 2rem rgba(255,255,255,.045), 0 0 0 4rem rgba(255,255,255,.035);
        content: "";
    }
    .hero-kicker {
        margin-bottom: .6rem;
        color: #e8e1ff;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .hero h1 {
        margin: 0;
        color: white;
        font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 800;
        letter-spacing: -.045em;
        line-height: 1.1;
    }
    .hero-copy {
        max-width: 37rem;
        margin-top: .8rem;
        color: #f0edff;
        font-size: 1.04rem;
        line-height: 1.65;
    }
    .mode-badge {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        margin-top: 1.15rem;
        padding: .4rem .75rem;
        border: 1px solid rgba(255,255,255,.26);
        border-radius: 999px;
        background: rgba(255,255,255,.13);
        color: white;
        font-size: .8rem;
        font-weight: 600;
    }
    .section-title {
        margin: 1.9rem 0 .25rem;
        color: #27243f;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -.025em;
    }
    .section-copy {
        margin: 0 0 1rem;
        color: #70738a;
        font-size: .96rem;
    }
    .sample-label {
        margin: .3rem 0 .55rem;
        color: #74758a;
        font-size: .82rem;
        font-weight: 700;
    }
    .info-card {
        min-height: 6.3rem;
        padding: 1rem 1.1rem;
        border: 1px solid #e9e7f4;
        border-radius: 1rem;
        background: rgba(255,255,255,.88);
    }
    .info-card-title {
        margin-bottom: .35rem;
        color: #34314f;
        font-size: .9rem;
        font-weight: 800;
    }
    .info-card-copy {
        color: #73758a;
        font-size: .82rem;
        line-height: 1.5;
    }
    div[data-testid="stForm"] {
        padding: 1.35rem;
        border: 1px solid #e9e7f4;
        border-radius: 1rem;
        background: rgba(255,255,255,.94);
        box-shadow: 0 10px 30px rgba(51, 43, 103, .06);
    }
    .stTextInput label, .stTextArea label {
        color: #34314f !important;
        font-weight: 700 !important;
    }
    .stTextInput input, .stTextArea textarea {
        border-color: #dedced !important;
        border-radius: .7rem !important;
        background: #fcfcff !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8066df !important;
        box-shadow: 0 0 0 1px #8066df !important;
    }
    .stButton > button, .stFormSubmitButton > button {
        min-height: 2.65rem;
        border: 1px solid #e3e0f1;
        border-radius: .7rem;
        background: white;
        color: #5143a5;
        font-weight: 700;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        border-color: #b8a9f1;
        color: #45349c;
        box-shadow: 0 5px 14px rgba(92, 69, 177, .12);
        transform: translateY(-1px);
    }
    .stFormSubmitButton > button {
        border: 0;
        background: linear-gradient(100deg, #6553cd, #8f4fd0);
        color: white;
    }
    .stFormSubmitButton > button:hover {
        border: 0;
        background: linear-gradient(100deg, #5543bd, #8040c2);
        color: white;
    }
    .result-card {
        padding: 1.25rem 1.4rem;
        border: 1px solid #e8e5f2;
        border-radius: 1rem;
        background: white;
        box-shadow: 0 10px 30px rgba(51, 43, 103, .06);
    }
    .result-eyebrow {
        margin-bottom: .3rem;
        color: #7463c4;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
    }
    .result-title {
        margin: 0 0 .5rem;
        color: #27243f;
        font-size: 1.2rem;
        font-weight: 800;
    }
    .footer-note {
        margin-top: 1.8rem;
        color: #87889a;
        font-size: .78rem;
        text-align: center;
    }
    @media (max-width: 640px) {
        .block-container { padding: 1rem 1rem 2rem; }
        .hero { padding: 1.6rem 1.3rem; border-radius: 1rem; }
        .hero-copy { font-size: .94rem; }
        div[data-testid="stForm"] { padding: .9rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
mode_label = (
    "AI-assisted support enabled"
    if api_key_configured
    else "Instant sample-data support · No API key needed"
)

st.markdown(
    """
    <div class="brand-row">
      <span class="brand-icon">📦</span>
      <span>Smart Commerce <span style="color:#8a829f;font-weight:500">· Support</span></span>
    </div>
    <section class="hero">
      <div class="hero-kicker">Your order, taken care of</div>
      <h1>How can we help today?</h1>
      <div class="hero-copy">
        Get a clear update on your order, delivery, and product availability.
        Enter your order number and tell us what you need.
      </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="mode-badge">✦ {mode_label}</div></section>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Let’s look up your order</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Choose a sample order or enter your order number below.</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="sample-label">Try a sample order</div>', unsafe_allow_html=True)
sample_columns = st.columns(4)
sample_orders = (
    ("ORD1025", "Delayed delivery"),
    ("ORD1026", "Delivered"),
    ("ORD1027", "Item availability"),
    ("ORD1028", "Delayed delivery"),
)
for column, (sample_id, scenario) in zip(sample_columns, sample_orders):
    with column:
        if st.button(
            f"{sample_id}  ·  {scenario}",
            key=f"sample_{sample_id}",
            use_container_width=True,
        ):
            st.session_state["order_id"] = sample_id
            st.session_state["customer_question"] = (
                "Can you check my order status and estimated delivery?"
            )

with st.form("order_question"):
    order_id = st.text_input(
        "Order number",
        placeholder="For example, ORD1025",
        help="Find your order number in your confirmation email.",
        key="order_id",
    )
    customer_question = st.text_area(
        "What can we help with?",
        placeholder="For example, “My order is late. Can you check its status?”",
        help="Include a little detail so we can give you a more useful answer.",
        height=110,
        key="customer_question",
    )
    submitted = st.form_submit_button(
        "✨  Check my order",
        type="primary",
        use_container_width=True,
    )

if "support_result" not in st.session_state:
    st.session_state["support_result"] = None

if submitted:
    st.session_state["support_result"] = None
    if not order_id.strip() or not customer_question.strip():
        st.session_state["support_result"] = {
            "kind": "validation",
            "message": "Please enter both your order number and a question.",
        }
    else:
        try:
            order = get_order(order_id)
            with st.spinner("Checking your order details…"):
                if api_key_configured:
                    from order_management.crew import ResolutionOutput, build_order_crew

                    crew = build_order_crew()
                    result = crew.kickoff(
                        inputs={
                            "order_id": order["order_id"],
                            "customer_question": customer_question.strip(),
                        }
                    )
                    output = result.tasks_output[-1].pydantic
                    if not isinstance(output, ResolutionOutput):
                        raise RuntimeError(
                            "The Resolution Agent did not return a valid structured result."
                        )
                else:
                    output = resolve_locally(order["order_id"], customer_question.strip())

            required_escalation = assess_escalation(
                customer_question, order["tracking_status"]
            )
            escalated = output.escalated or required_escalation["required"]
            reason = (
                required_escalation["reason"]
                if required_escalation["required"]
                else output.escalation_reason
            )
            st.session_state["support_result"] = {
                "kind": "escalation" if escalated else "response",
                "order_id": order["order_id"],
                "product_name": order["product_name"],
                "tracking_status": order["tracking_status"],
                "estimated_delivery": order["estimated_delivery"],
                "reason": reason,
                "response": output.customer_response,
                "internal_summary": output.internal_summary,
            }
        except LookupError as error:
            st.session_state["support_result"] = {
                "kind": "error",
                "message": str(error),
            }
        except Exception as error:
            st.session_state["support_result"] = {
                "kind": "error",
                "message": f"Unable to process this request: {error}",
            }

support_result = st.session_state["support_result"]
if support_result:
    st.markdown('<div class="section-title">Your order update</div>', unsafe_allow_html=True)
    if support_result["kind"] in ("validation", "error"):
        st.error(support_result["message"])
    else:
        if support_result["kind"] == "escalation":
            st.warning(
                "This request needs help from a human support representative. "
                "No refund, replacement, or other account change has been made."
            )
        else:
            st.success("We found your order. Here’s the latest update.")

        details = st.columns(3)
        with details[0]:
            st.markdown(
                f"""<div class="info-card">
                <div class="info-card-title">📦 {support_result['product_name']}</div>
                <div class="info-card-copy">Order {support_result['order_id']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with details[1]:
            st.markdown(
                f"""<div class="info-card">
                <div class="info-card-title">🚚 {support_result['tracking_status']}</div>
                <div class="info-card-copy">Latest tracking status</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with details[2]:
            st.markdown(
                f"""<div class="info-card">
                <div class="info-card-title">📅 {support_result['estimated_delivery']}</div>
                <div class="info-card-copy">Estimated delivery</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="result-card"><div class="result-eyebrow">Your support update</div>'
            '<div class="result-title">Here’s what we found</div></div>',
            unsafe_allow_html=True,
        )
        st.write(support_result["response"])
        if support_result["kind"] == "escalation":
            if support_result["reason"]:
                st.caption(f"Follow-up reason: {support_result['reason'].replace('_', ' ')}")
            if support_result["internal_summary"]:
                with st.expander("Support handoff details"):
                    st.write(support_result["internal_summary"])

st.markdown(
    """
    <div class="section-title">Simple, helpful support</div>
    """,
    unsafe_allow_html=True,
)
help_columns = st.columns(3)
help_cards = (
    ("🔎  Order updates", "Check delivery status and estimated arrival in one place."),
    ("📦  Product availability", "See stock information and possible alternatives."),
    ("🙋  Human follow-up", "Sensitive requests are flagged for a support representative."),
)
for column, (title, copy) in zip(help_columns, help_cards):
    with column:
        st.markdown(
            f"""<div class="info-card">
            <div class="info-card-title">{title}</div>
            <div class="info-card-copy">{copy}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown(
    '<div class="footer-note">Smart Commerce Support · Order information is based on available records.</div>',
    unsafe_allow_html=True,
)
