FROM python:3-slim AS builder
LABEL maintainer="IETF Tools Team <tools-discuss@ietf.org>"

WORKDIR /app

# Install build tools
RUN pip install build

# Copy everything required to build xml2rfc
COPY pyproject.toml README.md LICENSE Makefile configtest.py .

# Build xml2rfc package
COPY xml2rfc ./xml2rfc
RUN python -m build -o /dist

# Copy package to runtime step
FROM python:3-slim AS runtime
COPY --from=builder /dist ./dist

# Install xml2rfc
RUN pip install --no-cache ./dist/*.whl

ENTRYPOINT ["xml2rfc"]
