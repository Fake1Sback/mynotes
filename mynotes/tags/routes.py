from flask import Blueprint
from flask import render_template, redirect,flash, url_for, request
from mynotes import db
from mynotes.tags.forms import TagForm
from mynotes.models import load_user, Tag
from flask_login import current_user

tgs = Blueprint('tgs',__name__)

@tgs.route('/tags',methods=['GET','POST'])
def tags():
    page = request.args.get('page',1,type=int)
    if current_user.is_authenticated and current_user.activated:
        tags = Tag.query.filter(Tag.owner_id == current_user.id).paginate(per_page=20,page=page)
        return render_template('tags.html',tags = tags)
    else:
        return redirect(url_for('accounts.login'))

@tgs.route('/edittag',defaults={'tagid':None},methods=['GET','POST'])
@tgs.route('/edittag/<int:tagid>', methods=['GET','POST'])
def edittag(tagid):
    if current_user.is_authenticated and current_user.activated:
        form = TagForm()
        if request.method == 'GET':
            if tagid is None:
                return render_template('edittag.html',form = form)
            else:
                edited_tag = Tag.query.get(tagid)
                form.name.data = edited_tag.name
                form.description.data = edited_tag.description
                return render_template('edittag.html',form = form, tagid = tagid)
        elif request.method == 'POST':      
            if tagid is None:
                if form.validate_on_submit():
                    searched_tag = Tag.query.filter(Tag.name == form.name.data,Tag.owner_id == current_user.id).first()
                    if searched_tag:
                        flash(f'You allready have tag with such name','warning')
                        return render_template('edittag.html',form=form)
                    new_Tag = Tag(name=form.name.data,description=form.description.data,owner_id=current_user.id)
                    db.session.add(new_Tag)
                    db.session.commit()
                    flash(f'Tag {new_Tag.name} was added','success')
                    return redirect(url_for('tgs.tags'))
                else:
                    return render_template('edittag.html',form = form)               
            else:
                tag = Tag.query.get(tagid)
                if tag is not None:
                    if form.validate_on_submit():
                        tag.name = form.name.data
                        tag.description = form.description.data
                        db.session.commit()
                        flash(f'Tag was changed','success')
                        return redirect(url_for('tgs.tags'))
                    else:
                        return render_template('edittag.html',form = form,tagid=tagid)
                else:
                    flash('Tag with such id does not exist','warning')
                    return render_template('edittag.html',form=form,tagid=tagid)
    else:
        return redirect(url_for('accounts.login'))

@tgs.route('/deletetag/<int:tagid>')
def deletetag(tagid):
    if current_user.is_authenticated and current_user.activated:
        tag = Tag.query.get(tagid)
        if tag is not None:
            db.session.delete(tag)
            db.session.commit()
            flash(f'Tag {tag.name} was deleted','danger')
            return redirect(url_for('tgs.tags'))
    else:
        return redirect(url_for('accounts.login'))
