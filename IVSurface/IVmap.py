import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objs as go
import plotly.offline as pyo  # for generating HTML
from .BSMCompute import compute_implied_vols

def generate_iv_surface_html(ticker_symbol, start_date, end_date):
    """
    Generates a 3D implied volatility surface using Plotly and returns it 
    as an HTML string. (Use 'dangerouslySetInnerHTML' in React to display.)
    """

    # --- 1) Compute your data for calls & puts ---
    ivs_calls, mny_calls, ttes_calls = compute_implied_vols(ticker_symbol, "calls", start_date, end_date)
    ivs_puts, mny_puts, ttes_puts   = compute_implied_vols(ticker_symbol, "puts", start_date, end_date)
    # Combine calls + puts
    ivs  = np.array(ivs_calls + ivs_puts)
    mny  = np.array(mny_calls + mny_puts)
    ttes = np.array(ttes_calls + ttes_puts)

    # If no data, return an error message in HTML
    if len(ivs) == 0:
        return f"<p>No option data found for {ticker_symbol} with the chosen parameters.</p>"

    # --- 2) Filter or clamp moneyness if desired ---
    # e.g., -7 <= m <= 7. Just example; change as needed
    mask = (mny >= -7) & (mny <= 7)
    ivs  = ivs[mask]
    mny  = mny[mask]
    ttes = ttes[mask]

    if len(ivs) == 0:
        return f"<p>After filtering, no data remains for {ticker_symbol}.</p>"

    # --- 3) Interpolate to make a 3D surface grid ---
    grid_mny, grid_ttes = np.meshgrid(
        np.linspace(min(mny), max(mny), 50),
        np.linspace(min(ttes), max(ttes), 50)
    )
    grid_ivs = griddata(
        (mny, ttes), ivs, (grid_mny, grid_ttes), method='cubic'
    )

    # --- 4) Build a Plotly figure for 3D surface ---
    surface = go.Surface(
        x=grid_mny,  # X-axis
        y=grid_ttes, # Y-axis
        z=grid_ivs,  # Z-axis (IV)
        colorscale='Viridis'
    )
    layout = go.Layout(
        title=f"Implied Volatility Surface for {ticker_symbol}",
        scene=dict(
            xaxis_title="Moneyness (S/K or K/S)",
            yaxis_title="Time to Expiry (Years)",
            zaxis_title="Implied Volatility"
        )
    )
    fig = go.Figure(data=[surface], layout=layout)

    fig_json = fig.to_json()
    
    return fig_json

