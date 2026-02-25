## On first run activate the venv and install these modules:
# pip install dash dash-bootstrap-components numpy scipy

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

# --- App Initialization ---
# Using a Bootstrap theme for a clean look
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
app.title = "Scientific Calculator Dashboard"


# --- Unit Conversion Dictionaries ---
CONC_UNITS = {"mol/L": 1.0, "mmol/L": 1e-3, "umol/L": 1e-6, "nmol/L": 1e-9}
VOL_UNITS = {"L": 1.0, "ml": 1e-3, "ul": 1e-6}
MASS_UNITS = {"g": 1.0, "mg": 1e-3, "ug": 1e-6, "ng": 1e-9}
MASS_CONC_UNITS = {"mg/ml": 1.0, "ug/ml": 1e-3, "ng/ml": 1e-6}

# =============================================================================
# CALCULATOR 1: Molarity (C1V1 = C2V2)
# =============================================================================
molarity_layout = dbc.Card(
    dbc.CardBody([
        html.H4("Dilute by Molarity (C1V1 = C2V2)", className="card-title"),
        html.P("Enter three values to calculate the fourth."),
        dbc.Row([
            # C1 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("C1"), dbc.Input(id="c1-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="c1-unit", options=list(CONC_UNITS.keys()), value="mmol/L")),
            # V1 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("V1"), dbc.Input(id="v1-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="v1-unit", options=list(VOL_UNITS.keys()), value="ul")),
        ], className="mb-3"),
        dbc.Row([
            # C2 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("C2"), dbc.Input(id="c2-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="c2-unit", options=list(CONC_UNITS.keys()), value="umol/L")),
            # V2 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("V2"), dbc.Input(id="v2-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="v2-unit", options=list(VOL_UNITS.keys()), value="ml")),
        ], className="mb-3"),
        dbc.Button("Calculate", id="btn-calc-molarity", color="primary", n_clicks=0),
        dbc.Alert(id="molarity-output", color="success", className="mt-3", is_open=False)
    ])
)

@callback(
    Output("molarity-output", "children"),
    Output("molarity-output", "is_open"),
    Input("btn-calc-molarity", "n_clicks"),
    [State("c1-val", "value"), State("c1-unit", "value"),
     State("v1-val", "value"), State("v1-unit", "value"),
     State("c2-val", "value"), State("c2-unit", "value"),
     State("v2-val", "value"), State("v2-unit", "value")],
    prevent_initial_call=True
)
def calculate_molarity(n_clicks, c1, c1u, v1, v1u, c2, c2u, v2, v2u):
    inputs = {
        'c1': c1, 'v1': v1, 'c2': c2, 'v2': v2
    }
    
    # Check which input is empty (the one to solve for)
    solve_for = [k for k, v in inputs.items() if v is None]
    if len(solve_for) != 1:
        return "Error: Please leave exactly one field empty to solve for.", True
    
    solve_for = solve_for[0]

    try:
        # Convert all provided inputs to base units (mol/L and L)
        c1_base = float(c1) * CONC_UNITS[c1u] if c1 is not None else None
        v1_base = float(v1) * VOL_UNITS[v1u] if v1 is not None else None
        c2_base = float(c2) * CONC_UNITS[c2u] if c2 is not None else None
        v2_base = float(v2) * VOL_UNITS[v2u] if v2 is not None else None

        # Calculate the missing value
        if solve_for == 'c2':
            result = (c1_base * v1_base) / v2_base
            final_val = result / CONC_UNITS[c2u]
            return f"Result: C2 = {final_val:g} {c2u}", True
        if solve_for == 'v2':
            result = (c1_base * v1_base) / c2_base
            final_val = result / VOL_UNITS[v2u]
            return f"Result: V2 = {final_val:g} {v2u}", True
        # Add logic for C1 and V1 if needed
        if solve_for == 'c1':
            result = (c2_base * v2_base) / v1_base
            final_val = result / CONC_UNITS[c1u]
            return f"Result: C1 = {final_val:g} {c1u}", True
        if solve_for == 'v1':
            result = (c2_base * v2_base) / c1_base
            final_val = result / VOL_UNITS[v1u]
            return f"Result: V1 = {final_val:g} {v1u}", True

    except (ValueError, TypeError):
        return "Error: Ensure all three input fields are valid numbers.", True
    except ZeroDivisionError:
        return "Error: Cannot divide by zero.", True
    
    return "", False


# =============================================================================
# CALCULATOR 2: Prepare Molar Solution
# =============================================================================
prepare_molar_solution_layout = dbc.Card(
    dbc.CardBody([
        html.H4("Prepare Molar Solution", className="card-title"),
        html.P("Enter any three values to calculate the fourth."),
        # Row for Concentration
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Concentration"), dbc.Input(id="pms-conc-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="pms-conc-unit", options=list(CONC_UNITS.keys()), value="mmol/L")),
        ], className="mb-3"),
        # Row for Volume
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Volume"), dbc.Input(id="pms-vol-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="pms-vol-unit", options=list(VOL_UNITS.keys()), value="ul")),
        ], className="mb-3"),
        # Row for Mass
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Mass"), dbc.Input(id="pms-mass-val", type="number", placeholder="")])),
            dbc.Col(dcc.Dropdown(id="pms-mass-unit", options=list(MASS_UNITS.keys()), value="mg")),
        ], className="mb-3"),
        # Row for Molar Mass
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Molar Mass (g/mol)"), dbc.Input(id="pms-mm-val", type="number", placeholder="")])),
        ], className="mb-3"),
        dbc.Button("Calculate", id="btn-calc-pms", color="primary", n_clicks=0),
        dbc.Alert(id="pms-output", color="success", className="mt-3", is_open=False)
    ])
)

@callback(
    Output("pms-output", "children"),
    Output("pms-output", "is_open"),
    Input("btn-calc-pms", "n_clicks"),
    [State("pms-conc-val", "value"), State("pms-conc-unit", "value"),
     State("pms-vol-val", "value"), State("pms-vol-unit", "value"),
     State("pms-mass-val", "value"), State("pms-mass-unit", "value"),
     State("pms-mm-val", "value")],
    prevent_initial_call=True
)
def calculate_prepare_molar_solution(n_clicks, conc, conc_u, vol, vol_u, mass, mass_u, mm):
    try:
        inputs = {'conc': conc, 'vol': vol, 'mass': mass, 'mm': mm}
        
        # Identify which field is empty (the one to solve for)
        solve_for = [k for k, v in inputs.items() if v is None]
        if len(solve_for) != 1:
            return "Error: Please leave exactly one field empty to solve for.", True
        
        solve_for = solve_for[0]

        # Convert all provided inputs to their base units (mol/L, L, g)
        conc_base = float(conc) * CONC_UNITS[conc_u] if conc is not None else None
        vol_base = float(vol) * VOL_UNITS[vol_u] if vol is not None else None
        mass_base = float(mass) * MASS_UNITS[mass_u] if mass is not None else None
        mm_base = float(mm) if mm is not None else None # Molar mass is already in its base unit (g/mol)

        # Perform the calculation based on the empty field
        if solve_for == 'mass':
            result = conc_base * vol_base * mm_base
            final_val = result / MASS_UNITS[mass_u]
            return f"Result: Mass = {final_val:g} {mass_u}", True
        
        elif solve_for == 'conc':
            result = mass_base / (vol_base * mm_base)
            final_val = result / CONC_UNITS[conc_u]
            return f"Result: Concentration = {final_val:g} {conc_u}", True
            
        elif solve_for == 'vol':
            result = mass_base / (conc_base * mm_base)
            final_val = result / VOL_UNITS[vol_u]
            return f"Result: Volume = {final_val:g} {vol_u}", True

        elif solve_for == 'mm':
            result = mass_base / (conc_base * vol_base)
            # Molar mass result is already in g/mol
            return f"Result: Molar Mass = {result:g} g/mol", True

    except (ValueError, TypeError, KeyError):
        return "Error: Ensure all three input fields are valid numbers.", True
    except ZeroDivisionError:
        return "Error: Cannot divide by zero. Check your inputs.", True
    
    return "", False
    
# =============================================================================
# CALCULATOR 3: Mass Concentration (C1V1 = C2V2)
# =============================================================================
mass_conc_layout = dbc.Card(
    dbc.CardBody([
        html.H4("Dilute by concentration", className="card-title"),
        html.P("Enter three values to calculate the fourth. Uses mass/volume units."),
        dbc.Row([
            # C1 Inputs - Note the new 'mc-' prefix for all IDs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("C1"), dbc.Input(id="mc-c1-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-c1-unit", options=list(MASS_CONC_UNITS.keys()), value="mg/ml")),
            # V1 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("V1"), dbc.Input(id="mc-v1-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-v1-unit", options=list(VOL_UNITS.keys()), value="ul")),
        ], className="mb-3"),
        dbc.Row([
            # C2 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("C2"), dbc.Input(id="mc-c2-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-c2-unit", options=list(MASS_CONC_UNITS.keys()), value="ug/ml")),
            # V2 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("V2"), dbc.Input(id="mc-v2-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-v2-unit", options=list(VOL_UNITS.keys()), value="ml")),
        ], className="mb-3"),
        dbc.Button("Calculate", id="btn-calc-mc", color="primary", n_clicks=0),
        dbc.Alert(id="mc-output", color="success", className="mt-3", is_open=False)
    ])
)

@callback(
    Output("mc-output", "children"),
    Output("mc-output", "is_open"),
    Input("btn-calc-mc", "n_clicks"),
    [State("mc-c1-val", "value"), State("mc-c1-unit", "value"),
     State("mc-v1-val", "value"), State("mc-v1-unit", "value"),
     State("mc-c2-val", "value"), State("mc-c2-unit", "value"),
     State("mc-v2-val", "value"), State("mc-v2-unit", "value")],
    prevent_initial_call=True
)
def calculate_mass_conc(n_clicks, c1, c1u, v1, v1u, c2, c2u, v2, v2u):
    inputs = {'c1': c1, 'v1': v1, 'c2': c2, 'v2': v2}
    solve_for = [k for k, v in inputs.items() if v is None]
    if len(solve_for) != 1:
        return "Error: Please leave exactly one field empty to solve for.", True
    
    solve_for = solve_for[0]

    try:
        # Use the new MASS_CONC_UNITS dictionary for concentrations
        c1_base = float(c1) * MASS_CONC_UNITS[c1u] if c1 is not None else None
        v1_base = float(v1) * VOL_UNITS[v1u] if v1 is not None else None
        c2_base = float(c2) * MASS_CONC_UNITS[c2u] if c2 is not None else None
        v2_base = float(v2) * VOL_UNITS[v2u] if v2 is not None else None

        if solve_for == 'c2':
            result = (c1_base * v1_base) / v2_base
            final_val = result / MASS_CONC_UNITS[c2u]
            return f"Result: C2 = {final_val:g} {c2u}", True
        if solve_for == 'v2':
            result = (c1_base * v1_base) / c2_base
            final_val = result / VOL_UNITS[v2u]
            return f"Result: V2 = {final_val:g} {v2u}", True
        if solve_for == 'c1':
            result = (c2_base * v2_base) / v1_base
            final_val = result / MASS_CONC_UNITS[c1u]
            return f"Result: C1 = {final_val:g} {c1u}", True
        if solve_for == 'v1':
            result = (c2_base * v2_base) / c1_base
            final_val = result / VOL_UNITS[v1u]
            return f"Result: V1 = {final_val:g} {v1u}", True

    except (ValueError, TypeError):
        return "Error: Ensure all three input fields are valid numbers.", True
    except ZeroDivisionError:
        return "Error: Cannot divide by zero.", True
    
    return "", False

# =============================================================================
# Main App Layout and Callbacks
# =============================================================================
# Dictionary to hold our calculators
CALCULATORS = {
    "/molarity": {"name": "Dilute Molar Solution", "layout": molarity_layout},
    "/mass-concentration": {"name": "Dilute solution", "layout": mass_conc_layout},
    "/prepare-molar-solution": {"name": "Prepare Molar Solution", "layout": prepare_molar_solution_layout}
}

# --- Sidebar and Main Layout ---
sidebar = html.Div([
    html.H2("Calculators", className="display-6"),
    html.Hr(),
    dbc.Nav(
        [dbc.NavLink(data["name"], href=path, active="exact") for path, data in CALCULATORS.items()],
        vertical=True, pills=True
    )
], id="sidebar")

content = html.Div(id="page-content")

app.layout = dbc.Container([
    html.H1("Scientific Calculator Dashboard", className="my-4"),
    dbc.Row([
        dbc.Col(sidebar, width=3, className="bg-light p-3"),
        dbc.Col(content, width=9)
    ])
], fluid=True)


# --- Callback to switch between calculator layouts ---
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    # Default to the first calculator if the path is not recognized
    if pathname in CALCULATORS:
        return CALCULATORS[pathname]["layout"]
    else:
        # Redirect to the first calculator's page
        first_calculator_path = next(iter(CALCULATORS))
        return CALCULATORS[first_calculator_path]["layout"]

# Add the dcc.Location component to track the URL
app.layout.children.append(dcc.Location(id='url', refresh=False))


# --- Main execution block ---
if __name__ == '__main__':
    app.run(debug=True)