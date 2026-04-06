from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserMeSerializer


class PingView(APIView):
    """Public health-check endpoint used by the frontend to verify connectivity."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"pong": True})


class MeView(APIView):
    """Returns the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)
