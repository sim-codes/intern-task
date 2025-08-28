from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    """
    Rate limiting for login attempts.
    
    Allows 5 login attempts per minute per IP address to prevent brute force attacks.
    """
    scope = 'login'
    rate = '5/minute'

    def get_cache_key(self, request, view):
        """
        Generate cache key based on user IP address.
        """
        return self.get_ident(request)


class PasswordResetThrottle(SimpleRateThrottle):
    """
    Rate limiting for password reset requests.
    
    Allows 3 password reset requests per hour per IP address.
    """
    scope = 'password_reset'
    rate = '3/hour'

    def get_cache_key(self, request, view):
        """
        Generate cache key based on user IP address.
        """
        return self.get_ident(request)


class PasswordResetConfirmThrottle(SimpleRateThrottle):
    """
    Rate limiting for password reset confirmations.
    
    Allows 10 password reset confirmations per hour per IP address.
    """
    scope = 'password_reset_confirm'
    rate = '10/hour'

    def get_cache_key(self, request, view):
        """
        Generate cache key based on user IP address.
        """
        return self.get_ident(request)


class RegistrationThrottle(SimpleRateThrottle):
    """
    Rate limiting for user registration.
    
    Allows 10 registration attempts per hour per IP address.
    """
    scope = 'registration'
    rate = '10/hour'

    def get_cache_key(self, request, view):
        """
        Generate cache key based on user IP address.
        """
        return self.get_ident(request)
