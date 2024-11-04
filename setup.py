from setuptools import setup, find_packages

setup(
    name="feedback-analyzer",
    version="1.0.0",
    packages=find_packages(),  # Removed the src directory specification
    install_requires=[
        "pandas>=2.0.0",
        "anthropic>=0.8.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
        "tqdm>=4.66.0",
        "openpyxl>=3.1.0",
    ],
    author="Juhani Merilehto",
    author_email="juhani.merilehto@protonmail.com",
    description="A tool for analyzing open-ended feedback using LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/juhanimerilehto/thematic-analyzer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)