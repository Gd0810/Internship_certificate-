from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from company.models import InternshipTrack, TaskModule, UserTaskProgress
from accounts.models import InternProfile
from payments.models import Payment
from certificates.models import CertificateTemplate, OfferLetterTemplate

User = get_user_model()


class Command(BaseCommand):
    help = "Flushes pre-existing seeded data and sets up fresh demo tracks, templates, and 3 accounts (Django Admin, Company Admin, Student)."

    def handle(self, *args, **options):
        self.stdout.write("Clearing all pre-existing database records...")

        with transaction.atomic():
            UserTaskProgress.objects.all().delete()
            Payment.objects.all().delete()
            InternProfile.objects.all().delete()
            User.objects.all().delete()
            TaskModule.objects.all().delete()
            InternshipTrack.objects.all().delete()
            CertificateTemplate.objects.all().delete()
            OfferLetterTemplate.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("All old database records removed."))

        # 1. Create Tracks & Task Modules
        tracks_data = [
            {
                "name": "Generative AI",
                "description": "Learn prompt engineering, build applications with LLM APIs, implement RAG systems, and create autonomous AI agents.",
                "points": "Prompt Engineering & APIs, RAG & Vector Databases, AI Agents & Automation",
                "price": 499,
                "modules": [
                    ("Environment & LLM Setup", "Set up API keys, environment variables, and basic Python scripts."),
                    ("Prompt Engineering & API Integration", "Build structured prompts and handle JSON model completions."),
                    ("RAG & Vector Storage", "Implement vector store document chunking and semantic search."),
                    ("Autonomous AI Agent", "Build a tool-calling agent workflow for automated tasks."),
                ]
            },
            {
                "name": "Cybersecurity & Ethical Hacking",
                "description": "Understand security principles, web vulnerabilities (OWASP Top 10), conduct assessments, and practice defensive security.",
                "points": "Linux & Reconnaissance tools, Web Application Security, Incident Response & Defense",
                "price": 599,
                "modules": [
                    ("Linux Fundamentals & Recon", "Perform port scanning and target enumeration using Nmap."),
                    ("OWASP Top 10 Security Audit", "Analyze SQL injection, XSS, and broken authentication vectors."),
                    ("Incident Response & Patching", "Remediate vulnerabilities and write defensive security patches."),
                ]
            },
            {
                "name": "Cloud Computing & DevOps",
                "description": "Deploy server architectures, manage virtualization, containerize apps with Docker, and build CI/CD pipelines.",
                "points": "Cloud Deployment & Networking, Docker Containerization, DevOps & CI/CD Pipelines",
                "price": 699,
                "modules": [
                    ("Linux Cloud Server Setup", "Configure Nginx, systemd services, and SSH key pairs."),
                    ("Docker Containerization", "Write Dockerfiles and compose multi-container stacks."),
                    ("CI/CD Pipeline Automation", "Create automated build and deploy pipelines using GitHub Actions."),
                ]
            },
            {
                "name": "Full Stack Development",
                "description": "Build modern web applications using front-end and back-end technologies through hands-on projects.",
                "points": "Frontend Frameworks (React), REST API Backend (Node/Express), Database Modeling (MongoDB/PostgreSQL)",
                "price": 499,
                "modules": [
                    ("Environment & Git Setup", "Set up local dev environment and repository."),
                    ("Build Responsive Frontend", "Implement interactive UI components and responsive layout."),
                    ("Connect Backend REST API", "Wire client routes to server endpoints and database models."),
                    ("Testing & Production Deploy", "Write unit test cases and deploy to cloud host."),
                ]
            },
        ]

        created_tracks = []
        for item in tracks_data:
            track, _ = InternshipTrack.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "points": item["points"],
                    "price": item["price"],
                    "is_active": True,
                },
            )
            # Ensure points and description are updated
            track.description = item["description"]
            track.points = item["points"]
            track.price = item["price"]
            track.save()

            if not track.task_modules.exists():
                for idx, (title, desc) in enumerate(item["modules"], start=1):
                    TaskModule.objects.create(track=track, title=title, description=desc, order=idx)

            created_tracks.append(track)

        track_web = created_tracks[3]  # Full Stack Development

        # 2. Set up Default Templates
        CertificateTemplate.objects.create(track=None, folder_path="default-seed", is_active=True)
        OfferLetterTemplate.objects.create(track=None, folder_path="default-seed", is_active=True)
        self.stdout.write(self.style.SUCCESS("Default certificate & offer-letter templates activated."))

        # 3. Create the 3 Accounts
        # Account 1: Django Admin Superuser
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPassword123!",
            first_name="DjangoAdmin",
        )
        self.stdout.write(self.style.SUCCESS("Created Django Admin: admin / admin@example.com"))

        # Account 2: Company Admin (Staff User)
        company_user = User.objects.create_user(
            username="company",
            email="company@example.com",
            password="CompanyPassword123!",
            first_name="CompanyAdmin",
            is_staff=True,
        )
        self.stdout.write(self.style.SUCCESS("Created Company Admin: company / company@example.com"))

        # Account 3: Student Account
        student_user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="StudentPassword123!",
            first_name="John",
            last_name="Doe",
        )
        student_profile = InternProfile.objects.create(
            user=student_user,
            full_name="John Doe",
            college_name="Stanford University",
            degree="B.S. Computer Science",
            track=track_web,
            mobile_number="+919876543210",
            has_paid=True,
        )
        student_profile.generate_certificate_id()

        # Mark first task as completed for demonstration
        first_task = track_web.task_modules.first()
        if first_task:
            UserTaskProgress.objects.create(profile=student_profile, task=first_task, is_completed=True)

        self.stdout.write(self.style.SUCCESS("Created Student Account: student@example.com"))
        self.stdout.write(self.style.SUCCESS("--- Database reset and re-seeding complete ---"))
