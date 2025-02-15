import numpy as np
import pandas as pd
import plotly.graph_objects as go
from .data import get_yield_data

# def generate_yield_curve_html(issuer, start_date, end_date):
#     """
#     Maintains original parameters structure while using working local logic
#     Returns Plotly figure as JSON string
#     """
#     try:
#         # Get data using original working configuration
#         x, y, z = get_yield_data(start_date, end_date)
        
#         # Create grid using original logic
#         x_grid, y_grid = np.meshgrid(x, y)
        
#         # Generate surface plot with original styling
#         fig = go.Figure(data=[go.Surface(
#             z=z,
#             x=x_grid,
#             y=y_grid,
#             colorscale="Viridis",
#             colorbar=dict(title="Yield (%)"),
#         )])
        
#         # Maintain original layout configuration
#         fig.update_layout(
#             title="3D Interest Rate Term Structure",
#             scene=dict(
#                 xaxis=dict(title="Maturity (Months)"),
#                 yaxis=dict(title="Date"),
#                 zaxis=dict(title="Yield (%)"),
#             ),
#             margin=dict(l=0, r=0, b=0, t=50),
#         )
        
#         print(f"Yield data dimensions - X: {len(x)}, Y: {len(y)}, Z: {z.shape}")
#         print(f"Sample Z data: {z[0] if z.size > 0 else 'Empty'}")
        
#         return fig.to_json()
        
#     except Exception as e:
#         return {"error": str(e)}

def generate_yield_curve_html(issuer, start_date, end_date):
    # Fetch data
    x, y, z = get_yield_data(start_date, end_date)

    # Create Plotly figure
    fig = go.Figure(data=[
        go.Surface(
            z=z,
            x=x,  # Maturities (1D array)
            y=y,  # Dates (1D array)
            colorscale="Viridis",
            colorbar=dict(title="Yield (%)")
        )
    ])

    # Configure layout
    fig.update_layout(
        title="3D Interest Rate Term Structure",
        scene=dict(
            xaxis=dict(title="Maturity (Months)"),
            yaxis=dict(title="Date"),
            zaxis=dict(title="Yield (%)")
        ),
        margin=dict(l=0, r=0, b=0, t=50)
    )

    return fig.to_json()

# Example usage (for testing)
if __name__ == "__main__":
    fig_json = generate_term_structure_json(
        pd.to_datetime("2024-07-01"),
        pd.to_datetime("2025-01-01")
    )
    print(fig_json)  # Send this JSON to your frontend