from django.shortcuts import render,get_object_or_404
from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response

from quiz.models import Answer, Question, Quiz, QuizTaker, UsersAnswer
from quiz.serializers import  QuizDetailSerializer, QuizListSerializer

class QuizListAPI(generics.ListAPIView):
    serializer_class = QuizListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = Quiz.objects.filter(roll_out=True)
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            ).distinct()
        return queryset


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = QuizDetailSerializer

    def get(self, *args, **kwargs):
        slug = self.kwargs["slug"]
        quiz = get_object_or_404(Quiz, slug=slug)
        last_question = None
        obj, created = QuizTaker.objects.get_or_create(
            user=self.request.user, quiz=quiz)
        if created:
            for question in Question.objects.filter(quiz=quiz):
                UserAnswer.objects.create(quiz_taker=obj, question=question)
        else:
            last_question = UserAnswer.objects.filter(
                quiz_taker=obj, answer__isnull=False)
            if last_question.count() > 0:
                last_question = last_question.last().question.id
            else:
                last_question = None
       
        return Response({ 'quiz': self.get_serializer(quiz,context={'result':self.request}).data, 'last_question_id':last_question})

