from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.db.models import F
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import Group, User

from rest_framework import permissions, viewsets

from .models import Question, Choice
from .serializers import GroupSerializer, UserSerializer


# それぞれの汎用ビューには、どのモデルに対して動作するかを認識させる必要があります。
# これは model 属性を指定するか、
# get_queryset() 関数を定義することで実現できます。
# デフォルトでは、 DetailView 汎用ビューは <app name>/<model name>_detail.html という名前のテンプレートを使います。
# この場合、テンプレートの名前は "polls/question_detail.html" です。
# template_name 属性を指定すると、自動生成されたデフォルトのテンプレート名ではなく、
# 指定したテンプレート名を使うように Django に伝えることができます。
# 同様に、 ListView 汎用ビューは <app name>/<model name>_list.html というデフォルトのテンプレートを使うので、
# template_name を使って ListView に既存の "polls/index.html" テンプレートを使用するように伝えます。
# このチュートリアルの前の部分では、
# question や latest_question_list といったコンテキスト変数が含まれるコンテキストをテンプレートに渡していました。
# DetailView には question という変数が自動的に渡されます。
# なぜなら、 Django モデル（Question）を使用していて、
# Django はコンテキスト変数にふさわしい名前を決めることができるからです。
# 一方で、 ListView では、自動的に生成されるコンテキスト変数は question_list になります。
# これを上書きするには、 context_object_name 属性を与え、 latest_question_list を代わりに使用すると指定します。


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    
    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]

    # def get_queryset(self):
    #     """Return the last five published questions."""
    #     return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


# def index(request):
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "polls/index.html", context)


# # def index(request):
# #     latest_question_list = Question.objects.order_by("-pub_date")[:5]
# #     template = loader.get_template("polls/index.html")
# #     context = {
# #         "latest_question_list": latest_question_list,
# #     }
# #     return HttpResponse(template.render(context, request))


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})


# # def detail(request, question_id):
# #     try:
# #         question = Question.objects.get(pk=question_id)
# #     except Question.DoesNotExist:
# #         raise Http404("Question does not exist")
# #     return render(request, "polls/detail.html", {"question": question})


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "polls/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    