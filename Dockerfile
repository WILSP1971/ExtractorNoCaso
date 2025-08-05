# Usa una imagen base de Python con Debian
FROM python:3.10-slim


#RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev

# Instala dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

    # Establece el directorio de trabajo
WORKDIR /app
# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expón el puerto usado por Flask
EXPOSE 5000

# Comando por defecto para correr la app
CMD ["python", "app.py"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
