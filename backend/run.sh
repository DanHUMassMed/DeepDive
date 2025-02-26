#!/bin/bash
if [ -n "$1" ]; then
    export LOG_LEVEL=$1
fi
if [ "$2" == "CLEAR_LOGS" ]; then
    rm backend.log 
    rm backend_testing.log
fi
clear
uvicorn app.main:app --reload
