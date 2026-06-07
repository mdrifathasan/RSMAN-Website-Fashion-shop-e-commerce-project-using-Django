from django.db import models

class Report(models.Model):
    report_type = models.CharField(max_length=100)
    generated_at = models.DateTimeField(auto_now_add=True)
    # Change JSONField to TextField for SQLite compatibility
    data = models.TextField(blank=True, default='{}')  # Store JSON as text
    
    def __str__(self):
        return f"{self.report_type} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_data(self):
        """Parse the text data as JSON"""
        import json
        try:
            return json.loads(self.data)
        except:
            return {}
    
    def set_data(self, value):
        """Store data as JSON string"""
        import json
        self.data = json.dumps(value)