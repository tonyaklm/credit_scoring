FROM postgres
RUN mkdir -p /docker-entrypoint-initdb.d
RUN touch /docker-entrypoint-initdb.d/create-multiple-db-with-users.sh
RUN chown -R 777 /docker-entrypoint-initdb.d/
RUN chown -R 777 /docker-entrypoint-initdb.d/create-multiple-db-with-users.sh
