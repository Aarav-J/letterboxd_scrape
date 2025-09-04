FROM public.ecr.aws/lambda/python:3.8

# Install Redis
RUN yum update -y && \
    amazon-linux-extras install redis6 -y

# Copy function code
COPY letterboxdscraper.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Redis startup script
COPY start.sh ${LAMBDA_TASK_ROOT}
RUN chmod +x ${LAMBDA_TASK_ROOT}/start.sh

# Set the handler and entrypoint
CMD [ "start.sh" ]
