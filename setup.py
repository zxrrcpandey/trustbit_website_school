from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="trustbit_website_school",
    version="1.0.0",
    description="Trustbit Website School - Custom Webshop for School Supplies",
    author="Trustbit",
    author_email="info@trustbit.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
