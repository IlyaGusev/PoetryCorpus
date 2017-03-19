from rupo.api import get_accent
from rest_framework.views import APIView
from rest_framework.response import Response


class GetAccent(APIView):
    def get(self, request, format=None):
        word = request.query_params.get("word")
        if word == "" or word is None:
            return Response(-1)
        return Response(data=get_accent(word))