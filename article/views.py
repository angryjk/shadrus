# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http.response import HttpResponse, Http404
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response, redirect
from article.models import Article, Comments
from django.core.exceptions import ObjectDoesNotExist
from forms import CommentForm
from django.core.context_processors import csrf
from django.core.paginator import Paginator
from django.contrib import auth
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa

# Create your views here.
def basic_one(request):
	view = BASE_DIR #"basic_one"
	html = "<html><body>This is %s view</body></html>" %view
	return HttpResponse(html)

def template_two(request):
	view = "template_two"
	t = get_template('myview.html')
	html = t.render(Context({'name':view}))
	return HttpResponse(html)

def template_three_simple (request):
	view = "template_three"
	return render_to_response('myview.html', {'name':view})

def articles(request, page_number=1):
	all_articles = Article.objects.all()
	current_page = Paginator(all_articles,3)
	return render_to_response('articles.html', {'articles':current_page.page(page_number), 'username': auth.get_user(request).username})

def article (request, article_id=1, page_id=1):
	#return render_to_response('article.html',{'article':Article.objects.get(id=article_id),'comments':Comments.objects.filter(comments_article_id=article_id)})
	all_comments = Comments.objects.filter (comments_article_id=article_id)
	current_page = Paginator(all_comments,2)
	comment_form = CommentForm
	args = {}
	args.update(csrf(request))
	args['article'] = Article.objects.get(id=article_id)
	args['comments'] = current_page.page(page_id) #Comments.objects.filter (comments_article_id=article_id)
	args['form'] = comment_form
	args['username'] = auth.get_user(request).username 
	return render_to_response('article.html', args)

def addlike (request, page_id, article_id):
	try:
			if article_id in request.COOKIES:
				redirect ('/')
			else:
				article = Article.objects.get(id=article_id)
				article.article_likes +=1
				article.save()
				response = redirect('/page/%s/' % page_id)
				response.set_cookie(article_id, "test")
				return response
	except ObjectDoesNotExist:
		raise Http404
	return redirect('/page/%s/' % page_id)

def addcomment (request, article_id):
	if request.POST and ("pause" not in request.session):
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)#забороняє зберігати одразу в БД, при тому записуючи в comment значення тектстового поля
			comment.comments_article = Article.objects.get(id=article_id)
			form.save()
			request.session.set_expiry(60)
			request.session['pause'] = True
	return redirect('/articles/get/%s/' % article_id) #повернути на ту саму сторінку з якої писався коментар

def getpdf (request) :
	sourcehtml = request.get_host();
	pdfname = "file.pdf"
	resultFile = open(pdfname, "w+b")
	pisaStatus = pisa.CreatePDF(sourcehtml, dest=resultFile)
	resultFile = close()
	return pisaStatus.err
	'''response = HttpResponse(content_type='application/pdf')
	response ['Content-Disposition'] = 'attachment; filename="file.pdf"'
	p = canvas.Canvas(response)
	p.drawString(0,0, str(66))
	p.showPage()
	p.save()


	return response
	'''