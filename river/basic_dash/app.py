import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash


def get_simple_example():
    app = DjangoDash('simple_example')   # replaces dash.Dash
    app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
    external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
    for js in external_js:
        app.scripts.append_script({"external_url": js})

    app.layout = html.Div(['algo',


    ])



    if __name__ == '__main__':
        app.run_server(debug=True)

    return app