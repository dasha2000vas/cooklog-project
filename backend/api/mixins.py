from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

User = get_user_model()


class ListRetrieveViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    pass


class CreateDestroyRelationshipViewSet(
    GenericViewSet, CreateModelMixin, DestroyModelMixin
):
    permission_classes = (IsAuthenticated,)

    def create(
        self, request, field, key, post_serializer, model, *args, **kwargs
    ):
        request.data.update({field: kwargs[key]})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        object = post_serializer(
            instance=model.objects.get(id=self.kwargs[key]),
            context={'request': request}
        )
        headers = self.get_success_headers(object.data)
        return Response(
            object.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, model, key, *args, **kwargs):
        '''
        Сначала проверяется, существует ли объект(рецепт или автор),
        если нет, выбрасывается ошибка 404.
        Далее - существует ли связь текущего пользователя
        с этим объектом. Если нет, выходит ошибка 400.
        '''
        get_object_or_404(model, id=self.kwargs[key])
        try:
            self.get_object()
        except Http404:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, *args, **kwargs)
