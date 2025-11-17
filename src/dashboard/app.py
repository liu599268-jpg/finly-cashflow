"""
Finly Dashboard - Main Application
Interactive web dashboard for cash flow forecasting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.forecasting import ForecastEngine, Transaction, TransactionType, CashFlowCategory, HistoricalData
from src.quickbooks import QuickBooksClient, QuickBooksTransformer


# Page configuration
st.set_page_config(
    page_title="Finly - Cash Flow Forecasting",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .warning {
        color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main dashboard application"""

    # Header
    st.markdown('<h1 class="main-header">💰 Finly - AI-Powered Cash Flow Forecasting</h1>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/FFFFFF?text=FINLY", use_column_width=True)
        st.markdown("---")

        # Navigation
        page = st.radio(
            "Navigation",
            ["Dashboard", "Forecast", "Scenarios", "Settings"],
            index=0
        )

        st.markdown("---")

        # QuickBooks connection status
        st.subheader("QuickBooks")
        qb_connected = st.session_state.get('qb_connected', False)

        if qb_connected:
            st.success("✅ Connected")
            if st.button("Disconnect"):
                st.session_state['qb_connected'] = False
                st.rerun()
        else:
            st.warning("⚠️ Not Connected")
            if st.button("Connect to QuickBooks"):
                st.session_state['qb_connected'] = True
                st.success("Connected! (Demo mode)")
                st.rerun()

        st.markdown("---")

        # Data info
        if 'transactions' in st.session_state:
            st.metric("Transactions Loaded", len(st.session_state['transactions']))

    # Main content based on page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Forecast":
        show_forecast()
    elif page == "Scenarios":
        show_scenarios()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Show main dashboard overview"""

    st.header("📊 Dashboard Overview")

    # Demo data or load from session
    if 'forecast' not in st.session_state:
        # Generate demo forecast
        with st.spinner("Generating demo forecast..."):
            from utils.sample_data import SampleDataGenerator
            generator = SampleDataGenerator()
            historical = generator.generate_transactions(num_weeks=52)

            engine = ForecastEngine()
            forecast = engine.generate_forecast(
                historical_data=historical,
                company_name="Demo Company",
                weeks_ahead=13
            )

            st.session_state['forecast'] = forecast
            st.session_state['historical'] = historical

    forecast = st.session_state['forecast']

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        current_balance = forecast.current_balance
        st.metric(
            "Current Cash Balance",
            f"${current_balance:,.0f}",
            delta=None
        )

    with col2:
        final_balance = forecast.get_final_balance()
        change = final_balance - current_balance
        change_pct = (change / abs(current_balance)) * 100 if current_balance != 0 else 0
        st.metric(
            "13-Week Projected Balance",
            f"${final_balance:,.0f}",
            delta=f"{change:+,.0f} ({change_pct:+.1f}%)"
        )

    with col3:
        burn_rate = forecast.get_average_weekly_burn()
        if burn_rate > 0:
            st.metric(
                "Weekly Burn Rate",
                f"${burn_rate:,.0f}",
                delta="Burning cash",
                delta_color="inverse"
            )
        else:
            st.metric(
                "Weekly Profit",
                f"${abs(burn_rate):,.0f}",
                delta="Generating cash",
                delta_color="normal"
            )

    with col4:
        weeks_until_zero = forecast.get_weeks_until_zero()
        if weeks_until_zero:
            st.metric(
                "Cash Runway",
                f"{weeks_until_zero} weeks",
                delta="⚠️ Critical",
                delta_color="inverse"
            )
        else:
            st.metric(
                "Cash Runway",
                "Sustainable",
                delta="✅ Healthy",
                delta_color="normal"
            )

    # Cash flow chart
    st.subheader("13-Week Cash Flow Projection")

    dates = [point.date for point in forecast.forecast_points]
    balances = [point.predicted_balance for point in forecast.forecast_points]
    upper_bounds = [point.confidence_upper for point in forecast.forecast_points]
    lower_bounds = [point.confidence_lower for point in forecast.forecast_points]

    fig = go.Figure()

    # Add confidence interval
    fig.add_trace(go.Scatter(
        x=dates + dates[::-1],
        y=upper_bounds + lower_bounds[::-1],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval'
    ))

    # Add projected balance line
    fig.add_trace(go.Scatter(
        x=dates,
        y=balances,
        name='Projected Balance',
        line=dict(color='#1f77b4', width=3)
    ))

    # Add current balance marker
    fig.add_trace(go.Scatter(
        x=[datetime.now()],
        y=[current_balance],
        mode='markers',
        name='Current Balance',
        marker=dict(size=12, color='green')
    ))

    fig.update_layout(
        title="Cash Balance Projection with Confidence Interval",
        xaxis_title="Date",
        yaxis_title="Cash Balance ($)",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # Weekly breakdown table
    st.subheader("Weekly Breakdown")

    weekly_data = []
    for i, point in enumerate(forecast.forecast_points[:13]):
        weekly_data.append({
            'Week': i + 1,
            'Date': point.date.strftime('%Y-%m-%d'),
            'Inflows': f"${point.predicted_inflows:,.0f}",
            'Outflows': f"${point.predicted_outflows:,.0f}",
            'Net Flow': f"${point.net_cash_flow:,.0f}",
            'Ending Balance': f"${point.predicted_balance:,.0f}"
        })

    df = pd.DataFrame(weekly_data)
    st.dataframe(df, use_container_width=True)


def show_forecast():
    """Show detailed forecast page"""
    st.header("🔮 Generate New Forecast")

    st.info("Configure and generate a new 13-week cash flow forecast")

    col1, col2 = st.columns(2)

    with col1:
        forecast_weeks = st.slider("Forecast Horizon (weeks)", 4, 26, 13)
        use_ensemble = st.checkbox("Use Ensemble Models", value=False)

    with col2:
        start_date = st.date_input("Historical Data Start Date",
                                   datetime.now() - timedelta(days=365))
        end_date = st.date_input("Historical Data End Date", datetime.now())

    if st.button("Generate Forecast", type="primary"):
        with st.spinner("Generating forecast..."):
            # Demo: Generate forecast
            from utils.sample_data import SampleDataGenerator
            generator = SampleDataGenerator()
            historical = generator.generate_transactions(num_weeks=52)

            engine = ForecastEngine(use_ensemble=use_ensemble)
            forecast = engine.generate_forecast(
                historical_data=historical,
                company_name="Demo Company",
                weeks_ahead=forecast_weeks
            )

            st.session_state['forecast'] = forecast
            st.success(f"✅ {forecast_weeks}-week forecast generated successfully!")
            st.rerun()


def show_scenarios():
    """Show scenario analysis page"""
    st.header("📈 Scenario Analysis")

    st.info("Compare different business scenarios and their impact on cash flow")

    # Scenario configuration
    st.subheader("Define Scenarios")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Best Case**")
        revenue_growth_high = st.number_input("Revenue Growth (%)", value=25.0, key="high")
        expense_reduction_high = st.number_input("Expense Reduction (%)", value=5.0, key="high_exp")

    with col2:
        st.markdown("**Base Case**")
        revenue_growth_base = st.number_input("Revenue Growth (%)", value=10.0, key="base")
        expense_reduction_base = st.number_input("Expense Reduction (%)", value=0.0, key="base_exp")

    with col3:
        st.markdown("**Worst Case**")
        revenue_growth_low = st.number_input("Revenue Growth (%)", value=-10.0, key="low")
        expense_increase_low = st.number_input("Expense Increase (%)", value=10.0, key="low_exp")

    if st.button("Run Scenario Analysis", type="primary"):
        st.success("Scenario analysis complete! (Demo)")

        # Show comparison chart
        st.subheader("Scenario Comparison")

        # Demo data
        weeks = list(range(1, 14))
        best_case = [500000 + (i * 15000) for i in weeks]
        base_case = [500000 + (i * 10000) for i in weeks]
        worst_case = [500000 + (i * 5000) for i in weeks]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=weeks, y=best_case, name='Best Case',
                                line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x=weeks, y=base_case, name='Base Case',
                                line=dict(color='blue', width=2)))
        fig.add_trace(go.Scatter(x=weeks, y=worst_case, name='Worst Case',
                                line=dict(color='red', width=2)))

        fig.update_layout(
            title="13-Week Cash Flow by Scenario",
            xaxis_title="Week",
            yaxis_title="Cash Balance ($)",
            hovermode='x unified',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)


def show_settings():
    """Show settings page"""
    st.header("⚙️ Settings")

    tab1, tab2, tab3 = st.tabs(["QuickBooks", "Forecasting", "About"])

    with tab1:
        st.subheader("QuickBooks Integration")

        client_id = st.text_input("Client ID", type="password")
        client_secret = st.text_input("Client Secret", type="password")
        company_id = st.text_input("Company/Realm ID")
        environment = st.selectbox("Environment", ["Sandbox", "Production"])

        if st.button("Save QuickBooks Settings"):
            st.success("Settings saved!")

    with tab2:
        st.subheader("Forecasting Settings")

        default_horizon = st.slider("Default Forecast Horizon (weeks)", 4, 26, 13)
        confidence_level = st.slider("Confidence Level (%)", 70, 95, 80)

        st.checkbox("Enable Ensemble Models", value=False)
        st.checkbox("Include Seasonality", value=True)

        if st.button("Save Forecasting Settings"):
            st.success("Settings saved!")

    with tab3:
        st.subheader("About Finly")
        st.markdown("""
        **Finly** is an AI-powered cash flow forecasting application for SMBs.

        **Version:** 1.0.0
        **Built with:** Python, Streamlit, scikit-learn, Prophet

        **Features:**
        - QuickBooks Online integration
        - 13-week AI/ML forecasts
        - Scenario planning
        - Interactive dashboards

        © 2025 Finly. All rights reserved.
        """)


if __name__ == "__main__":
    main()
