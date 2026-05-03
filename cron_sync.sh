#!/bin/bash

# 프로젝트 디렉토리로 이동
PROJECT_DIR="/home/ubuntu/AI/Pbid"
cd $PROJECT_DIR

# 로그 파일 경로
LOG_FILE="$PROJECT_DIR/data/cron_sync.log"

echo "==========================================" >> $LOG_FILE
echo "시작 시간: $(date +'%Y-%m-%d %H:%M:%S')" >> $LOG_FILE

# 1. 데이터 수집 (collector.py)
echo "[1/3] 데이터 수집 중..." >> $LOG_FILE
$PROJECT_DIR/venv/bin/python3 backend/collector.py >> $LOG_FILE 2>&1

# 2. AI 분석 (ai_analyzer.py)
echo "[2/3] AI 분석 및 스코어링 중..." >> $LOG_FILE
$PROJECT_DIR/venv/bin/python3 backend/ai_analyzer.py >> $LOG_FILE 2>&1

# 3. 데이터 익스포트 (export_data.py)
echo "[3/3] frontend 데이터 익스포트 중..." >> $LOG_FILE
$PROJECT_DIR/venv/bin/python3 backend/export_data.py >> $LOG_FILE 2>&1

# 4. 배포 (Git Push를 통한 Vercel 트리거)
echo "[4/4] Git Push 및 배포 트리거 중..." >> $LOG_FILE
git add . >> $LOG_FILE 2>&1
git commit -m "chore: 로컬 크론 자동 수집 [$(date +'%Y-%m-%d %H:%M:%S')]" >> $LOG_FILE 2>&1 || echo "No changes to commit" >> $LOG_FILE
git push origin main >> $LOG_FILE 2>&1

echo "종료 시간: $(date +'%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "==========================================" >> $LOG_FILE
