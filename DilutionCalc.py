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
        html.H4("Molarity (C1V1 = C2V2)", className="card-title"),
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
# CALCULATOR 2: Mass from Volume and Concentration
# =============================================================================
mass_from_vol_layout = dbc.Card(
    dbc.CardBody([
        html.H4("Mass from Volume Calculator", className="card-title"),
        html.P("Calculates mass from concentration, volume, and molar mass."),
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Concentration"), dbc.Input(id="mfv-conc-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mfv-conc-unit", options=list(CONC_UNITS.keys()), value="mol/L")),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Volume"), dbc.Input(id="mfv-vol-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mfv-vol-unit", options=list(VOL_UNITS.keys()), value="ml")),
        ], className="mb-3"),
        dbc.Row([
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("Molar Mass (g/mol)"), dbc.Input(id="mfv-mm-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mfv-mass-unit", options=list(MASS_UNITS.keys()), value="mg"), width=4),
        ], className="mb-3"),
        dbc.Button("Calculate", id="btn-calc-mfv", color="primary", n_clicks=0),
        dbc.Alert(id="mfv-output", color="success", className="mt-3", is_open=False)
    ])
)

@callback(
    Output("mfv-output", "children"),
    Output("mfv-output", "is_open"),
    Input("btn-calc-mfv", "n_clicks"),
    [State("mfv-conc-val", "value"), State("mfv-conc-unit", "value"),
     State("mfv-vol-val", "value"), State("mfv-vol-unit", "value"),
     State("mfv-mm-val", "value"), State("mfv-mass-unit", "value")],
    prevent_initial_call=True
)
def calculate_mass_from_volume(n_clicks, conc, conc_u, vol, vol_u, mm, mass_u):
    try:
        # Convert inputs to base units (mol/L, L)
        conc_base = float(conc) * CONC_UNITS[conc_u]
        vol_base = float(vol) * VOL_UNITS[vol_u]
        molar_mass = float(mm)

        # Calculation: moles = conc * vol, then mass = moles * molar_mass
        mass_base = conc_base * vol_base * molar_mass # Mass in grams
        
        # Convert final mass to selected unit
        final_mass = mass_base / MASS_UNITS[mass_u]

        return f"Result: Mass = {final_mass:g} {mass_u}", True

    except (ValueError, TypeError):
        return "Error: Please fill in all fields with valid numbers.", True
    except ZeroDivisionError:
        return "Error: Cannot divide by zero.", True

# =============================================================================
# CALCULATOR 3: Mass Concentration (C1V1 = C2V2)
# =============================================================================
mass_conc_layout = dbc.Card(
    dbc.CardBody([
        html.H4("Mass Concentration (C1V1 = C2V2)", className="card-title"),
        html.P("Enter three values to calculate the fourth. Uses mass/volume units."),
        dbc.Row([
            # C1 Inputs - Note the new 'mc-' prefix for all IDs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("C1"), dbc.Input(id="mc-c1-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-c1-unit", options=list(MASS_CONC_UNITS.keys()), value="mg/ml")),
            # V1 Inputs
            dbc.Col(dbc.InputGroup([dbc.InputGroupText("V1"), dbc.Input(id="mc-v1-val", type="number")])),
            dbc.Col(dcc.Dropdown(id="mc-v1-unit", options=list(VOL_UNITS.keys()), value="ml")),
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
    "/molarity": {"name": "Molarity (C1V1=C2V2)", "layout": molarity_layout},
    "/mass-from-volume": {"name": "Mass from Volume", "layout": mass_from_vol_layout},
    "/mass-concentration": {"name": "Mass Concentration", "layout": mass_conc_layout},
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