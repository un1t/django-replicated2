from setuptools import setup


setup(
    name='django_replicated',
    description='Django DB router for stateful master-slave replication',
    packages=[
        'django_replicated',
        'django_replicated.tests',
    ],
    test_suite = "runtests.runtests",
)
