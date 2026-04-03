FPV Lens Corrector Pro 🎥
FPV Lens Corrector Pro는 광각 렌즈로 촬영된 FPV 드론 영상의 왜곡(Fish-eye)을 실시간으로 확인하며 교정할 수 있는 파이썬 기반 GUI 툴입니다. 복잡한 명령어나 유료 소프트웨어 없이 슬라이더 조절만으로 깔끔한 직선 영상을 얻을 수 있습니다.

✨ 주요 기능
실시간 미리보기: 왜곡 보정 수치(k1, k2)를 실시간으로 확인하며 조절 가능

정밀 구간 설정: 타임라인 슬라이더 및 직접 시간 입력(HH:MM:SS) 지원

이중 보정 엔진: 중앙부(k1)와 외곽부(k2)를 개별적으로 제어하여 정밀한 교정 지원

고화질 인코딩: FFmpeg 엔진을 활용한 고화질(H.264) 영상 추출

🚀 시작하기
1. 필수 요구 사항
이 프로그램을 실행하려면 시스템에 Python과 FFmpeg이 설치되어 있어야 합니다.

FFmpeg 설치 가이드 (환경 변수 등록 권장)

2. 패키지 설치
저장소를 클론한 후 필요한 라이브러리를 설치합니다.

Bash
git clone https://github.com/사용자이름/프로젝트저장소이름.git
cd 프로젝트저장소이름
pip install customtkinter opencv-python pillow numpy
3. 실행 방법
파이썬을 통해 프로그램을 실행합니다.

Bash
python fpv_fixer_pro.py
🛠 사용 방법
파일 찾기 버튼을 눌러 보정할 영상을 불러옵니다.

하단 슬라이더나 좌측 입력창을 통해 보정 구간을 설정합니다.

**k1(중앙부)**과 k2(외곽부) 슬라이더를 조절하여 왜곡을 폅니다.

전체 영상 교정 시작 버튼을 누르면 원본 폴더에 보정된 영상이 저장됩니다.

📦 배포 버전 만들기 (선택 사항)
파이썬 없이 실행 가능한 .exe 파일을 만들려면 다음 명령어를 사용하세요.

Bash
pyinstaller --noconsole --onefile --collect-all customtkinter --name "FPV_Fixer" fpv_fixer_pro.py
📝 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

💡 작성 팁
https://github.com/사용자이름/프로젝트저장소이름.git 부분만 실제 본인의 Git 주소로 수정해 주세요.

만약 실제 작동 스크린샷이 있다면 README.md 중간에 사진을 한 장 첨부하면 유저들이 훨씬 이해하기 좋습니다. (![Screenshot](./screenshot.png))
