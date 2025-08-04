# Use a slim Python image for a smaller footprint
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for asyncpg and psycopg2
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your application will run on
EXPOSE 9000

# Set an entrypoint script to wait for the database
# We will create this script in the next step
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# The command to run your application.
# The entrypoint.sh script will handle the database wait, and then this CMD will run.
CMD ["./entrypoint.sh"]
