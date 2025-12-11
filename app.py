import streamlit as st
import yfinance as yf
import ephem
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import time

# Page configuration
st.set_page_config(
    page_title="MoonCrypto Dashboard",
    page_icon="🌝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #FFD700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
    }
    .verdict-box {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .verdict-green {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .verdict-red {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
    .story-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #6c757d;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_bitcoin_data(period="6mo"):
    """Fetch Bitcoin price data using yfinance"""
    try:
        btc = yf.Ticker("BTC-USD")
        data = btc.history(period=period)
        if data.empty:
            st.error("No Bitcoin data retrieved. Please check your internet connection.")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching Bitcoin data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def calculate_moon_phases(start_date, end_date):
    """Calculate moon phase data using ephem"""
    try:
        moon_data = []
        current_date = start_date
        
        while current_date <= end_date:
            moon = ephem.Moon()
            moon.compute(current_date)
            
            # Calculate illumination percentage
            illumination = moon.moon_phase * 100
            
            # Determine if it's a full moon (>95% illumination)
            is_full_moon = illumination > 95
            
            moon_data.append({
                'Date': current_date,
                'Illumination': illumination,
                'IsFullMoon': is_full_moon
            })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(moon_data)
    except Exception as e:
        st.error(f"Error calculating moon phases: {str(e)}")
        return None

def merge_datasets(bitcoin_df, moon_df):
    """Merge Bitcoin and moon phase datasets"""
    try:
        # Reset index to make Date a column for Bitcoin data
        bitcoin_df = bitcoin_df.reset_index()
        bitcoin_df['Date'] = pd.to_datetime(bitcoin_df['Date']).dt.date
        
        # Convert moon data dates to same format
        moon_df['Date'] = pd.to_datetime(moon_df['Date']).dt.date
        
        # Merge datasets on Date
        merged_df = pd.merge(bitcoin_df, moon_df, on='Date', how='inner')
        
        if merged_df.empty:
            st.error("No overlapping dates found between Bitcoin and moon data.")
            return None
            
        return merged_df
    except Exception as e:
        st.error(f"Error merging datasets: {str(e)}")
        return None

def calculate_correlation(bitcoin_prices, moon_illumination):
    """Calculate Pearson correlation coefficient"""
    try:
        if len(bitcoin_prices) < 2 or len(moon_illumination) < 2:
            return 0.0, 1.0
        
        correlation, p_value = pearsonr(bitcoin_prices, moon_illumination)
        return correlation, p_value
    except Exception as e:
        st.error(f"Error calculating correlation: {str(e)}")
        return 0.0, 1.0

def create_dual_axis_chart(merged_df):
    """Create dual-axis chart with Bitcoin prices and moon illumination"""
    try:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add Bitcoin price line (gold)
        fig.add_trace(
            go.Scatter(
                x=merged_df['Date'],
                y=merged_df['Close'],
                mode='lines',
                name='Bitcoin Price',
                line=dict(color='gold', width=2),
                hovertemplate='<b>Bitcoin Price</b><br>Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
            ),
            secondary_y=False,
        )
        
        # Add Moon illumination line (silver)
        fig.add_trace(
            go.Scatter(
                x=merged_df['Date'],
                y=merged_df['Illumination'],
                mode='lines',
                name='Moon Illumination',
                line=dict(color='silver', width=2),
                hovertemplate='<b>Moon Illumination</b><br>Date: %{x}<br>Illumination: %{y:.1f}%<extra></extra>'
            ),
            secondary_y=True,
        )
        
        # Add full moon markers
        full_moon_data = merged_df[merged_df['IsFullMoon']]
        if not full_moon_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=full_moon_data['Date'],
                    y=full_moon_data['Illumination'],
                    mode='markers',
                    name='Full Moon',
                    marker=dict(color='white', size=10, symbol='circle', 
                               line=dict(color='silver', width=2)),
                    hovertemplate='<b>Full Moon</b><br>Date: %{x}<br>Illumination: %{y:.1f}%<extra></extra>'
                ),
                secondary_y=True,
            )
        
        # Set x-axis title
        fig.update_xaxes(title_text="Date")
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Bitcoin Price (USD)", secondary_y=False, title_font_color="gold")
        fig.update_yaxes(title_text="Moon Illumination (%)", secondary_y=True, title_font_color="silver")
        
        # Update layout
        fig.update_layout(
            title="Bitcoin Price vs Moon Illumination",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None

def create_verdict_box(correlation, p_value):
    """Create verdict box based on correlation"""
    if correlation > 0.1:
        verdict_class = "verdict-green"
        verdict_text = "VERDICT: ASTROLOGY IS REAL? 😱"
    else:
        verdict_class = "verdict-red"
        verdict_text = "VERDICT: JUST COINCIDENCE 📉"
    
    return f"""
    <div class="verdict-box {verdict_class}">
        {verdict_text}<br>
        <small>Correlation: {correlation:.4f} (p-value: {p_value:.4f})</small>
    </div>
    """

def generate_story(correlation, merged_df):
    """Generate dynamic story based on correlation and data"""
    try:
        # Calculate some basic statistics
        btc_change = ((merged_df['Close'].iloc[-1] - merged_df['Close'].iloc[0]) / merged_df['Close'].iloc[0]) * 100
        full_moon_count = merged_df['IsFullMoon'].sum()
        avg_illumination = merged_df['Illumination'].mean()
        
        if correlation > 0.1:
            story = f"""
            🌟 **The Cosmic Connection Revealed!**
            
            Our analysis has uncovered a fascinating correlation of {correlation:.4f} between Bitcoin prices and lunar illumination! 
            Over the analyzed period, Bitcoin {'surged' if btc_change > 0 else 'declined'} by {abs(btc_change):.1f}%, 
            while we observed {full_moon_count} full moon events.
            
            Could it be that the gravitational pull of our celestial neighbor influences not just the tides, 
            but also the volatile seas of cryptocurrency markets? The data suggests there might be more to 
            astrology than meets the eye! 🚀
            
            *Average moon illumination during this period: {avg_illumination:.1f}%*
            """
        elif correlation > 0:
            story = f"""
            🔍 **A Whisper of Cosmic Influence**
            
            While the correlation of {correlation:.4f} between Bitcoin and moon phases is modest, 
            it's not entirely negligible. During our analysis period, Bitcoin {'gained' if btc_change > 0 else 'lost'} 
            {abs(btc_change):.1f}% while we witnessed {full_moon_count} full moon cycles.
            
            Perhaps the moon's influence on markets is subtle, like a gentle tide rather than a tsunami. 
            Or maybe it's just the collective psychology of traders who believe in lunar cycles creating 
            a self-fulfilling prophecy? 🤔
            
            *Average moon illumination: {avg_illumination:.1f}%*
            """
        else:
            story = f"""
            📊 **Science Prevails Over Superstition**
            
            With a correlation of {correlation:.4f}, our data strongly suggests that moon phases have 
            little to no influence on Bitcoin prices. During the analyzed period, Bitcoin 
            {'rose' if btc_change > 0 else 'fell'} by {abs(btc_change):.1f}% across {full_moon_count} full moon events, 
            showing no meaningful pattern.
            
            It appears that market fundamentals, news events, and investor sentiment are far more 
            powerful forces than lunar gravity when it comes to cryptocurrency prices. 
            The stars may guide our dreams, but data guides our investments! 💡
            
            *Average moon illumination: {avg_illumination:.1f}%*
            """
        
        return story
    except Exception as e:
        return f"Error generating story: {str(e)}"

def identify_full_moon_periods(merged_df):
    """Identify periods with full moons"""
    try:
        full_moon_dates = merged_df[merged_df['IsFullMoon']]['Date'].tolist()
        return full_moon_dates
    except Exception as e:
        st.error(f"Error identifying full moon periods: {str(e)}")
        return []

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🌝 MoonCrypto: Do Full Moons Pump Bitcoin?</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("📊 Analysis Controls")
    
    # Date range selection
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo", 
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y"
    }
    
    selected_period = st.sidebar.selectbox(
        "Select Analysis Period:",
        options=list(period_options.keys()),
        index=2  # Default to 6 months
    )
    
    # Analysis button
    if st.sidebar.button("🚀 Analyze Cosmic Correlation", type="primary"):
        with st.spinner("Fetching data from the cosmos... 🌌"):
            
            # Fetch Bitcoin data
            bitcoin_data = fetch_bitcoin_data(period_options[selected_period])
            if bitcoin_data is None:
                st.stop()
            
            # Calculate date range for moon phases
            start_date = bitcoin_data.index.min().date()
            end_date = bitcoin_data.index.max().date()
            
            # Calculate moon phases
            moon_data = calculate_moon_phases(start_date, end_date)
            if moon_data is None:
                st.stop()
            
            # Merge datasets
            merged_data = merge_datasets(bitcoin_data, moon_data)
            if merged_data is None:
                st.stop()
            
            # Calculate correlation
            correlation, p_value = calculate_correlation(merged_data['Close'], merged_data['Illumination'])
            
            # Store results in session state
            st.session_state.merged_data = merged_data
            st.session_state.correlation = correlation
            st.session_state.p_value = p_value
            st.session_state.analysis_complete = True
    
    # Display results if analysis is complete
    if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:
        
        merged_data = st.session_state.merged_data
        correlation = st.session_state.correlation
        p_value = st.session_state.p_value
        
        # Create three columns for metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="📈 Bitcoin Price Change",
                value=f"${merged_data['Close'].iloc[-1]:,.2f}",
                delta=f"{((merged_data['Close'].iloc[-1] - merged_data['Close'].iloc[0]) / merged_data['Close'].iloc[0] * 100):+.1f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="🌙 Full Moon Events",
                value=f"{merged_data['IsFullMoon'].sum()}",
                delta=f"Avg Illumination: {merged_data['Illumination'].mean():.1f}%"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label="📊 Correlation Coefficient",
                value=f"{correlation:.4f}",
                delta=f"p-value: {p_value:.4f}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Verdict Box
        verdict_html = create_verdict_box(correlation, p_value)
        st.markdown(verdict_html, unsafe_allow_html=True)
        
        # Check for full moon periods and trigger confetti
        full_moon_dates = identify_full_moon_periods(merged_data)
        if full_moon_dates and len(full_moon_dates) > 0:
            if st.button("🎉 Celebrate Full Moon Discoveries!"):
                st.balloons()
                st.success(f"🌕 Found {len(full_moon_dates)} full moon events in the data!")
        
        # Interactive Chart
        st.subheader("📈 Interactive Price vs Moon Phase Chart")
        chart = create_dual_axis_chart(merged_data)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Story Section
        st.subheader("📖 The Cosmic Story")
        story = generate_story(correlation, merged_data)
        st.markdown(f'<div class="story-section">{story}</div>', unsafe_allow_html=True)
        
        # Data Table (expandable)
        with st.expander("🔍 View Raw Data"):
            st.dataframe(
                merged_data[['Date', 'Close', 'Illumination', 'IsFullMoon']].tail(20),
                use_container_width=True
            )
    
    else:
        # Welcome message
        st.markdown("""
        ### Welcome to MoonCrypto! 🌙₿
        
        Ever wondered if the phases of the moon influence Bitcoin prices? This dashboard explores 
        the correlation between lunar cycles and cryptocurrency market movements using real data 
        and statistical analysis.
        
        **How it works:**
        1. Select your analysis period from the sidebar
        2. Click "Analyze Cosmic Correlation" to fetch data
        3. Explore the interactive charts and correlation analysis
        4. Read the dynamically generated story based on your data
        
        **Features:**
        - 📊 Real-time Bitcoin price data via Yahoo Finance
        - 🌙 Accurate moon phase calculations using astronomical data
        - 📈 Interactive dual-axis charts with Plotly
        - 🎯 Statistical correlation analysis (Pearson coefficient)
        - 📖 Dynamic storytelling based on correlation strength
        - 🎉 Celebratory effects for full moon discoveries
        
        Ready to discover if astrology meets finance? Click the analyze button to begin!
        """)
        
        # Fun facts while waiting
        st.markdown("""
        ---
        ### 🌟 Fun Facts While You Wait:
        - The moon's gravitational pull affects ocean tides by up to 50 feet in some places
        - Bitcoin's price has been known to be influenced by everything from tweets to regulatory news
        - The term "lunatic" comes from the Latin "luna" (moon), reflecting ancient beliefs about lunar influence
        - Some traders swear by lunar cycles, while others rely purely on technical analysis
        """)

if __name__ == "__main__":
    main()