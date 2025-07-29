from setuptools import setup, find_packages

setup(
    name="threadr-backend",
    version="1.0.0",
    description="Threadr - Twitter Thread Generator Backend",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "gunicorn>=21.2.0",
        "openai>=1.10.0",
        "httpx>=0.26.0",
        "beautifulsoup4>=4.12.3",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
    ],
)