# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "role", "branch", "branch_name", "project",
                  "first_name", "last_name", "phone", "department", "is_locked", "is_active",
                  "can_manage_questions", "can_manage_tasks", "can_view_data",
                  "can_export_data", "can_manage_employees"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        password = self.request.data.get("password", "hr123456")
        serializer.save(password=make_password(password))

    @action(detail=True, methods=["post"])
    def toggle_lock(self, request, pk=None):
        user = self.get_object()
        user.is_locked = not user.is_locked
        user.is_active = not user.is_locked
        user.save()
        return Response({"is_locked": user.is_locked})

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        pw = request.data.get("password", "hr123456")
        user.password = make_password(pw)
        user.save()
        return Response({"status": "ok"})

