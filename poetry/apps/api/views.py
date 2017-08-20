from rest_framework.views import APIView


class GetAccent(APIView):
    def get(self, request, format=None):
        raise NotImplementedError()