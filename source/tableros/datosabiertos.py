import dash_html_components as html

accrualPeriodicityDays = {
  "R/P10Y": 360 * 10,
  "R/P4Y": 360 * 4,
  "R/P3Y": 360 * 3,
  "R/P2Y": 360 * 2,
  "R/P1Y": 360,
  "R/P6M": 30 * 6,
  "R/P4M": 30 * 4,
  "R/P3M": 30 * 3,
  "R/P2M": 30 * 2,
  "R/P1M": 30,
  "R/P0.5M": 30 * 0.5,
  "R/P0.33M": 30 * 0.33,
  "R/P1W": 7,
  "R/P0.5W": 7 * 0.5,
  "R/P0.33W": 7 * 0.33,
  "R/P1D": 1,
  "R/PT1H": 1,
  "R/PT1S": 1,
  "eventual": 0
}

def layout():
  return html.Div("Datos abiertos")