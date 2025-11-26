"""
Test environment setup command - creates isolated test environment with mock AI data.

Orchestrates full test environment initialization:
1. Database setup (create/flush/persist)
2. Load test configuration (providers, models)
3. Generate content with MockAIProvider
4. Create test superuser
5. Validate all data
6. Display access summary

Usage:
    # Full fresh setup
    python manage.py setup_test_env --full

    # Quick setup keeping existing DB
    python manage.py setup_test_env

    # Setup with persistence (don't flush on next run)
    python manage.py setup_test_env --full --persist

    # Show current test data stats
    python manage.py setup_test_env --analyze
"""
import logging
import sys
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.contrib.auth import get_user_model
from core.models import AIProvider, AIModel, PromptTemplate, IssueTemplate, Issue

logger = logging.getLogger("githubai")
User = get_user_model()


class Command(BaseCommand):
    help = "Setup test environment with mock AI data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Full setup: drop/create DB, flush all data, start fresh",
        )
        parser.add_argument(
            "--persist",
            action="store_true",
            help="Mark test DB as persistent (won't auto-flush on next run)",
        )
        parser.add_argument(
            "--analyze",
            action="store_true",
            help="Analyze current test data without making changes",
        )
        parser.add_argument(
            "--skip-content",
            action="store_true",
            help="Skip content generation (only load config)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Verbose output for debugging",
        )

    def handle(self, *args, **options):
        self.verbose = options.get("verbose", False)

        # Header
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(
            self.style.SUCCESS("GitHubAI Test Environment Setup".center(80))
        )
        self.stdout.write("=" * 80 + "\n")

        # Check if we're in test settings
        from django.conf import settings

        if not getattr(settings, "TEST_ENV", False):
            self.stdout.write(
                self.style.WARNING(
                    "⚠ Warning: Not running in test environment "
                    "(DJANGO_SETTINGS_MODULE should be githubai.settings_test)"
                )
            )
            if not self._confirm("Continue anyway?"):
                return

        # Analyze mode
        if options.get("analyze"):
            self._analyze_test_data()
            return

        # Step 1: Database setup
        self._step("Database Setup")
        if options.get("full"):
            self._full_database_setup()
        else:
            self._quick_database_check()

        # Step 2: Load test configuration
        self._step("Load Test Configuration")
        self._load_test_config()

        # Step 3: Generate content (optional)
        if not options.get("skip_content"):
            self._step("Generate Test Content")
            self._generate_test_content()
        else:
            self.stdout.write("  Skipping content generation (--skip-content)")

        # Step 4: Create test superuser
        self._step("Create Test Superuser")
        self._create_test_superuser()

        # Step 5: Validate
        self._step("Validate Configuration")
        self._validate_config()

        # Step 6: Summary
        self._display_summary()

        # Mark persistence if requested
        if options.get("persist"):
            self._mark_persistent()

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ Test Environment Ready!".center(80)))
        self.stdout.write("=" * 80 + "\n")

    def _step(self, title: str):
        """Display step header"""
        self.stdout.write("\n" + "-" * 80)
        self.stdout.write(self.style.SUCCESS(f"▶ {title}"))
        self.stdout.write("-" * 80)

    def _confirm(self, question: str) -> bool:
        """Ask user for yes/no confirmation"""
        response = input(f"{question} [y/N]: ").lower().strip()
        return response in ["y", "yes"]

    def _full_database_setup(self):
        """Full database setup: flush and migrate"""
        self.stdout.write("  Flushing database...")
        try:
            call_command("flush", "--no-input", verbosity=0)
            self.stdout.write(self.style.SUCCESS("  ✓ Database flushed"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error flushing database: {e}"))
            sys.exit(1)

        self.stdout.write("  Running migrations...")
        try:
            call_command("migrate", "--no-input", verbosity=0)
            self.stdout.write(self.style.SUCCESS("  ✓ Migrations applied"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error running migrations: {e}"))
            sys.exit(1)

    def _quick_database_check(self):
        """Quick check that database is accessible"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("  ✓ Database connection OK"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Database connection failed: {e}")
            )
            sys.exit(1)

    def _load_test_config(self):
        """Load test configuration fixtures"""
        self.stdout.write("  Loading test_config.json...")
        try:
            call_command(
                "loaddata",
                "apps/core/fixtures/test_config.json",
                verbosity=2 if self.verbose else 0,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Loaded {AIProvider.objects.count()} providers, "
                    f"{AIModel.objects.count()} models"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error loading config: {e}"))
            sys.exit(1)

    def _generate_test_content(self):
        """Generate test content using MockAIProvider or load fixtures"""
        # Check if MockAIProvider is available
        from django.conf import settings

        if settings.AI_PROVIDER == "mock":
            self.stdout.write(
                "  Using MockAIProvider for content generation (deterministic)..."
            )
            # Just load the test_content fixture for now
            # In future, could actually call generate_content_data with mock
            try:
                call_command(
                    "loaddata",
                    "apps/core/fixtures/test_content.json",
                    verbosity=2 if self.verbose else 0,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Loaded {PromptTemplate.objects.count()} templates, "
                        f"{IssueTemplate.objects.count()} issue templates, "
                        f"{Issue.objects.count()} sample issues"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Error loading test content: {e}")
                )
        else:
            self.stdout.write("  Loading test_content.json fixture...")
            try:
                call_command(
                    "loaddata",
                    "apps/core/fixtures/test_content.json",
                    verbosity=2 if self.verbose else 0,
                )
                self.stdout.write(self.style.SUCCESS("  ✓ Test content loaded"))
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Error loading content: {e}")
                )

    def _create_test_superuser(self):
        """Create test superuser if not exists"""
        try:
            if User.objects.filter(username="admin").exists():
                self.stdout.write("  ✓ Test superuser 'admin' already exists")
            else:
                User.objects.create_superuser(
                    username="admin", email="admin@test.local", password="admin123"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "  ✓ Created test superuser (username: admin, password: admin123)"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"  ⚠ Error creating superuser: {e}")
            )

    def _validate_config(self):
        """Validate configuration"""
        self.stdout.write("  Running validation...")
        try:
            call_command("validate_config", skip_connectivity=True, verbosity=0)
            self.stdout.write(self.style.SUCCESS("  ✓ Configuration valid"))
        except SystemExit as e:
            if e.code == 0:
                self.stdout.write(self.style.SUCCESS("  ✓ Configuration valid"))
            else:
                self.stdout.write(
                    self.style.WARNING("  ⚠ Validation found issues (check above)")
                )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ⚠ Validation error: {e}"))

    def _display_summary(self):
        """Display summary of loaded data and access URLs"""
        self._step("Test Environment Summary")

        # Data counts
        provider_count = AIProvider.objects.count()
        model_count = AIModel.objects.count()
        template_count = PromptTemplate.objects.count()
        issue_count = Issue.objects.count()
        user_count = User.objects.count()

        self.stdout.write("\n  📊 Data Loaded:")
        self.stdout.write(f"     • AI Providers: {provider_count}")
        self.stdout.write(f"     • AI Models: {model_count}")
        self.stdout.write(f"     • Prompt Templates: {template_count}")
        self.stdout.write(f"     • Sample Issues: {issue_count}")
        self.stdout.write(f"     • Users: {user_count}")

        # Access URLs
        self.stdout.write("\n  🌐 Access URLs:")
        self.stdout.write("     • Django Admin:    http://localhost:8001/admin/")
        self.stdout.write("     • API Root:        http://localhost:8001/api/")
        self.stdout.write("     • Chat Interface:  http://localhost:5174/")
        self.stdout.write("     • Documentation:   http://localhost:8002/")

        # Credentials
        self.stdout.write("\n  🔑 Test Credentials:")
        self.stdout.write("     • Username: admin")
        self.stdout.write("     • Password: admin123")

        # AI Provider
        from django.conf import settings

        self.stdout.write("\n  🤖 AI Provider:")
        self.stdout.write(f"     • Provider: {settings.AI_PROVIDER}")
        self.stdout.write(
            f"     • Model: {getattr(settings, f'{settings.AI_PROVIDER.upper()}_MODEL', 'N/A')}"
        )

    def _analyze_test_data(self):
        """Analyze current test data without making changes"""
        self._step("Test Data Analysis")

        # Providers
        self.stdout.write("\n  AI Providers:")
        for provider in AIProvider.objects.all():
            self.stdout.write(
                f"    • {provider.name} ({provider.provider_type}) - "
                f"{'ACTIVE' if provider.is_active else 'INACTIVE'}"
            )
            models = AIModel.objects.filter(provider=provider)
            for model in models:
                self.stdout.write(
                    f"      → {model.name} ({'default' if model.is_default else 'available'})"
                )

        # Templates
        self.stdout.write("\n  Prompt Templates:")
        for template in PromptTemplate.objects.all()[:10]:  # Show first 10
            self.stdout.write(f"    • {template.name} ({template.category})")

        # Issues
        issue_count = Issue.objects.count()
        self.stdout.write(f"\n  Sample Issues: {issue_count}")
        for issue in Issue.objects.all()[:5]:  # Show first 5
            self.stdout.write(f"    • #{issue.github_issue_number}: {issue.title}")

        # Users
        self.stdout.write(f"\n  Users: {User.objects.count()}")
        for user in User.objects.all()[:5]:
            self.stdout.write(
                f"    • {user.username} ({'staff' if user.is_staff else 'user'})"
            )

    def _mark_persistent(self):
        """Mark test database as persistent (for future feature)"""
        self.stdout.write(
            "\n  ℹ Note: --persist flag noted (no DB persistence mechanism yet)"
        )
