#!/usr/bin/env bash
# 샤인영어 리포트 발행 스크립트
#   ./publish.sh "커밋 메시지"
# 빌드 → 커밋 → main 과 gh-pages(서비스 브랜치) 양쪽에 push
set -euo pipefail
cd "$(dirname "$0")"

MSG="${1:-리포트 업데이트}"

python3 build.py

git add -A
if git diff --cached --quiet; then
  echo "변경된 내용이 없습니다."
  exit 0
fi

git commit -m "$MSG"
git push origin main
git push origin main:gh-pages

echo "발행 완료 → https://loveinny7.github.io/shine-report/"
