from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIScrubber:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def scrub_text(self, text: str) -> str:
        """
        Analyze and anonymize PII in the given text.
        """
        results = self.analyzer.analyze(
            text=text, 
            entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "LOCATION"], 
            language="en"
        )
        anonymized_result = self.anonymizer.anonymize(
            text=text, 
            analyzer_results=results
        )
        return anonymized_result.text

pii_scrubber = PIIScrubber()
