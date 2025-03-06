from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """
    Allows access only to users who have a customer profile.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_customer
        )


class IsProvider(BasePermission):
    """
    Allows access only to users with a provider profile.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'provider')


class IsCustomerOrProvider(BasePermission):
    """
    Allows access to users who have either a customer or provider profile.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_customer or request.user.is_provider)
        )

class IsPackageMaker(BasePermission):
    """
    Allows access only to users with a package maker role.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'package_maker'
        )
    
class IsPackageMakerOrCustomer(BasePermission):
    """
    Allows access to users who have either a package maker or customer profile.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'package_maker' or request.user.role == 'customer')
        )