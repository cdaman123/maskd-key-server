# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create a non-root user
RUN groupadd -r maskd_user && useradd -r -g maskd_user maskd_user

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=maskd_user:maskd_user app/ /app/app/

# Switch to non-root user for security
USER maskd_user

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.main:app"]
