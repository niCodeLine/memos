from unittest import TestCase

from app.ai.enrichment import classify_urgency, enrich_reminder, suggest_category


class EnrichmentTests(TestCase):
    def test_classifies_high_urgency_words(self):
        self.assertEqual(classify_urgency("urgente llamar al medico"), "high")

    def test_suggests_health_category(self):
        self.assertEqual(suggest_category("dentista mañana"), "health")

    def test_enriches_missing_fields(self):
        reminder = enrich_reminder({"text": "deadline importante"})

        self.assertEqual(reminder["urgency"], "high")
        self.assertEqual(reminder["channel"], "telegram")
        self.assertIsNotNone(reminder["remind_at"])
