import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

IVSURFACE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, IVSURFACE_PATH)

from IVSurface.IVmap import generate_iv_surface_html

app = Flask(__name__)
CORS(app)

@app.route('/compute', methods=['POST'])
def compute():
    data = request.json
    parameters = data.get('parameters', {})
    graph_type = data.get('graphType')

    if graph_type == 'IVMap':
        from IVSurface.IVmap import generate_iv_surface_html
        fig_json = generate_iv_surface_html(
            parameters.get('Ticker', 'AAPL'),
            parameters.get('Start Date'),
            parameters.get('End Date')
        )
    elif graph_type == 'OrderFlowCanyon':
        from OrderFlowCanyon.main import generate_order_flow_html
        print('here')
        fig_json = generate_order_flow_html(
            parameters.get('Ticker', 'AAPL'),
            parameters.get('Start Date'),
            parameters.get('End Date')
        )
    elif graph_type == 'USFixedIncomeYield':
        from YieldCurve.main import generate_yield_curve_html
        fig_json = generate_yield_curve_html(
            parameters.get('Issuer', 'US Treasury'),
            parameters.get('Start Date'),
            parameters.get('End Date')
        )
    else:
        return jsonify({"error": "Invalid graph type"}), 400
    
    return jsonify({"plotly_json": fig_json})

if __name__ == '__main__':
    app.run(port=5001)