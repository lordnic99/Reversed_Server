#!/usr/bin/env bash

set_secret_key() {
   if [ -f .env ]; then
       if grep -q '^SECRET_KEY=' .env; then
           echo "-> SECRET_KEY already exists in the .env file. Not generating a new key."
       fi
   else
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo "SECRET_KEY=$SECRET_KEY" > .env
        echo "-> New SECRET_KEY has been set in the .env file."
   fi
}

set_secret_key

export $(cat .env)

./run.py