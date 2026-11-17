# HISTORICAL PROTOTYPE ONLY. No staging Space was created. Current runtime is GitHub Actions / ci_run.py.
# server.py no longer hosts HTTP. Do not build/deploy this file or launch a local runtime.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/home/user
RUN useradd -m -u 1000 user
WORKDIR /home/user/app
COPY requirements.txt /tmp/staging-requirements.txt
RUN pip install --no-cache-dir -r /tmp/staging-requirements.txt
COPY --chown=user:user . .
USER user
EXPOSE 7860
CMD ["python", "server.py"]
