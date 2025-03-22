from rest_framework import serializers
from .models import LogEntry

class LogSerializers(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = "__all__"