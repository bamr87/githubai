"""
Management command to check saved prompts.
"""
from django.core.management.base import BaseCommand
from core.models import PromptTemplate


class Command(BaseCommand):
    help = 'Check saved prompts in database'

    def handle(self, *args, **options):
        total = PromptTemplate.objects.count()
        self.stdout.write(f'\nTotal prompts: {total}\n')

        self.stdout.write('\nAll prompts:')
        self.stdout.write('=' * 70)
        for p in PromptTemplate.objects.order_by('id'):
            self.stdout.write(f'\nID {p.id}: {p.name}')
            self.stdout.write(f'  Category: {p.category}')
            self.stdout.write(f'  Model: {p.model} ({p.provider})')
            self.stdout.write(f'  Active: {p.is_active}')
            self.stdout.write(f'  Usage: {p.usage_count} times')
            if p.description:
                desc = p.description[:80] + '...' if len(p.description) > 80 else p.description
                self.stdout.write(f'  Description: {desc}')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('\nDone!'))
