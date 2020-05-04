from flask import render_template, redirect, flash, url_for, request, Blueprint, abort, send_file, Response, make_response, json, Markup, send_from_directory
from mynotes import db, app
from sqlalchemy import func
from mynotes.articles.forms import ArticleForm, DownloadForm
from mynotes.models import load_user, Article, Association, Tag, ArticleImage
from flask_login import current_user
from rsa import DecryptionError
from werkzeug.utils import secure_filename
import pdfkit
import os, io, secrets, imghdr


rticles = Blueprint('rticles',__name__)

@rticles.route('/edit/<int:articleid>', methods=['GET','POST'])
@rticles.route('/edit', defaults={"articleid":None}, methods = ['GET','POST'])
def edit(articleid):
    if current_user.is_authenticated and current_user.activated:
        form = ArticleForm()
        if request.method == 'GET':
            all_tags = current_user.tags
            if articleid is None:
                form.temporary_id.data = secrets.token_hex(16)
                return render_template('edit.html', form = form, alltags = all_tags,encrypted=False)
            else:
                article = Article.query.get(articleid)
                if article.author_id != current_user.id:
                    abort(403)
                form.title.data = article.title
                form.content.data = article.content
                form.shared.data = article.shared
                form.encrypted.data = article.encrypted
                article_tags = ''
                title_tags = []
                for i in article.tags:
                    title_tags.append(i)
                    if i == article.tags[-1]:
                        article_tags = article_tags + i.name
                    else:
                        article_tags = article_tags + i.name + ','
                form.tags.data = article_tags
                return render_template('edit.html', form = form, title_tags=title_tags, articleid=articleid, alltags=current_user.tags, encrypted=article.encrypted)
        elif request.method == 'POST':
            if form.validate_on_submit() == False:
                abort(500)
            tags_string = form.tags.data
            form_tags = tags_string.split(',')
            for i in form_tags:
                i.strip()
            if articleid is None:
                article = Article(title=form.title.data,content=form.content.data,shared=form.shared.data,encrypted=form.encrypted.data, author_id=current_user.id)
                for i in current_user.tags:
                    for j in form_tags:
                        if i.name == j:
                            article.tags.append(i)
                db.session.add(article)
                db.session.commit()
                article_images = ArticleImage.query.filter(ArticleImage.temporary_id == form.temporary_id.data).all()
                if article_images:
                    for i in article_images:
                        i.temporary_id = None
                        i.article_id = article.id
                    db.session.commit()
                flash(f'Article was added','success')
                return redirect(url_for('rticles.articles'))
            else:
                article = Article.query.get(articleid)
                if article.author_id != current_user.id:
                    abort(403)
                article.title = form.title.data
                article.content = form.content.data
                article.shared = form.shared.data
                article.encrypted = form.encrypted.data
                article.tags.clear()      
                all_user_tags = current_user.tags
                for i in form_tags:
                    for j in all_user_tags:
                        if i == j.name:
                            article.tags.append(j)
                db.session.commit()
                flash(f'Article was updated','success')
                return redirect(url_for('rticles.articles'))           
    else:
        flash('To create or edit articles you need to be loged in','warning')
        abort(403)

@rticles.route('/delete/<int:articleid>')
def delete(articleid):
    if current_user.is_authenticated and current_user.activated:
        article_to_delete = Article.query.get(articleid)
        if article_to_delete is not None:
            if article_to_delete.author_id == current_user.id:
                db.session.delete(article_to_delete)
                db.session.commit()
                flash(f'Article was deleted','danger')
                return redirect(url_for('rticles.articles'))
            else:
                abort(403)
        else:
            abort(500)    
    else:
        flash('To delete articles you need to be logged in','warning')
        abort(403)


@rticles.route('/')
@rticles.route('/articles',methods=['GET'])
def articles():
    page = request.args.get('page',1,type=int)
    title = request.args.get('title','',type=str)
    tags = request.args.get('tags','',type=str)
    onlymy = request.args.get('onlymy',False,type=bool)
    if current_user.is_authenticated and current_user.activated:
        user_articles = Article.query.filter(Article.author_id == current_user.id)
        if not onlymy:
            shared_articles = Article.query.filter(Article.author_id != current_user.id, Article.shared == True)
            user_articles = user_articles.union(shared_articles)
        if title:
            user_articles = user_articles.filter(Article.title.contains(title))
        if tags:
            request_tags_set = set(tags.replace(' ','').split(','))
            featured_tags = Tag.query.filter(Tag.name.in_(request_tags_set)).with_entities(Tag.id,Tag.name).all()
            tag_idis = []
            existing_tags = []
            for i in featured_tags:
                tag_idis.append(i[0])
            assoc = Association.query.filter(Association.tag_id.in_(tag_idis))\
                .group_by(Association.article_id)\
                .having(func.count(Association.tag_id) == len(request_tags_set))\
                .with_entities(Association.article_id).all()
            assoc_idis = []
            for i in assoc:
                assoc_idis.append(i[0])
            user_articles = user_articles.filter(Article.id.in_(assoc_idis))
        user_articles = user_articles.order_by(Article.date_posted.desc()).paginate(page=page,per_page=10)
        return render_template('articles.html',articles=user_articles,title=title,tags=tags,onlymy=onlymy)
    else:
        articles = Article.query.filter_by(shared=True)
        if title:
            articles = articles.filter(Article.title.contains(title))
        if tags:
            request_tags_set = set(tags.replace(' ','').split(','))
            featured_tags = Tag.query.filter(Tag.name.in_(request_tags_set)).with_entities(Tag.id).all()
            tag_idis = []
            for i in featured_tags:
                tag_idis.append(i[0])
            assoc = Association.query.filter(Association.tag_id.in_(tag_idis))\
                .group_by(Association.article_id)\
                .having(func.count(Association.tag_id) == len(request_tags_set))\
                .with_entities(Association.article_id).all()
            assoc_idis = []
            for i in assoc:
                assoc_idis.append(i[0])
            articles = articles.filter(Article.id.in_(assoc_idis))
        articles = articles.order_by(Article.date_posted.desc()).paginate(page=page,per_page=10)
        return render_template('articles.html',articles=articles,title=title,tags=tags,onlymy=onlymy)

@rticles.route('/article/<int:articleid>')
def article(articleid):
    article = Article.query.get(articleid)
    form = DownloadForm()
    if article.shared:
        return render_template('article.html',article=article,encrypted = article.encrypted, form = form)
    else:
        if current_user.is_authenticated and current_user.activated and current_user.id == article.author_id:
            return render_template('article.html',article=article,encrypted = article.encrypted, form = form)
        else:
            abort(403)

@rticles.route('/articleimage',methods=['GET','POST'])
def articleimage():
    if request.method == 'GET':
        image_id = request.args.get('id',-1,type=int)
        if image_id == -1:
            return Response(status=404)
        else:
            db_image = ArticleImage.query.filter(ArticleImage.id == image_id).first()
            if db_image:
                if current_user.is_authenticated:
                    if current_user.id == db_image.owner_id:
                        return send_file(io.BytesIO(db_image.content),attachment_filename=db_image.name)
                    else:
                        article_id = db_image.article_id
                        if article_id:
                            is_shared = Article.query.filter(Article.id == article_id).with_entities(Article.shared).first()[0]
                            if is_shared:
                                return send_file(io.BytesIO(db_image.content),attachment_filename=db_image.name)
                            else:
                                return Response(status=403)
                        else:
                            return Response(status=404)
                else:
                    article_id = db_image.article_id
                    if article_id:
                        is_shared = Article.query.filter(Article.id == article_id).with_entities(Article.shared).first()[0]
                        if is_shared:
                            return send_file(io.BytesIO(db_image.content),attachment_filename=db_image.name)
                        else:
                            return Response(status=403)
                    else:
                        return Response(status=404)
            else:
                return Response(status=404)
    elif request.method == 'POST':
        if current_user.is_authenticated:
            temporary_id = request.form.get('temp-id','',type=str)
            article_id = request.form.get('art-id',-1,type=int)
            if 'article-image' not in request.files:
                return Response(status=400)
            file = request.files['article-image']
            
            name_parts = file.filename.split('.')
            if len(name_parts) > 2:
                return abort(500)

            for i in range(len(name_parts)):
                name_parts[i] = secure_filename(name_parts[i])
                if name_parts[i] == '':
                    name_parts[i] = secrets.token_urlsafe(16)

            file_content = file.read()
            img_format = imghdr.what(None,file_content)
            
            if img_format is None:
                return Response(status=500)
            else:
                if img_format not in ['rgb','gif','webp','pbm','pgm','ppm','tiff','rast','xbm','jpeg','bmp','png']:
                    return Response(status=500)

            filename = name_parts[0] + '.' + img_format
            article_image = ArticleImage(name = filename,content = file_content,owner_id = current_user.id)
            if temporary_id != '' and article_id == -1:
                article_image.temporary_id = temporary_id
            elif temporary_id == '' and article_id != -1:
                article_image.article_id = article_id
            else:
                abort(500)
            db.session.add(article_image)
            db.session.commit()

            return url_for('rticles.articleimage',id=article_image.id,_external=True)
        else:
            abort(403)


@rticles.route('/download',methods=['POST'])
def download():
    form = DownloadForm()
    if form.validate_on_submit() == False:
        abort(500)
    id = form.id.data
    title = form.title.data
    content = f'''
    <html>
        <head>
            <meta charset='utf-8'>
        </head>
        <body>
    {form.content.data} 
        </body>
    </html>
    ''' 
    article = Article.query.get(id)
    if not article:
        abort(404)
    if article.encrypted:
        abort(500)
    safe_name = secure_filename(article.title.replace(' ',''))
    if safe_name == '':
        safe_name = secrets.token_urlsafe(10)
    first_css = os.path.join(app.root_path,'static','atelier-sulphurpool-light.css')
    second_css = os.path.join(app.root_path,'static','main_theme7.css')
    if article.shared:
        pdf = pdfkit.from_string(content,False,css=[first_css,second_css])
        return send_file(io.BytesIO(pdf),mimetype='application/pdf',as_attachment=True,attachment_filename=safe_name + '.pdf')
    else:       
        if not current_user.is_authenticated:
            abort(403)
        else:
            if article.author_id == current_user.id:
                options = {'cookie':[('session',request.cookies['session'])]}
                pdf = pdfkit.from_string(content,False,css=[first_css,second_css],options=options)
                return send_file(io.BytesIO(pdf),mimetype='application/pdf',as_attachment=True,attachment_filename=safe_name + '.pdf')
            else:
                abort(403)