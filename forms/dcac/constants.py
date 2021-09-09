"""Stores all constants used as numbers for readability"""

class RequestTypes:
    """ """
    STANDARD = 1
    INTERNAL = 2
    LARGE = 3

    CHOICES = (
        (STANDARD, 'Standard'),
        (INTERNAL, 'Internal'),
        (LARGE, 'Large')
    )


class ResponseCodes:
    """"""
    APPROVED = '1'
    REJECTED = '2'
    PAID = '3'


class FundSources:
    """"""
    ACG = 1
    DEPRECIATION = 2

    CHOICES = (
        (ACG, 'Annual Consumable Grant'),
        (DEPRECIATION, 'Depreciation Fund')
    )
