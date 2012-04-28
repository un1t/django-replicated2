import sys
from distutils.core import setup


setup(
    name='django_replicated',
    description='Django DB router for stateful master-slave replication',
    packages=[
        'django_replicated',
    ],
    scripts=['runtests.py'] if 'develop' in sys.argv else []
)
