"""Main collection of views."""
import os
from flask import Blueprint, jsonify, render_template, url_for
from flask import current_app as app


# Blue print for the main display
home_blueprint = Blueprint(
    'home',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@home_blueprint.route('/', methods=['GET'])
def home():
    """Main home page."""
    return render_template(
        'main.html',
    )


# Cache Buster for static files
@home_blueprint.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)
