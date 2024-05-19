# Build Django staticfiles and 
FROM python:3.9-slim-bookworm as django-app

WORKDIR /usr/src/app

RUN --mount=type=bind,source=./requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir --requirement /tmp/requirements.txt
COPY . .
# COPY --from=nodejs-frontend /frontend/bundles ./bundles/
# RUN export SECRET_KEY=build_stage_key && \
#     export DATABASE_URL=sqlite:///db.sqlite3 && \
#     python manage.py collectstatic --noinput

CMD ["gunicorn", "-b", "0.0.0.0:8000", "star_burger.wsgi:application"]