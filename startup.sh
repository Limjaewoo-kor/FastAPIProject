#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 애플리케이션 실행
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

chmod +x startup.sh
