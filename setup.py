from setuptools import setup, find_packages

setup(
    name = "django-alpaca",
    url = "http://github.com/sebleier/django-alpaca/",
    author = "Sean Bleier",
    author_email = "sebleier@gmail.com",
    version = "0.0.1",
    packages = find_packages(),
    description = "Load fixtures using south, in a sane way.",
    install_requires=['django', 'south'],
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
