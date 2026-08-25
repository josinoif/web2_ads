FROM python:3.12-alpine
WORKDIR /app
COPY common.py app.py analise_mod.py store_mod.py ./
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
