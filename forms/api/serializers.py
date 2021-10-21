"""Serializers for turning Django ORM data into JSON"""

from rest_framework import serializers

from dcac.models import ACGReimbursementForm

class RequestSerializer(serializers.ModelSerializer):
    """Serializer to turn a ACGReimbursementForm object into a json format"""
    reimbursement_type = serializers.CharField(source='get_reimbursement_type_display') # convert to string
    organization = serializers.StringRelatedField()
    class Meta:
        model = ACGReimbursementForm
        exclude = ['sort_code', 'account_number']
