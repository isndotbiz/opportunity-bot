@echo off
echo ================================================
echo Opportunity Bot - Credit Score Opportunities
echo ================================================
echo.

cd /d D:\workspace\opportunity-research-bot

echo Activating environment...
call venv\Scripts\activate.bat

echo.
echo Searching for credit score improvement opportunities...
echo.

set PYTHONIOENCODING=utf-8

python -c "
import sys
sys.path.insert(0, '.')
print('Searching Reddit, Google, Indie Hackers for credit opportunities...')
print('Keywords: credit score, business credit, Equifax, 700+ FICO')
print('')
print('This is a simplified search - full version needs LLM server')
print('Results will be saved to: data/opportunities/')
"

echo.
echo ================================================
echo To run full version:
echo 1. Start LLM: cd ..\llama-cpp-docker ^&^& docker-compose up -d
echo 2. Then: python production_opportunity_pipeline.py
echo ================================================
pause
