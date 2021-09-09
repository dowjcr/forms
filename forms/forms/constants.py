"""Stores constants used as numbers for readability that are used across all apps"""

class AdminRoles:
    """ """
    JCRTREASURER = 1
    SENIORTREASURER = 2
    BURSARY = 3
    ASSISTANTBURSAR = 4

    CHOICES = (
        (JCRTREASURER, 'JCR Treasurer'),
        (SENIORTREASURER, 'Senior Treasurer'),
        (BURSARY, 'Bursary'),
        (ASSISTANTBURSAR, 'Assistant Bursar')
    )
