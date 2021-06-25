"""Stores all constants used as numbers for readability"""

class AdminRoles:
    """ """
    JCRTREASURER = 1
    SENIORTREASURER = 2
    BURSARY = 3
    SENIORBURSAR = 4

    CHOICES = (
        (JCRTREASURER, 'JCR Treasurer'),
        (SENIORTREASURER, 'Senior Treasurer'),
        (BURSARY, 'Bursary'),
        (SENIORBURSAR, 'Senior Bursar')
    )


class RequestTypes:
    """ """
    STANDARD = 1
    INTERNAL = 2
    LARGE = 3

    CHOICES = (
        (STANDARD, 'Standard Request'),
        (INTERNAL, 'Internal Transfer'),
        (LARGE, 'Large Requests')
    )


class ResponseCodes:
    """
    `request.POST.get('code')`"""
    APPROVED = '1'
    REJECTED = '2'
    PAID = '3'