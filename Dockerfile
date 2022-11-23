FROM python:3.8

# set a key-value label for the Docker image
LABEL maintainer="Mahmoud Kassem"

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD ./techtrends/ /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Initialize the database
RUN python init_db.py

# Make port 3111 available to the world outside this container
EXPOSE 3111

# Run app.py when the container launches
CMD ["python", "app.py"]
