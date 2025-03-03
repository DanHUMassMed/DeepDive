#!/bin/bash
if [ -n "$1" ]; then
    export LOG_LEVEL=$1
fi
if [ "$2" == "CLEAR_LOGS" ]; then
    rm backend.log 
    rm backend_testing.log
fi
if [ "$3" == "ACTIVATE_DEBUG" ]; then
    export ACTIVATE_DEBUG="TRUE"
fi
clear
export DEEP_DIVE_WORKSPACE="/Users/dan/Code/LLM/DeepDive/workspace/deep-dive"
uvicorn app.main:app --reload
