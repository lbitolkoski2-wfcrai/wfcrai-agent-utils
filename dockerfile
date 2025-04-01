FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
RUN mkdir /src /dist
WORKDIR /src
COPY . /src
RUN uv build
RUN cp dist/*.whl /dist/

# Clean up the source directory after the build
RUN rm -rf /src
# Set an environment variable pointing to the wheel file in the /whl directory
WORKDIR /
ENV AGENT_UTILS_PACKAGE=/dist/wfcrai_agent_utils-0.1.0-py3-none-any.whl
