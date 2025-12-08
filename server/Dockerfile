# Step 1: Use an official Python runtime as a parent image
FROM python:3.11

# Step 2: Set working directory inside the container
WORKDIR /app

# Step 3: Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of the project files
COPY . .

# Step 5: Expose the port (Render uses $PORT)
ENV PORT 10000

# Step 6: Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
