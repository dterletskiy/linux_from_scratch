ARG ARG_OS_NAME=ubuntu
ARG ARG_OS_VERSION=20.04

FROM ${ARG_OS_NAME}:${ARG_OS_VERSION}

ARG ARG_MESSAGE_HEADER="----- "

# Fix for tzdata for docker image build
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

ARG ARG_PACKAGES=" \
   nano vi whois \
"

# Install necessary for build packages
RUN for PACKAGE in ${ARG_PACKAGES}; do \
      echo ${ARG_MESSAGE_HEADER} "Installing package: ${PACKAGE}" && \
      apt update && apt install -y ${PACKAGE} || true; \
   done

# Cleaning
RUN apt autoremove -y && apt clean all


# Define user credentials and data
ARG ARG_USER_NAME=guest
ARG ARG_USER_PASSWORD=
ARG ARG_USER_HASHED_PASSWORD=
ARG ARG_USER_PASSWORD_SALT="guest"
ARG ARG_USER_UID=1000
ARG ARG_USER_GID=1000
ARG ARG_USER_WORKDIR="workspace"

# Creating the user
RUN if [ -z ${ARG_USER_PASSWORD+x} ] || [ -z ${ARG_USER_PASSWORD} ]; then \
      echo ${ARG_MESSAGE_HEADER} "User password is unset or empty"; \
      echo ${ARG_MESSAGE_HEADER} "User password will be used as user name"; \
      ARG_USER_PASSWORD=${ARG_USER_NAME}; \
   else \
      echo ${ARG_MESSAGE_HEADER} "User password is set to '${ARG_USER_PASSWORD}'"; \
   fi; \
   echo ${ARG_MESSAGE_HEADER} "User password: '${ARG_USER_PASSWORD}'"; \
   \
   if [ -z ${ARG_USER_HASHED_PASSWORD+x} ] || [ -z ${ARG_USER_HASHED_PASSWORD} ]; then \
      echo ${ARG_MESSAGE_HEADER} "User hashed password is unset or empty"; \
      echo ${ARG_MESSAGE_HEADER} "Generating user hashed password from user password"; \
      ARG_USER_HASHED_PASSWORD=$(perl -e "print crypt(${ARG_USER_PASSWORD},${ARG_USER_PASSWORD_SALT})"); \
      ARG_USER_HASHED_PASSWORD=$(mkpasswd -m sha-512 -S ${ARG_USER_PASSWORD_SALT} ${ARG_USER_PASSWORD}); \
   else \
      echo ${ARG_MESSAGE_HEADER} "User hashed password is set to '${ARG_USER_HASHED_PASSWORD}'"; \
   fi; \
   echo ${ARG_MESSAGE_HEADER} "User hashed password: '${ARG_USER_HASHED_PASSWORD}'"; \
   \
   groupadd --gid ${ARG_USER_GID} ${ARG_USER_NAME} && \
   useradd \
      --uid ${ARG_USER_UID} \
      --gid ${ARG_USER_GID} \
      --create-home \
      --shell /bin/bash \
      --groups adm,sudo \
      --password ${ARG_USER_HASHED_PASSWORD} \
      ${ARG_USER_NAME}

# Switch the user from root to ${ARG_USER_NAME}
USER ${ARG_USER_NAME}
ENV USER_NAME=${ARG_USER_NAME}

# Create workdir for docker and define it as WORKDIR
RUN mkdir -p /home/${ARG_USER_NAME}/${ARG_USER_WORKDIR} && chown ${ARG_USER_NAME}:${ARG_USER_NAME} /home/${ARG_USER_NAME}/${ARG_USER_WORKDIR}
ENV BUILD_DIR /home/${ARG_USER_NAME}/${ARG_USER_WORKDIR}
WORKDIR ${BUILD_DIR}
ENV PATH ~/.local/bin:${PATH}
