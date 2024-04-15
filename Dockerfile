# Use a Python base image in version 3.8
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Expose the application port 3111
EXPOSE 3111

# Copy the requirements.txt file into the container at /app
COPY ./techtrends/requirements.txt /app


# Install packages defined in the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container at /app
COPY ./techtrends/. .

# Run the database initialization script
RUN python init_db.py

# Command to execute the application at container start
CMD ["python", "app.py"]