from flask import Blueprint, render_template, abort
from flask_login import current_user

kys = Blueprint('kys',__name__)

@kys.route('/keys',methods=['GET'])
def keys():
    if current_user.is_authenticated:
        return render_template('keys.html')
    else:
        abort(403)
