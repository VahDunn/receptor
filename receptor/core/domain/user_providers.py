from enum import StrEnum


class UserProvider(StrEnum):
    telegram = "telegram"
    email = "email"
    google = "google"
    apple = "apple"
    github = "github"