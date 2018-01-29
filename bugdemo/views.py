from .models import Question
from django.http import HttpResponse

# Create your views here.
def new_question(request, question):
	# import ipdb; ipdb.set_trace()
	new_question = Question(question_text=question)
	new_question.save()
	return  HttpResponse('your question saved')