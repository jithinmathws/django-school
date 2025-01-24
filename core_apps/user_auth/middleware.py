"""
Custom middleware to add user information to response headers.
This middleware adds the authenticated user's email to the response headers,
which can be useful for debugging or tracking purposes.
"""

class CustomHeaderMiddleware:
    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process each request/response through the middleware
        Args:
            request: The incoming HTTP request
        Returns:
            response: The processed HTTP response with added headers if user is authenticated
        """
        response = self.get_response(request)
        if request.user.is_authenticated:
            response["X-Django-User"] = request.user.email
        return response