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
        track_web, _ = InternshipTrack.objects.get_or_create(
            name="Web Development",
            defaults={
                "description": "Build real front-end and back-end features across guided modules using modern Django & web tech.",
                "price": 499,
                "is_active": True,
            },
        )
        web_modules = [
            ("Environment & Git Setup", "Set up your local dev environment and make your first commit."),
            ("Build a Responsive Layout", "Implement modern HTML & CSS templates for web applications."),
            ("Connect Django Views & API", "Wire templates to backend views and REST endpoints."),
            ("Write Tests & Deploy", "Add test cases and verify application workflow."),
        ]
        for idx, (title, desc) in enumerate(web_modules, start=1):
            TaskModule.objects.create(track=track_web, title=title, description=desc, order=idx)

        track_ds, _ = InternshipTrack.objects.get_or_create(
            name="Data Science & AI",
            defaults={
                "description": "Learn data preprocessing, machine learning model building, and evaluation.",
                "price": 699,
                "is_active": True,
            },
        )
        ds_modules = [
            ("Data Cleaning & EDA", "Analyze and clean structured datasets using Pandas."),
            ("Model Training", "Train regression and classification algorithms."),
            ("Evaluation & Deployment", "Evaluate performance and package models for production."),
        ]
        for idx, (title, desc) in enumerate(ds_modules, start=1):
            TaskModule.objects.create(track=track_ds, title=title, description=desc, order=idx)

        self.stdout.write(self.style.SUCCESS("Demo internship tracks and task modules created."))

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
