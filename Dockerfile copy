FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
COPY . /app
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt
ENTRYPOINT ["python", "mlops/modeling/train.py"]
