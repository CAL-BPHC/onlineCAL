import factory
from factory.django import DjangoModelFactory

from .models import CustomUser, Faculty, Instrument, LabAssistant, Student


class CustomUserFaker(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Faker("email")


class StudentFactory(CustomUserFaker):
    class Meta:
        model = Student

    supervisor = factory.SubFactory("booking_portal.factories.FacultyFactory")


class FacultyFactory(CustomUserFaker):
    class Meta:
        model = Faculty


class LabAssistantFactory(CustomUserFaker):
    class Meta:
        model = LabAssistant


class InstrumentFactory(DjangoModelFactory):
    class Meta:
        model = Instrument
