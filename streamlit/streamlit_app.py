
import streamlit as st
import requests
import re

# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Travel Intelligence Assistant",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Travel Intelligence Assistant")

st.caption(
    "AI-powered commercial, customer, financial "
    "and loyalty analytics"
)

# --------------------------------------------------
# 2. Snowflake connection
# --------------------------------------------------

conn = st.connection("snowflake")
session = conn.session()

# --------------------------------------------------
# 3. Semantic views
# --------------------------------------------------

SEMANTIC_VIEWS = [
    "TRAVEL_DEV_DB.SEMANTIC.COMMERCIAL_ANALYTICS",
    "TRAVEL_DEV_DB.SEMANTIC.CUSTOMER_ANALYTICS",
    "TRAVEL_DEV_DB.SEMANTIC.FINANCIAL_ANALYTICS",
    "TRAVEL_DEV_DB.SEMANTIC.LOYALTY_ANALYTICS"
]

# --------------------------------------------------
# 4. Session state
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_messages" not in st.session_state:
    st.session_state.api_messages = []

# --------------------------------------------------
# 5. Cortex Analyst API
# --------------------------------------------------

def ask_analyst(messages):

    host = session.connection.host
    token = session.connection.rest.token

    url = f"https://{host}/api/v2/cortex/analyst/message"

    headers = {
        "Authorization": f'Snowflake Token="{token}"',
        "Content-Type": "application/json"
    }

    messages = [
        {
            **message,
            "content": [
                {
                    **item,
                    "text": item["text"] + (
                        "\nPreserve the requested aggregation level. "
                        "For total metrics, return a single aggregate row "
                        "unless a breakdown is explicitly requested. "
                        "For follow-up questions, preserve the previous "
                        "metric, filters and aggregation level unless "
                        "the user requests a change. "
                        "Include reporting dates only when appropriate "
                        "and without changing the aggregation level. "
                        "Use unique column aliases."
                    )
                }
                if message["role"] == "user"
                and item["type"] == "text"
                and i == len(messages) - 1
                else item
                for item in message["content"]
            ]
        }
        for i, message in enumerate(messages)
    ]

    payload = {
        "messages": messages,
        "semantic_models": [
            {"semantic_view": view}
            for view in SEMANTIC_VIEWS
        ],
        "stream": False
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()

# --------------------------------------------------
# 6. Execute generated SQL
# --------------------------------------------------

def execute_sql(statement):

    # Remove trailing whitespace and semicolons
    statement = statement.strip().rstrip(";").strip()

    # Basic guardrail for analytical queries
    if not re.match(
        r"^\s*(SELECT|WITH)\b",
        statement,
        re.IGNORECASE
    ):
        raise ValueError("Only analytical queries are allowed.")

    return session.sql(statement).limit(1000).to_pandas()

# --------------------------------------------------
# 7. Display assistant response
# --------------------------------------------------


def format_metric(value, column_name):

    name = column_name.upper()

    # Percentage metrics stored as decimal fractions
    if any(keyword in name for keyword in [
        "RATE",
        "PERCENTAGE",
        "PCT",
        "ROI"
    ]):
        return f"{value:.2%}"

    # Ratios
    elif "RATIO" in name:
        return f"{value:,.2f}"

    # Counts and loyalty points
    elif any(keyword in name for keyword in [
        "COUNT",
        "POINTS",
        "CUSTOMERS",
        "BOOKINGS",
        "TRAVELLERS",
        "ROOM_NIGHTS",
        "MEMBERS"
    ]):
        return f"{value:,.0f}"

    # Explicit AUD currency metrics
    elif "AUD" in name or "SALES" in name:
        return f"${value:,.2f}"

    # Other monetary metrics
    elif any(keyword in name for keyword in [
        "SALES",
        "REVENUE",
        "MARGIN",
        "COST",
        "PAYMENT",
        "REFUND",
        "DISCOUNT",
        "SPEND",
        "VALUE",
        "CASH"
    ]):
        return f"{value:,.2f}"

    # Default numeric formatting
    else:
        return f"{value:,.2f}"


def display_results(df):

    df = df.copy()

    # Make duplicate column names unique
    seen = {}
    new_columns = []

    for col in df.columns:
        seen[col] = seen.get(col, 0) + 1

        if seen[col] == 1:
            new_columns.append(col)
        else:
            new_columns.append(
                f"{col}_{seen[col]}"
            )

    df.columns = new_columns

    if df.empty:
        st.info("No matching records found.")
        return

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    # Single-row results: KPI cards
    if len(df) == 1 and numeric_cols:

        columns = st.columns(min(len(numeric_cols), 3))

        for i, col in enumerate(numeric_cols):

            value = df.iloc[0][col]
            label = col.replace("_", " ").title()

            with columns[i % len(columns)]:
                st.metric(label, format_metric(value, col))

    # Multi-row results: automatic charts
    elif len(df) > 1 and numeric_cols:

        date_cols = [
            col for col in df.columns
            if any(
                keyword in col.upper()
                for keyword in ["DATE", "MONTH", "YEAR"]
            )
        ]

        category_cols = [
            col for col in df.columns
            if col not in numeric_cols
            and col not in date_cols
        ]

        # Time series
        if date_cols:

            chart_df = df.sort_values(date_cols[0])

            st.line_chart(
                chart_df.set_index(date_cols[0])[
                    numeric_cols[0]
                ]
            )

        # Category comparison
        elif category_cols and len(df) <= 30:

            st.bar_chart(
                df.set_index(category_cols[0])[
                    numeric_cols[0]
                ]
            )

    # Create a formatted copy for display
    display_df = df.copy()
    
    for col in numeric_cols:
        display_df[col] = display_df[col].apply(
            lambda value: format_metric(value, col)
            if value == value and value is not None
            else ""
        )

    # Display formatted result table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def display_response(message):

    if message.get("domain"):
        st.caption(f"Data domain: {message['domain']}")

    for item in message.get("content", []):

        content_type = item.get("type")

        if content_type == "text":
            st.markdown(item["text"])

        elif content_type == "sql":

            with st.expander("View generated SQL"):
                st.code(item["statement"], language="sql")

            if "data" in item:
                display_results(item["data"])

                st.caption(
                    f"{len(item['data'])} rows returned "
                    "(maximum 1,000 displayed)"
                )

            if "error" in item:
                st.error(item["error"])

        elif content_type == "suggestions":

            st.markdown("**Suggested questions:**")

            for suggestion in item.get("suggestions", []):
                st.markdown(f"- {suggestion}")

    for warning in message.get("warnings", []):
        st.warning(str(warning))

# --------------------------------------------------
# 8. Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Travel Analytics")

    st.markdown("**Available business domains**")

    st.markdown("""
    - Commercial Analytics
    - Customer Analytics
    - Financial Analytics
    - Loyalty Analytics
    """)

    st.divider()

    st.caption("Environment: DEV")
    st.caption("Powered by Snowflake Cortex Analyst")

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.api_messages = []
        st.rerun()

# --------------------------------------------------
# 9. Display conversation history
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":
            st.markdown(message["text"])

        else:
            display_response(message)

# --------------------------------------------------
# 10. Process new questions
# --------------------------------------------------

question = st.chat_input(
    "Ask a question about your travel business..."
)

if question:

    user_message = {
        "role": "user",
        "text": question
    }

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(question)

    api_user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": question
            }
        ]
    }

    with st.chat_message("assistant"):

        try:

            with st.spinner("Analysing your question..."):

                response = ask_analyst(
                    st.session_state.api_messages
                    + [api_user_message]
                )

            selection = response.get(
                "semantic_model_selection", {}
            )

            identifier = selection.get("identifier", {})

            selected_view = (
                identifier.get("semantic_view") or "Unknown"
            )

            domain = (
                selected_view.split(".")[-1]
                .replace("_", " ")
                .title()
            )

            analyst_message = response["message"]

            processed_content = []

            for item in analyst_message.get("content", []):

                item = item.copy()

                if item.get("type") == "sql":

                    try:
                        with st.spinner("Executing SQL..."):
                            item["data"] = execute_sql(
                                item["statement"]
                            )

                    except Exception as e:
                        item["error"] = str(e)

                processed_content.append(item)

            assistant_message = {
                "role": "assistant",
                "domain": domain,
                "content": processed_content,
                "warnings": response.get("warnings", [])
            }

            st.session_state.api_messages.extend([
                api_user_message,
                analyst_message
            ])

            st.session_state.messages.append(
                assistant_message
            )

            display_response(assistant_message)

        except Exception as e:

            st.error(f"Unable to process question: {e}")
