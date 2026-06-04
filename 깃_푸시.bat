@echo off
chcp 65001 > nul

echo 🔄 자동 업로드를 시작합니다...

:: 1. 변경 사항을 스테이징하고 커밋합니다.
git add .
git commit -m "by auto uploader"

:: 2. 원격 저장소의 최신 코드를 가져옵니다.
git pull --no-edit

:: 3. git pull 명령어의 성공 여부를 확인합니다.
if %errorlevel% equ 0 (
    :: 성공적으로 병합되었다면 푸시합니다.
    git push
    echo.
    echo ✅ 안전하게 업로드 및 병합되었습니다.
) else (
    :: 충돌(Conflict) 등의 에러가 발생했다면 병합을 취소합니다.
    echo.
    echo 🚨 [경고] 다른 사람의 코드와 충돌(Conflict)이 발생했습니다!
    echo 🚨 안전을 위해 자동 병합을 취소하고 코드를 원래 상태로 되돌립니다.
    git merge --abort
    echo 🚨 에디터를 열어 충돌된 파일을 직접 확인하고 수동으로 푸시해주세요.
)

:: 4. 창이 바로 닫히지 않고 결과를 확인할 수 있도록 멈춰 둡니다.
echo.
pause