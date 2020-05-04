from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, SelectField, FileField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class ArticleForm(FlaskForm):
    temporary_id = HiddenField(default='')
    title = StringField('Title',validators=[DataRequired()])
    tags = StringField('Tags')
    shared = BooleanField('Shared',default=False)
    encrypted = BooleanField(default=False)
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Save')

class DownloadForm(FlaskForm):
    id = StringField('Id',validators=[DataRequired()])
    title = StringField('Title',validators=[DataRequired()])
    content = StringField('Content',validators=[DataRequired()])

