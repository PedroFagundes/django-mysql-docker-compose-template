import jwt

from django.conf import settings


class DecodeJWTRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request = self.process_request(request)

        return self.get_response(request)

    def process_request(self, request):
        authorization_token = request.headers.get('Authorization')

        if request.user and authorization_token:
            token = request.headers['Authorization'].replace(
                'Bearer ', '')

            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])

            workspace_id = decoded_token.get('workspace_id')

            request.workspace_id = workspace_id

        return request
