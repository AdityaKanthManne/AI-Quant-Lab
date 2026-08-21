FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY research_projects ./research_projects
EXPOSE 8000
CMD ["uvicorn", "research_copilot.api:app", "--host", "0.0.0.0", "--port", "8000"]

