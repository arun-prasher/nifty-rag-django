from django.core.management.base import BaseCommand
from django.conf import settings

from ragapp.indexer import build_and_save_index


class Command(BaseCommand):
    help = 'Build and save FAISS index for playbooks/rules/summaries'

    def handle(self, *args, **options):
        build_and_save_index(settings.TRADING_KNOWLEDGE_DIR, settings.RAG_INDEX_DIR)
        self.stdout.write(self.style.SUCCESS('✅ RAG index built successfully.'))
