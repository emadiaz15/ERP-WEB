from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import Pagination
from apps.metrics.api.repositories.parameter_repository import ParameterRepository
from apps.metrics.api.serializers.parameter_serializers import MetricParameterSerializer


class MetricParameterListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.query_params.get("search")
        queryset = ParameterRepository.list_parameters(search=search)
        paginator = Pagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = MetricParameterSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MetricParameterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        parameter = serializer.save(user=request.user)
        output = MetricParameterSerializer(parameter).data
        return Response(output, status=status.HTTP_201_CREATED)


class MetricParameterDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, parameter_id: int):
        queryset = ParameterRepository.list_parameters()
        return get_object_or_404(queryset, pk=parameter_id)

    def get(self, request, parameter_id: int):
        parameter = self._get_object(parameter_id)
        serializer = MetricParameterSerializer(parameter)
        return Response(serializer.data)

    def put(self, request, parameter_id: int):
        parameter = self._get_object(parameter_id)
        serializer = MetricParameterSerializer(parameter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save(user=request.user)
        output = MetricParameterSerializer(updated).data
        return Response(output)

    def delete(self, request, parameter_id: int):
        parameter = self._get_object(parameter_id)
        ParameterRepository.soft_delete(parameter, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
