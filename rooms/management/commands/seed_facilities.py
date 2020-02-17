from django.core.management.base import BaseCommand
from rooms.models import Facility


class Command(BaseCommand):

    help = "seeding facilities"

    """     def add_arguments(self, parser):
        parser.add_argument(
            "--times", help="This command tells you that how many times he loves me"
        ) """

    def handle(self, *args, **options):
        facilities = [
            "Private entrance",
            "Paid parking on premises",
            "Paid parking off premises",
            "Elevator",
            "Parking",
            "Gym",
        ]
        for f in facilities:
            Facility.objects.create(name=f)
        self.stdout.write(self.style.SUCCESS(f"{len(facilities)} facilities created "))
